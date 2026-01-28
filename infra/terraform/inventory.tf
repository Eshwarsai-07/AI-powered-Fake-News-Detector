resource "local_file" "ansible_inventory" {
  depends_on = [aws_instance.server]
  
  content = <<-EOT
    [webservers]
    ${aws_instance.server.public_ip} ansible_user=ubuntu ansible_ssh_private_key_file="${abspath("${path.module}/ai-fake-news-detector-key.pem")}" ansible_ssh_common_args='-o StrictHostKeyChecking=no' repo_url=${var.repo_url}
  EOT
  
  filename = "${path.module}/../ansible/inventory.ini"
  file_permission = "0644"
}
