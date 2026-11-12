output "resource_group_name" {
  description = "Nome do resource group."
  value       = azurerm_resource_group.main.name
}

output "container_app_name" {
  description = "Nome do Container App (usado pelo pipeline de deploy)."
  value       = azurerm_container_app.main.name
}

output "app_fqdn" {
  description = "FQDN público do app (usado no job mvp-prod do Prometheus)."
  value       = azurerm_container_app.main.ingress[0].fqdn
}

output "app_url" {
  description = "URL pública do app, só HTTPS."
  value       = "https://${azurerm_container_app.main.ingress[0].fqdn}"
}
