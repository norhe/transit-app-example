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

## Client

The backend client uses [hvac](https://github.com/hvac/hvac) to interact wiith Vault.  Install it like so:
```
pip3 install hvac
```

### Explanation

Imagine we have a firm with customer data.  We want to encrypt that data in the database such that we protect it from both external and internal attackers.  Many databases support encrypting the raw files using things like TDE.  However, this only protects us from someone stealing the bits on disk.  If someone like a DBA, app developer, HVAC technician, etc, can read from the database than file level encryption does not help.

Using Vault's Encryption as a Service (transit secret engine), we can protect the data from both vectors.  If the raw data is stolen it will be of no value, and internal threats with read access will not be able to surreptitiously access and steal the data.

This is a simple example, but the principles herein could be broadly applied to databases, files on disk, data in object storage, etc.  It is a flexible tool for transparently encrypting both arbitrary chunks of data using the API, and larger files using the datakey pattern.

In this example we have the following table:
```
+------------------------+--------------+------+-----+---------+----------------+
| Field                  | Type         | Null | Key | Default | Extra          |
+------------------------+--------------+------+-----+---------+----------------+
| cust_no                | int(11)      | NO   | PRI | NULL    | auto_increment |
| birth_date             | varchar(255) | NO   |     | NULL    |                |
| first_name             | varchar(32)  | NO   |     | NULL    |                |
| last_name              | varchar(32)  | NO   |     | NULL    |                |
| create_date            | varchar(255) | NO   |     | NULL    |                |
| social_security_number | varchar(16)  | NO   |     | NULL    |                |
| address                | varchar(255) | NO   |     | NULL    |                |
| salary                 | varchar(16)  | NO   |     | NULL    |                |
+------------------------+--------------+------+-----+---------+----------------+
```

We want our applications to be able to use this data as necessary, but for the data in the database to be protected as discussed previously.  In our example, we want to encrypt the birth_date, social_security_number, address, and salary fields.  

N.B. The output of an encrypted record may consist of more characters than the input string.  For instance, if one encrypts something like a social security number (123-45-6789) the output would look something like:
```
vault:v1:7gJQbolfH6KgyxJ4VnkGbO7YTig5waMq96IBGKJRH37T
```

Database schemas may need to be adjusted to account for the longer values.  For instance, if you configured your database with a value of varchar(11) then the resultant encrypted value would not fit in that column.