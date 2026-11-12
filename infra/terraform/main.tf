locals {
  tags = {
    projeto    = var.project_name
    disciplina = "devops"
    gs         = "2026.2"
  }
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${var.project_name}-prod"
  location = var.location
  tags     = local.tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "log-${var.project_name}-prod"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  daily_quota_gb      = 0.5 # limita o custo de ingestão de logs
  tags                = local.tags
}

resource "azurerm_container_app_environment" "main" {
  name                       = "cae-${var.project_name}-prod"
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  tags                       = local.tags
}

# Sem VM, NSG ou IP público de máquina: o único ponto de entrada é o ingress
# HTTPS (443) gerenciado pela Azure. Não existe SSH nem RDP para abrir.
resource "azurerm_container_app" "main" {
  name                         = "ca-${var.project_name}-prod"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"
  tags                         = local.tags

  template {
    min_replicas = 1
    max_replicas = 1

    container {
      name   = "app"
      image  = var.container_image
      cpu    = 0.25
      memory = "0.5Gi"

      env {
        name  = "ENABLE_ERROR_SIMULATION"
        value = tostring(var.enable_error_simulation)
      }

      liveness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/health"
      }

      readiness_probe {
        transport = "HTTP"
        port      = 8000
        path      = "/health"
      }
    }
  }

  ingress {
    external_enabled           = true
    target_port                = 8000
    allow_insecure_connections = false

    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  lifecycle {
    # Quem troca a imagem é o pipeline (az containerapp update); o Terraform não reverte.
    ignore_changes = [template[0].container[0].image]
  }
}
