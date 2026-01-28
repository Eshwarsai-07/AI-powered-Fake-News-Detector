output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.server.public_ip
}

output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.server.id
}

output "instance_availability_zone" {
  description = "Availability zone where instance is deployed"
  value       = aws_instance.server.availability_zone
}

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.web_sg.id
}

output "ssh_command" {
  description = "Command to SSH into the instance"
  value       = "ssh -i ai-fake-news-detector-key.pem ubuntu@${aws_instance.server.public_ip}"
}

output "ssh_key_path" {
  description = "Path to the SSH private key"
  value       = local_file.pem_file.filename
}

output "connection_info" {
  description = "Quick reference for connecting to the instance"
  value = <<-EOT
    
    ╔════════════════════════════════════════════════════════════╗
    ║           EC2 Instance Connection Information              ║
    ╚════════════════════════════════════════════════════════════╝
    
    Public IP:    ${aws_instance.server.public_ip}
    Instance ID:  ${aws_instance.server.id}
    Region:       ${var.aws_region}
    AZ:           ${aws_instance.server.availability_zone}
    
    SSH Command:
    chmod 400 ai-fake-news-detector-key.pem
    ssh -i ai-fake-news-detector-key.pem ubuntu@${aws_instance.server.public_ip}
    
    Security Group Ports Open:
    - SSH:   22
    - HTTP:  80
    - HTTPS: 443
    
    ML Model Storage:
    - S3 Bucket:  ${aws_s3_bucket.model_bucket.id}
    
  EOT
}

output "model_bucket_name" {
  value       = aws_s3_bucket.model_bucket.id
  description = "The name of the S3 bucket created for ML models"
}
