# Vault Setup

Run the server:
```
vault server -dev -dev-root-token-id=root &
```

_Please note that the database must already be setup before proceeding._

## Configure Vault and Database Engine:

Now that the database is configured we can begin work on Vault.

```
export VAULT_ADDR=http://localhost:8200

# Authenticate
vault login root

# Enable Auditing
vault audit enable file file_path=/tmp/vault_audit.log

# Enable our secret engine
vault secrets enable -path=lob_a/workshop/database database

# Configure our secret engine
vault write lob_a/workshop/database/config/ws-mysql-database \
    plugin_name=mysql-database-plugin \
    connection_url="{{username}}:{{password}}@tcp(127.0.0.1:3306)/" \
    allowed_roles="workshop-app" \
    username="root" \
    password="root"

# Create our role
vault write lob_a/workshop/database/roles/workshop-app-long \
    db_name=ws-mysql-database \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';GRANT ALL ON *.* TO '{{name}}'@'%';" \
    default_ttl="1h" \
    max_ttl="24h"

vault write lob_a/workshop/database/roles/workshop-app \
    db_name=ws-mysql-database \
    creation_statements="CREATE USER '{{name}}'@'%' IDENTIFIED BY '{{password}}';GRANT ALL ON *.* TO '{{name}}'@'%';" \
    default_ttl="5m" \
    max_ttl="1h"
```

Vault is now configured.  

### Test Example

We can now test that the credentials generated are valid like so:

```
$ vault read lob_a/workshop/database/creds/workshop-app
Key                Value
---                -----
lease_id           database/creds/workshop-app/qthWaQW9brX0dO6de0UNCvlk
lease_duration     5m
lease_renewable    true
password           A1a-1nIXGSYdjo3IME3u
username           v-token-workshop-a-IhjjXuaXJ3ILR

$ docker exec -it workshop-mysql mysql -uv-token-workshop-a-IhjjXuaXJ3ILR -pA1a-1nIXGSYdjo3IME3u
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 57
Server version: 5.7.22 MySQL Community Server (GPL)

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;

```

## Configure Encryption as a Service (Transit):

We need to enable the transit engine, and create a key for our application to use:

```
# Enable the secret engine
vault secrets enable -path=lob_a/workshop/transit transit

# Create our customer key
vault write -f lob_a/workshop/transit/keys/customer-key

# Create our archive key to demonstrate multiple keys
vault write -f lob_a/workshop/transit/keys/archive-key


```