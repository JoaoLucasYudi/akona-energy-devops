variable "subscription_id" {
  description = "ID da assinatura Azure onde os recursos serão criados."
  type        = string
}

variable "location" {
  description = "Região da Azure (confirmada no teste de viabilidade H2b)."
  type        = string
  default     = "eastus2"
}

variable "project_name" {
  description = "Nome curto do projeto, usado nos nomes dos recursos. Só minúsculas, números e hífen."
  type        = string
  default     = "akona-energy"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,18}[a-z0-9]$", var.project_name))
    error_message = "project_name deve ter de 3 a 20 caracteres: minúsculas, números e hífen, começando com letra e sem terminar em hífen."
  }
}

variable "container_image" {
  description = "Imagem inicial do container. Depois do primeiro apply, quem troca a imagem é o pipeline."
  type        = string
  default     = "ghcr.io/joaolucasyudi/akona-energy-devops:latest"

  validation {
    condition     = can(regex("^[a-z0-9][a-z0-9._/:@-]*$", var.container_image))
    error_message = "container_image não pode ter maiúsculas (referências de imagem com maiúsculas falham com \"invalid reference format\")."
  }
}

variable "enable_error_simulation" {
  description = "Liga a rota /simular-erro (ENABLE_ERROR_SIMULATION). Desligada por padrão; só ligar para a demonstração do alerta."
  type        = bool
  default     = false
}
