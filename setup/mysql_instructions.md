# Database Setup

We need a database to interact with.  We're using mysql.

```
# Pull the latest mysql container image to match Azure version
docker pull mysql/mysql-server:5.7.21

# Create a directory for our data (change the following
# line if running on Windows)
mkdir ~/workshop-data

# Run the container.  The following command creates a
# database named 'my_app', specifies the root user
# password as 'root', and adds a user named vault
docker run --name workshop-mysql \
  -p 3306:3306 \
  -v ~/workshop-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_ROOT_HOST=% \
  -e MYSQL_DATABASE=my_app \
  -e MYSQL_USER=vault \
  -e MYSQL_PASSWORD=vaultpw \
  -d mysql/mysql-server:5.7.21
```

To interact with the database:
```
docker exec -it workshop-mysql mysql -uroot -proot
```


Prod:
Use TF to create Azure service
https://azure.microsoft.com/en-us/services/mysql/
Then use TF to register service pointing to that endpoint?