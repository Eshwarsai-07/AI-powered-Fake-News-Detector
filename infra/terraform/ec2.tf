# 1. Generate a secure private key
resource "tls_private_key" "pk" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# 2. Create AWS Key Pair
resource "aws_key_pair" "kp" {
  key_name   = "ai-fake-news-detector-key"
  public_key = tls_private_key.pk.public_key_openssh
}

# 3. Save Private Key locally
resource "local_file" "pem_file" {
  filename        = "${path.module}/ai-fake-news-detector-key.pem"
  content         = tls_private_key.pk.private_key_pem
  file_permission = "0400"
}

# 4. Find latest Ubuntu 22.04 AMI
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# 5. Create the EC2 Instance
resource "aws_instance" "server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.medium" # Upgraded for BERT + K8s + Monitoring stack memory requirements

  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.web_sg.id]
  associate_public_ip_address = true
  key_name                    = aws_key_pair.kp.key_name

  # Root block device configuration
  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    delete_on_termination = true
    encrypted             = false
  }

  # User data to ensure instance initializes properly
  user_data = <<-EOF
              #!/bin/bash
              # Update system
              apt-get update -y
              
              # Signal successful initialization
              echo "Instance initialized successfully" > /var/log/user-data.log
              EOF

  # Metadata options (IMDSv2)
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "optional"
    http_put_response_hop_limit = 1
    instance_metadata_tags      = "enabled"
  }

  # Explicit timeouts to prevent timeout errors
  timeouts {
    create = "15m"
    update = "15m"
    delete = "15m"
  }

  tags = {
    Name = "ai-fake-news-detector-server"
  }

  # Ensure instance is fully ready before marking as created
  depends_on = [
    aws_internet_gateway.gw,
    aws_route_table_association.public
  ]
}
