variable "hcloud_token" {
  description = "API-токен Hetzner Cloud (создаётся в панели Hetzner)"
  type        = string
  sensitive   = true
}

variable "server_type" {
  description = "Тип сервера (размер CPU/RAM)"
  type        = string
  default     = "cx22"  # самый дешёвый вариант, хватает для пет-проекта
}

variable "location" {
  description = "Регион дата-центра"
  type        = string
  default     = "nbg1"  # Нюрнберг, Германия
}

variable "ssh_public_key_path" {
  description = "Путь к публичному SSH-ключу на твоём компьютере"
  type        = string
  default     = "~/.ssh/notes_app_deploy.pub"
}
