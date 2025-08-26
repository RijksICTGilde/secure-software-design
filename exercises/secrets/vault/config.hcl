disable_mlock = true
ui = true

listener "tcp" {
  tls_disable = 1
  address = "[::]:8200"
}

storage "postgresql" {
  connection_url =  "postgres://vault:vault@postgres:5432/vault?sslmode=allow"
  ha_enabled = "true"
}

default_lease_ttl = "8h"
max_lease_ttl = "22h"
log_level  = "debug"

api_addr = "http://0.0.0.0:8200"