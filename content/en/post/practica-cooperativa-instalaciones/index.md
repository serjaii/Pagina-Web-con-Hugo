---
title: "Cooperative Practice: Full Deployment of Database Engines"
author: "Sergio Jiménez, José María Oteo, David Dorante"
date: "2025-12-09"
categories: ["Database", "Oracle", "MariaDB", "PostgreSQL", "MongoDB", "DevOps"]
tags: ["oracle", "mysql", "postgresql", "mongodb", "neo4j", "redis", "cassandra", "memcached", "couchdb"]
image: "cover.png"
---

# Cooperative Guide to Database Installation and Configuration

This document collects the work done to set up various database management systems on **Debian 13**. The steps for each differ.

This practice has been carried out by students Sergio Jiménez, José María Oteo, and David Dorante.

## Oracle 21c Installation on Debian 13

### 1. Pre-configuration and dependencies

- First, we will update system packages to avoid possible version conflicts during Oracle dependency installation.

```bash
serjaii@db:~$ sudo apt update && sudo apt upgrade -y
```

- We install Oracle dependencies on our system.

```bash
serjaii@db:~$ sudo apt policy libaio1t64 libaio-dev unixodbc rlwrap alien net-tools unzip bc ksh
```

- Usage of each dependency:

    - **libaio1t64**: Asynchronous I/O dependency, mandatory for Oracle.
    - **libaio-dev**: contains header files and symbolic links for developers to compile programs using libaio.
    - **unixodbc**: ODBC libraries required by Oracle.
    - **rlwrap**: improves SQL*Plus terminal experience.
    - **bc**: calculations used by Oracle scripts.
    - **ksh**: KornShell, required by some installation scripts.
    - **alien**: converts .rpm package to .deb.
    - **net-tools**: includes netstat, used by Oracle.
    - **unzip**: for SQL*Plus later.

- We configure a static IP to facilitate future remote connections.

- In hosts, we add an entry pointing to our private address.

- Oracle and SQL*Plus need the `libaio.so.1` library, which is not found in the system since the package and library names changed in Debian 13. To avoid errors when entering Oracle, we will create a symbolic link from `libaio1t64` named `libaio.so.1` so Oracle recognizes the library.

Check:
```bash
serjaii@db:~$ ls -l /usr/lib/x86_64-linux-gnu/libaio.so.1
lrwxrwxrwx 1 root root 40 oct 8 20:22 /usr/lib/x86_64-linuxgnu/libaio.so.1 -> /usr/lib/x86_64-linux-gnu/libaio.so.1t64
```

### 2. Server Installation

- Possible Error: The alien process might require more than 2GB of space in `/tmp`. If not available, we must increase that size.

- We use the “alien” command to convert the .rpm package we just downloaded from Oracle 21c to .deb format, which Debian executes.

- After modifying the file extension to .deb, we manually install said Oracle package.

```bash
serjaii@db:~$ sudo dpkg -i oracle-database-ee-21c_1.02_amd64.deb
```

- We execute the configuration script created by Oracle.

```bash
serjaii@db:~$ sudo /etc/init.d/oracledb_ORCLCDB-21c configure
```

- To avoid being asked for a username and password when entering Oracle, we will add our user, in my case `sergio`, to the `dba` group.

```bash
serjaii@db:~$ sudo usermod -aG dba $USER
```

- Once Oracle is installed, we must add the following environment variables to `.bashrc` on the machine where we installed the server.

```bash
serjaii@db:~$ grep '^export' ~/.bashrc 
export ORACLE_HOME=/opt/oracle/product/21c/dbhome_1 
export ORACLE_SID=ORCLCDB 
export ORACLE_BASE=/opt/oracle 
export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH 
export PATH=$ORACLE_HOME/bin:$PATH 
export NLS_LANG=SPANISH_SPAIN.AL32UTF8
serjaii@db:~$ alias alias sqlplus='rlwrap sqlplus'
```

- Once variables are added, we reload bashrc to apply them.

```bash
serjaii@db:~$ source ~/.bashrc
```

- We verify we can access the database as administrator.

```bash
serjaii@db:~$ sqlplus / as sysdba
```

### 3. Create User and Grant Permissions in Oracle 21c

- Optimization to allow user creation.

```bash
SQL> STARTUP;
SQL> ALTER SESSION SET "_ORACLE_SCRIPT"=true;
```

- We create a user to test connections later and grant permissions.

```bash
SQL> CREATE USER sergio IDENTIFIED BY sergio;
SQL> GRANT ALL PRIVILEGES TO sergio;
```

- To start the service automatically on reboot, we modify crontab.

```bash
serjaii@db:~$ sudo crontab -e
```

- Access the database with the created user.

### 4. Oracle Server Configuration for Remote Connection

- Oracle listens on localhost by default. We modify `listener.ora` to listen to all requests.

```bash
serjaii@db:~$ sudo nano /opt/oracle/homes/OraDBHome21cEE/network/admin/listener.ora
```

- We also modify `tnsnames.ora`, as it indicates how the client connects. We modify the “HOST” value of “ORCLCDB”.

```bash
serjaii@db:~$ sudo nano /opt/oracle/homes/OraDBHome21cEE/network/admin/tnsnames.ora
```

- Reboot to apply changes.

```bash
serjaii@db:~$ sudo reboot
```

### 5. Installation and Configuration of Oracle Client (SQL*Plus)

- Update system packages.

```bash
serjaii@db:~$ sudo apt update
```

- Install dependencies required by SQL*Plus.

```bash
serjaii@db:~$ sudo apt install libaio1t64 libaio-dev rlwrap wget p7zip-full -y
```

- Create symbolic link again for Debian to recognize the package.

```bash
serjaii@db:~$ sudo ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
```

- Create a working folder.

```bash
serjaii@db:~$ mkdir oracle
serjaii@db:~$ cd oracle
```

- Download packages for Basic and SQL*Plus.

```bash
serjaii@db:~$ wget https://download.oracle.com/otn_software/linux/instantclient/2119000/instantclient-basic-linux.x64-21.19.0.0.0dbru.zip
serjaii@db:~$ wget https://download.oracle.com/otn_software/linux/instantclient/2119000/instantclient-sqlplus-linux.x64-21.19.0.0.0dbru.zip
```

- Unzip packages.

```bash
serjaii@db:~$ 7z x instantclient-basic-linux.x64-21.19.0.0.0dbru.zip
serjaii@db:~$ 7z x instantclient-sqlplus-linux.x64-21.19.0.0.0dbru.zip
```

- Add environment variables to `.bashrc` and source it.

```bash
serjaii@db:~$ sudo nano ~/.bashrc
serjaii@db:~$ source ~/.bashrc
```

- Connect to the server.

```bash
serjaii@db:~$ sqlplus sergio/sergio@//192.168.122.79:1521/ORCLCDB
```

### 6. Database Creation with Tables and Data in Oracle

- Access as administrator.

```bash
serjaii@db:~$ sqlplus / as sysdba 
SQL> ALTER SESSION SET "_ORACLE_SCRIPT"=true;
```

- Create database and user.

```bash
SQL> CREATE USER hotel IDENTIFIED BY hotel123;
SQL> GRANT ALL PRIVILEGES TO hotel;
```

- Connect with new user.

```bash
serjaii@db:~$ sqlplus hotel/hotel123@//192.168.122.79:1521/ORCLCDB
```

- Create tables (clients, rooms, reservations, payments) and insert data (omitted for brevity, same SQL structure as original).

## PostgreSQL Server Installation on Debian 13

### 1. Pre-configuration and dependencies

- Update packages.

```bash
serjaii@db:~$ sudo apt update
```

### 2. Server Installation

- Install postgresql package.

```bash
serjaii@db:~$ sudo apt install postgresql -y
```

- Check status and enable service.

```bash
serjaii@db:~$ systemctl status postgresql
serjaii@db:~$ sudo systemctl enable postgresql
```

- Check access.

```bash
serjaii@db:~$ sudo -u postgres psql
```

### 3. Remote Connection Configuration

- Modify `postgresql.conf` to set `listen_addresses = '*'`.

```bash
serjaii@db:~$ sudo nano /etc/postgresql/17/main/postgresql.conf
```

- Modify `pg_hba.conf` to allow remote connections.

```bash
serjaii@db:~$ sudo nano /etc/postgresql/17/main/pg_hba.conf
```

- Restart service.

```bash
serjaii@db:~$ sudo systemctl restart postgresql
```

### 4. Create Database, User and Grant Permissions

- Access as privileged user.

```bash
serjaii@db:~$ sudo -u postgres psql
```

- Create database, user and grant privileges.

```bash
postgres=# CREATE DATABASE prueba_db;
postgres=# CREATE ROLE sergio WITH LOGIN PASSWORD 'sergio';
postgres=# GRANT ALL PRIVILEGES ON DATABASE prueba_db TO sergio;
postgres=# GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sergio;
```

- Test local connection.

```bash
serjaii@db:~$ psql -h localhost -p 5432 -U sergio -d prueba_db
```

### 5. Client Installation

- Install postgresql-client.

```bash
serjaii@db:~$ sudo apt install postgresql-client -y
```

- Test remote connection.

```bash
serjaii@db:~$ psql -h 192.168.122.79 -p 5432 -U sergio -d prueba_db
```

### 6. Creation of Database with Data

- Create 'hotel' database and tables (same structure as Oracle).

## MySQL Server Installation on Debian 13

### 1. Server Installation

- Update system.

```bash
serjaii@db:~$ sudo apt update
```

- Install MariaDB.

```bash
serjaii@db:~$ sudo apt install mariadb-server -y
```

- Enable and check service.

```bash
serjaii@db:~$ sudo systemctl status mariadb
serjaii@db:~$ sudo systemctl enable mariadb
```

- Check access.

```bash
serjaii@db:~$ sudo mysql -u root -p
```

### 2. Remote Connection Configuration

- Modify `50-server.cnf` to change bind-address.

```bash
serjaii@db:~$ sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```

- Restart service.

```bash
serjaii@db:~$ sudo systemctl restart mariadb
```

### 3. Create User and Database

- Create user allowing remote access.

```sql
MariaDB [(none)]> CREATE USER 'sergio'@'%' IDENTIFIED BY 'sergio';
MariaDB [(none)]> GRANT ALL PRIVILEGES ON *.* TO 'sergio'@'%' WITH GRANT OPTION;
```

### 4. Client Installation

- Install mariadb-client.

```bash
serjaii@db:~$ sudo apt install mariadb-client -y
```

- Test connection.

```bash
serjaii@db:~$ mysql -h 192.168.122.79 -P 3306 -u sergio -p
```

### 5. Create Tables and Data

- Create 'hotel' database and populate tables.

## MongoDB Server Installation on Debian 13

### 1. Dependencies and Pre-configuration

- Install curl and gnupg.

```bash
serjaii@db:~$ sudo apt install curl gnupg -y
```

- Download and add MongoDB GPG key.

```bash
serjaii@db:~$ sudo curl -fsSL https://pgp.mongodb.com/server-8.0.asc | sudo gpg -dearmor -o /usr/share/keyrings/mongodbserver-8.0.gpg
```

- Add MongoDB repository.

```bash
serjaii@db:~$ sudo echo "deb [signed-by=/usr/share/keyrings/mongodbserver-8.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```

### 2. Server Installation

- Install MongoDB.

```bash
serjaii@db:~$ sudo apt update
serjaii@db:~$ sudo apt install mongodb-org -y
```

- Start and enable service.

```bash
serjaii@db:~$ sudo systemctl start mongod
serjaii@db:~$ sudo systemctl enable mongod
```

### 3. Remote Connection Configuration

- Modify `mongod.conf` bindIp to 0.0.0.0.

```bash
serjaii@db:~$ sudo nano /etc/mongod.conf
```

- Restart service.

### 4. Create Database and User

- Create database and user with roles.

```bash
use pruebadb
db.createUser({ user: "sergio", pwd: "sergio", roles: [{ role: "readWrite", db: "pruebadb" }] })
```

- Enable authentication in `mongod.conf` and restart.

### 5. Client Installation

- Add repository and install `mongodb-mongosh`.

```bash
serjaii@db:~$ sudo apt install -y mongodb-mongosh
```

- Test remote connection.

```bash
serjaii@db:~$ mongosh "mongodb://usuario:contraseña@IP_DEL_SERVIDOR:27017/pruebadb?authSource=pruebadb"
```

### 6. Create Collections and Data

- Insert data into 'clientes', 'habitaciones', 'servicios' collections.

## Neo4j Server Installation on Debian 13

### 1. Dependencies

- Install basic utilities.

```bash
serjaii@db:~$ sudo apt install -y wget curl gnupg lsb-release ca-certificates apt-transport-https 
```

- Install Java 21 (Temurin).

```bash
serjaii@db:~$ wget -qO https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/adoptium.gpg > /dev/null
serjaii@db:~$ echo "deb [signed-by=/etc/apt/trusted.gpg.d/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/adoptium.list
serjaii@db:~$ sudo apt update
serjaii@db:~$ sudo apt install -y temurin-21-jdk
```

- Add Neo4j key and repository.

```bash
serjaii@db:~$ wget -qO https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/neo4j.gpg > /dev/null
serjaii@db:~$ echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
```

### 2. Server Installation

- Install Neo4j.

```bash
serjaii@db:~$ sudo apt install neo4j -y
```

- Set initial password.

```bash
serjaii@db:~$ sudo neo4j-admin dbms set-initialpassword 'root1234'
```

- Start service.

```bash
serjaii@db:~$ sudo systemctl start neo4j
```

### 3. Remote Configuration

- Configure `neo4j.conf` to listen on all interfaces.

```bash
serjaii@db:~$ sudo nano /etc/neo4j/neo4j.conf
```

- Restart service.

### 4. Client Installation

- Install `cypher-shell`.

```bash
serjaii@db:~$ sudo apt install -y cypher-shell
```

- Connect.

```bash
serjaii@db:~$ cypher-shell bolt://IP_SERVIDOR:7687 -u neo4j -p 'root1234' -a
```

### 5. Data Insertion

- Create nodes and relationships (Clients, Rooms, Services, Payments, Reservations).

## Redis Server Installation on Debian 13

### 1. Dependencies

- Add Redis repository.

```bash
serjaii@db:~$ curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archivekeyring.gpg
serjaii@db:~$ echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list && sudo apt update
```

### 2. Server Installation

- Install Redis.

```bash
serjaii@db:~$ sudo apt install redis
```

- Enable and start service.

### 3. Remote Configuration

- Modify `redis.conf` to bind to all interfaces and set a password.

### 4. Client Installation

- Install `redis-tools`.

```bash
serjaii@db:~$ sudo apt install redis-tools
```

- Connect.

```bash
serjaii@db:~$ redis-cli -h bd -p 6379 -a clienteredis
```

### 5. Data Insertion

- Use `HSET` to insert data for Clients, Rooms, Services, Payments.

## Cassandra Server Installation on Debian 13

### 1. Dependencies

- Install Java 11 (Temurin) and Python build tools.

```bash
sudo apt install -y temurin-11-jdk python3-pip python3-dev
```

### 2. Server Installation

- Download Cassandra 4.1.5 tarball and extract to `/opt/cassandra`.
- Create cassandra user.
- Create systemd service file `cassandra.service`.
- Enable and start Cassandra.

### 3. Client Configuration (cqlsh)

- Install python driver and fix compatibility issues with Python 3.13 (patch `cluster.py` to use eventlet).
- Create `cqlsh` wrapper script.

### 4. Remote Configuration

- Modify `cassandra.yaml` to listen on the server IP instead of localhost.
- Restart service.

### 5. Usage

- Create Keyspaces and Tables (Authors, Books, Loans).
- Insert data using CQL.

## Web Application and SQL Injection

Details on connecting web applications to these databases and testing SQL Injection vulnerabilities on PostgreSQL/MySQL are included. Modifications to make the app vulnerable and fix it are described (using parameterized queries).

## Memcached Server Installation on Debian 13

### 1. Package Installation
- First, we update the repositories.
```bash
serjaii@db:~$ sudo apt update
```
- We install the memcached server along with the client library and tools.
```bash
serjaii@db:~$ sudo apt install memcached libmemcached-tools
```
- Check the service status.

- This occurs because in recent versions of Memcached, it does not support two `-l` directives in the same file; this causes exactly the `status=71` error. We edit the `/etc/memcached.conf` file and comment out the second line referring to `-l`.
```bash
serjaii@db:~$ sudo nano /etc/memcached.conf
```
- Restart and check the service status again.
```bash
serjaii@db:~$ sudo systemctl restart memcached && sudo systemctl status memcached
```

### 2. Memcached in a Web Server
First of all, we must know what Memcached is. Since it is not a database per se, we can understand it as a service that functions as a cache for the database when it connects to a web application. To test its functionality, I will implement it on a Web Server taking data from a MySQL database.

- As we are working in a scenario too small to notice a difference when information comes from memcached or from the database server itself, I have added a notice on the web server to recognize it.
```html
{% if cached %}
<div style="background:#ffc107;color:#212529;padding:6px 10px;border-radius:6px;font-weight:600;">
    Served from cache
</div>
{% endif %}
```

### 3. Implementation in Flask
Starting from the project, I will review the steps followed to implement memcached in a web server, although this process may differ depending on whether it is done with Flask or any other application.

First, we will start by adding `pymemcache==4.0.8` to our virtual environment in `requirements.txt`.

The rest of the changes will be made on the `app.py` file:
- Import library.
- Initiate the memcached client.

## Installation, basic use and explanation of CouchDB on Debian 13
Apache CouchDB is a document-oriented NoSQL database that stores JSON documents, exposes an HTTP/REST API and MapReduce views, and an efficient replication system. It is written in Erlang and uses append-only storage on B-trees, facilitating fault tolerance and concurrent reads. Fauxton is its integrated web interface for administration and testing.

### 1. Dependencies and CouchDB Server Installation.
The official CouchDB repository does not yet have specific packages for Debian 13, as it is a very recent version. Therefore, we will temporarily use Debian 12 packages for CouchDB installation until CouchDB publishes specific packages for Debian 13.

- We update system packages, ensuring APT packages and metadata are up to date to avoid conflicts.
```bash
serjaii@db:~$ sudo apt update && sudo apt upgrade -y
```
- We install necessary dependencies for CouchDB installation, to add HTTPS repositories and manage GPG keys.
```bash
serjaii@db:~$ sudo apt install -y curl gnupg ca-certificates lsb-release apt-transport-https 
```
- **curl**: to download the GPG key.
- **gnupg**: to convert the GPG key to apt format (dearmor).
- **lsb-release**: to obtain "VERSION_CODENAME".

- We add the official CouchDB repository, where official CouchDB packages are found. We also add its GPG key so apt trusts the repo. In this step, we download the key and save it in apt format (.gpg).
```bash
serjaii@db:~$ curl -fsSL https://couchdb.apache.org/repo/keys.asc | gpg --dearmor | sudo tee /usr/share/keyrings/couchdb-archive-keyring.gpg >/dev/null
```
- We add the entry to the sources list.
```bash
serjaii@db:~$ echo "deb [signed-by=/usr/share/keyrings/couchdb-archive-keyring.gpg] https://apache.jfrog.io/artifactory/couchdb-deb/ bookworm main" | sudo tee /etc/apt/sources.list.d/couchdb.list
```
- Update APT indices so the system recognizes the GPG key.
```bash
serjaii@db:~$ sudo apt update
```
- Launch CouchDB installation.
```bash
serjaii@db:~$ sudo apt install couchdb
```
- As we see, two typical errors appeared because it is trying to install CouchDB on Debian 12 using dependencies that may be obsolete in Debian 13. To install CouchDB, we will have to download and install the "libicu72" and "libmozjs-78-0" dependencies beforehand, which are the ones failing during installation.
```bash
serjaii@db:~$ wget http://ftp.debian.org/debian/pool/main/i/icu/libicu72_72.1-3+deb12u1_amd64.deb
serjaii@db:~$ wget http://ftp.debian.org/debian/pool/main/m/mozjs78/libmozjs-78-0_78.15.0-7_amd64.deb
serjaii@db:~$ sudo apt install ./libicu72_72.1-3+deb12u1_amd64.deb ./libmozjs-78-0_78.15.0-7_amd64.deb
```
The `./` before the filename tells apt to install from a local file, not from repositories. This will also resolve dependencies automatically if anything else is missing.

- Update system again and execute command to install "CouchDB".
```bash
serjaii@db:~$ sudo apt update
serjaii@db:~$ sudo apt install couchdb
```
- Select "Accept".
- Select "Standalone" option, as CouchDB will run on this machine only. It's the usual option for tests and local environments.
- Set a CouchDB Erlang magic cookie value.
- In the next page, as I want the server to listen to remote connections, I will configure the interface to "0.0.0.0".
- Add a password for the admin user, in my case "admin".
- Repeat password.
- Verify access to CouchDB.
```bash
serjaii@db:~$ curl http://localhost:5984/
```

### 2. Configuration for Remote Connection.
- Edit the `[httpd]` section in `/etc/couchdb/local.ini`, indicating with value "0.0.0.0" that CouchDB will listen on all network interfaces, not just localhost. We will also add a password for when we connect to admin user remotely.
```bash
serjaii@db:~$ sudo nano /opt/couchdb/etc/local.ini
serjaii@db:~$ grep -Ev "^;|^$" /opt/couchdb/etc/local.ini
```
- Verify CouchDB listens on all interfaces.
```bash
serjaii@db:~$ ss -tuln | grep 5984
```

### 3. CouchDB Client Installation.
Unlike other database systems, CouchDB does not require installing an independent client. This is because CouchDB is designed as an HTTP/REST server, meaning all management and data manipulation operations are done via HTTP requests in JSON format.
We have the following client options available:
- CouchDB includes a web client called **Fauxton** running directly in the browser.
    - Requires the admin user configured during installation.
    - No additional installation needed, cross-platform, accessible from any modern browser.
    - Allows: Creating/deleting databases, managing documents, users, permissions, views, and replication.
    - Access example: `http://SERVER_IP:5984/_utils/`

- CouchDB can be fully controlled using **curl**.
    - Works on any OS, no extra installation, allows automation via scripts.
    - Remote access example:
```bash
serjaii@db:~$ curl -u admin:myPassword http://SERVER_IP:5984/_all_dbs
```

### 4. Basic Use of CouchDB.
- After installing and configuring remote connection, verify server is active.
```bash
serjaii@db:~$ curl -u admin:myPassword http://SERVER_IP:5984/
```
- Create and list databases.
```bash
serjaii@db:~$ curl -X PUT -u admin:myPassword http://SERVER_IP:5984/test1
serjaii@db:~$ curl -u admin:myPassword http://SERVER_IP:5984/_all_dbs
```
- Create a document with automatic ID.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"type":"person","name":"Ana","age":29}' -u admin:myPassword http://SERVER_IP:5984/test1
```
- Create a document with known ID.
```bash
serjaii@db:~$ curl -X PUT -H "Content-Type: application/json" -d '{"type":"person","name":"Juan","age":35}' -u admin:myPassword http://SERVER_IP:5984/test1/juan
```
- Read created documents.
```bash
serjaii@db:~$ curl -u admin:myPassword http://SERVER_IP:5984/test1/_all_docs
serjaii@db:~$ curl -u admin:myPassword http://SERVER_IP:5984/test1/juan
```
- Delete a document (requires knowing the revision `_rev`).
```bash
serjaii@db:~$ curl -X DELETE "http://SERVER_IP:5984/test1/juan?rev=175f7db8e2f472106529dba1e056feb54" -u admin:myPassword
```
- Create an index on fields "type" and "age" using Mango queries.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"index":{"fields": ["type","age"]},"name":"idx_type_age","type":"json"}' -u admin:myPassword http://SERVER_IP/test1/_index
```
- Execute a Mango query. Returns JSON with documents where type is "person" and age > 25.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"selector":{"type":"person","age": {"$gt":25}},"fields":["_id","name","age"]}' -u admin:myPassword http://SERVER_IP:5984/test1/_find
```
- Create views with MapReduce.
```bash
serjaii@db:~$ curl -X PUT -H "Content-Type: application/json" -d '{"views":{"by_type": {"map":"function(doc) {if(doc.type)emit(doc.type,null);}"}},"language":"javascript"} ' -u admin:admin http://SERVER_IP:5984/test1/_design/people
```
- List or execute the view.
```bash
serjaii@db:~$ curl -u admin:myPassword "http://SERVER_IP:5984/test1/_design/people/_view/by_type"
```
- Local database replication.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"source":"test1","target":"test1_backup","create_target":true}' -u admin:myPassword http://SERVER_IP:5984/_replicate
```
- Create a user in CouchDB.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"_id":"org.couchdb.user:sergio","name":"sergio","roles": ["admin"],"type":"user","password":"sergio"}' -u admin:admin http://SERVER_IP:5984/_users
```
- Assign permissions to user on database.
```bash
serjaii@db:~$ curl -X PUT -H "Content-Type: application/json" -d '{"admins":{"names": [],"roles": []},"members":{"names":["sergio"],"roles":["admin"]}}' -u admin:myPassword http://SERVER_IP:5984/test1/_security
```
- Verify access with new user.
```bash
serjaii@db:~$ curl -u sergio:sergio http://SERVER_IP:5984/test1/_all_docs
```

### 5. CouchDB Internal Functioning.
**Architecture**
- Written in Erlang/OTP, using beam.smp VM.
- All communication is HTTP/REST, using JSON.
- Each document has unique `_id` and `_rev` (revision).

**Storage**
- Uses append-only B-trees (copy-on-write).
- Modifications create new nodes in the B-tree, guaranteeing consistent reads without locks.

**MVCC (Multi-Version Concurrency Control)**
- Allows concurrent reads without locks.
- Conflicts are detected on write and must be resolved by the application.

**Replication**
- Push/pull model: compares sequences (`_changes`) and replicates only differences.
- Supports continuous replication, ideal for distributed or offline-first bases.

**Compaction and Maintenance**
- Due to append-only model, files grow continuously.
- Periodic compaction of DB and views is used to free space.

## Installation of SQL Developer as remote ORACLE client using TNS connection.

### 1. Java 17 Installation
SQL Developer requires Java 17. Since Debian Trixie does not have it in its official repositories, we will install it from Adoptium:

- Install necessary dependencies.
```bash
sudo apt install -y wget apt-transport-https gpg
```
- Add GPG key for Adoptium.
```bash
serjaii@db:~$ wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | sudo gpg --dearmor -o /usr/share/keyrings/adoptium.gpg
```
- Add the repository.
```bash
serjaii@db:~$ echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb bookworm main" | sudo tee /etc/apt/sources.list.d/adoptium.list
```
- Update and install Java 17.
```bash
sudo apt update
sudo apt install -y temurin-17-jdk
```
- Verify installation.
```bash
java -version
```

### 2. Download SQL Developer from Oracle
- Download via the official SQL Developer link.
- Once downloaded, unzip the .zip file.
```bash
serjaii@db:~$ unzip sqldeveloper-24.3.1.347.1826-no-jre.zip
```
- We will have a folder with extracted files. Grant execution permissions to the `.sh` file in that directory.
```bash
serjaii@db:~$ chmod +x sqldeveloper/sqldeveloper.sh
serjaii@db:~$ ./sqldeveloper.sh
```
- Create `tnsnames.ora`.
```bash
serjaii@db:~$ nano .oracle/tnsnames.ora
```
- Content (adjust HOST IP and SERVICE_NAME as needed):
```ini
ORCLCDB =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.122.79)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ORCLCDB)
    )
  )
```
- Add Oracle environment variables to `.bashrc`.
```bash
serjaii@db:~$ nano ~/.bashrc 
export ORACLE_HOME=$HOME/oracle/instantclient_21_19 
export TNS_ADMIN=$HOME/.oracle 
export PATH=$ORACLE_HOME:$PATH 
export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH 
alias sqlplus='rlwrap sqlplus'
```
- Apply changes.
```bash
echo $TNS_ADMIN
```
- Verify output shows path to `.oracle`.
- Check `tnsnames.ora` is accessible.
```bash
serjaii@db:~$ cat $TNS_ADMIN/tnsnames.ora 
```
