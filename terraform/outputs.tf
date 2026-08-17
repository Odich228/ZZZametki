output "server_ip" {
  description = "Публичный IP-адрес созданного сервера"
  value       = hcloud_server.notes_app_server.ipv4_address
}
