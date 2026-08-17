terraform {
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.45"
    }
  }
}

provider "hcloud" {
  token = var.hcloud_token
}

resource "hcloud_server" "notes_app_server" {
  name        = "notes-app-server"
  server_type = var.server_type
  image       = "ubuntu-24.04"
  location    = var.location

  ssh_keys = [hcloud_ssh_key.deploy_key.id]
}

resource "hcloud_ssh_key" "deploy_key" {
  name       = "notes-app-deploy-key"
  public_key = file(var.ssh_public_key_path)
}
