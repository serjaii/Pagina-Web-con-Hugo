---
title: "Interconexión de Servidores de Bases de Datos: Oracle y PostgreSQL"
author: "Sergio Jiménez"
date: "2025-12-03"
categories: ["Base de Datos", "Oracle", "PostgreSQL", "Networking", "DevOps"]
tags: ["oracle", "postgresql", "dblink", "odbc", "heterogeneous-services", "oracle-fdw"]
image: "cover.png"
---

# Interconexión de Servidores

En este artículo detallo el proceso realizado para interconectar servidores de bases de datos Oracle y PostgreSQL en diferentes configuraciones: Oracle-Oracle, PostgreSQL-PostgreSQL y conexiones heterogéneas entre ambos sistemas.

## Preparación del Entorno

Para realizar esta práctica, he partido de una máquina virtual existente (`bd`) que ya contaba con los servidores de base de datos instalados. He clonado esta máquina para crear un segundo nodo (`bd2`).

```bash
virt-clone --original bd --name bd2 --auto-clone
```

### Configuración de red en bd2

Una vez clonada, he modificado la configuración de red de 'bd2' para asignarle la IP **192.168.122.127** y cambiar su hostname, evitando conflictos con la máquina original (cuya IP es 192.168.122.126).

```bash
# Cambiar IP
sudo sed -i 's/192.168.122.126/192.168.122.127/g' /etc/network/interfaces
# Cambiar hostname
sudo sed -i 's/bd/bd2/g' /etc/hosts
sudo hostnamectl set-hostname bd2
```

### Renombrar bases de datos en bd2

#### PostgreSQL
En el servidor PostgreSQL de 'bd2', renombré la base de datos a `prueba_db_2` para distinguirla claramente.

```sql
ALTER DATABASE prueba_db RENAME TO prueba_db_2;
```

#### Oracle
Para Oracle, realicé una serie de comandos para cerrar, renombrar y volver a abrir la Pluggable Database como `ORCLPDB2`.

```sql
ALTER PLUGGABLE DATABASE ORCLPDB1 CLOSE IMMEDIATE;
ALTER PLUGGABLE DATABASE ORCLPDB1 OPEN RESTRICTED;
ALTER PLUGGABLE DATABASE ORCLPDB1 RENAME GLOBAL_NAME TO ORCLPDB2;
ALTER PLUGGABLE DATABASE ORCLPDB2 CLOSE IMMEDIATE;
ALTER PLUGGABLE DATABASE ORCLPDB2 OPEN;
ALTER SYSTEM REGISTER;
```

---

## 1. Interconexión Oracle-Oracle

Configuré un Database Link para conectar desde la base de datos Oracle en `bd` hacia la base de datos Oracle en `bd2`.

### Configuración en ‘bd’

Edité el archivo `tnsnames.ora` para definir la conexión hacia `bd2`.

**Archivo**: `/opt/oracle/homes/OraDBHome21cEE/network/admin/tnsnames.ora`

```ini
BD2_LINK =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.122.127)(PORT = 1521))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = ORCLPDB2)
    )
  )
```

### Configuración en ‘bd2’

Me aseguré de que el listener estuviera escuchando correctamente y creé un usuario específico para la conexión.

```sql
ALTER SYSTEM SET local_listener='(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.122.127)(PORT=1521))' SCOPE=BOTH;
ALTER SYSTEM REGISTER;

-- Crear usuario en ORCLPDB2
ALTER SESSION SET CONTAINER=ORCLPDB2;
CREATE USER serjaii IDENTIFIED BY "0191";
GRANT CONNECT, RESOURCE TO serjaii;
GRANT CREATE SESSION TO serjaii;
```

### Crear Database Link

En `bd`, creé el enlace utilizando las credenciales del usuario creado anteriormente.

```sql
CREATE DATABASE LINK link_to_bd2
  CONNECT TO serjaii IDENTIFIED BY "0191"
  USING 'BD2_LINK';
```

### Comprobación

Realicé una consulta distribuida para verificar el enlace:

```sql
SELECT e.ename AS empleado_local, d.dname AS departamento_remoto
FROM emp e
JOIN dept@link_to_bd2 d ON e.deptno = d.deptno
WHERE e.deptno = 10;
```

**Resultado:**
```text
EMPLEADO_L DEPARTAMENTO_REMOTO
---------- ------------------
CLARK      ACCOUNTING
KING       ACCOUNTING
MILLER     ACCOUNTING
```

---

## 2. Interconexión PostgreSQL-PostgreSQL

Para conectar dos servidores PostgreSQL, utilicé la extensión `dblink`.

### Configuración Previa

Es necesario asegurar que ambos servidores permitan conexiones remotas:
*   `pg_hba.conf`: añadir `host all all 0.0.0.0/0 md5`
*   `postgresql.conf`: establecer `listen_addresses = '*'`

### Crear extensión dblink

Habilité la extensión en ambas bases de datos.

```sql
CREATE EXTENSION IF NOT EXISTS dblink;
```

### Verificación

Probé la conexión ejecutando una consulta remota desde `bd` hacia `bd2`.

```sql
SELECT e.ename, t.dname, t.loc
FROM emp e
JOIN dblink(
  'host=192.168.122.127 user=serjaii password=0191 dbname=prueba_db_2',
  'SELECT deptno, dname, loc FROM dept'
) AS t(deptno int, dname varchar, loc varchar)
ON e.deptno = t.deptno
WHERE e.deptno = 20;
```

**Resultado:**
```text
 ename |  dname   |  loc   
-------+----------+--------
 SMITH | RESEARCH | DALLAS
 JONES | RESEARCH | DALLAS
 SCOTT | RESEARCH | DALLAS
 ADAMS | RESEARCH | DALLAS
 FORD  | RESEARCH | DALLAS
```

---

## 3. Interconexión Oracle-PostgreSQL (Heterogeneous Services)

Esta configuración permite conectar desde Oracle hacia una base de datos PostgreSQL utilizando ODBC y Oracle Heterogeneous Services.

### Instalación de ODBC en bd

```bash
sudo apt-get update
sudo apt-get install -y unixodbc unixodbc-dev odbc-postgresql
```

### Configuración ODBC

Definí el Data Source Name (DSN) en `/etc/odbc.ini`.

```ini
[PostgreSQL_bd2]
Description=PostgreSQL connection to bd2
Driver=PostgreSQL Unicode
Servername=192.168.122.127
Port=5432
Database=prueba_db_2
Username=serjaii
Password=0191
```

Verifiqué la conexión con `isql -v PostgreSQL_bd2`.

### Configuración Heterogeneous Services

Creé el archivo de inicialización del gateway.

**Archivo**: `/opt/oracle/homes/OraDBHome21cEE/hs/admin/initpgbd2.ora`

```ini
HS_FDS_CONNECT_INFO = PostgreSQL_bd2
HS_FDS_TRACE_LEVEL = DEBUG
# Apuntar a la librería correcta es CRÍTICO para evitar errores
HS_FDS_SHAREABLE_NAME = /usr/lib/x86_64-linux-gnu/libodbc.so
set ODBCINI=/etc/odbc.ini
set LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/odbc
```

### Configuración de Listener y TNS

**Archivo**: `listener.ora`

```ini
SID_LIST_LISTENER =
  (SID_LIST =
    (SID_DESC =
      (SID_NAME = pgbd2)
      (ORACLE_HOME = /opt/oracle/product/21c/dbhome_1)
      (PROGRAM = dg4odbc)
      (ENVS="ODBCINI=/home/oracle/odbc.ini") 
    )
  )
```
*Nota: Es importante asegurar que el usuario Oracle tenga acceso al archivo odbc.ini, a veces es necesario copiarlo a su home o definir la variable ENVS adecuadamente.*

**Archivo**: `tnsnames.ora`

```ini
PGBD2 =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.122.126)(PORT = 1521))
    (CONNECT_DATA = (SID = pgbd2))
    (HS = OK)
  )
```

Recargué el listener con `lsnrctl reload`.

### Crear Database Link

```sql
CREATE DATABASE LINK link_to_postgres
  CONNECT TO "serjaii" IDENTIFIED BY "0191"
  USING 'PGBD2';
```

### Solución de Errores Comunes

Durante el proceso encontré el error `ORA-28500` con mensaje `[unixODBC][Driver Manager]Data source name not found`. Esto se debió a que el proceso del listener no encontraba el archivo `odbc.ini`. La solución fue configurar explícitamente la variable de entorno `ODBCINI` en el `listener.ora` o asegurar permisos de lectura para el usuario `oracle`. También corregí el `HS_FDS_SHAREABLE_NAME` para apuntar a `libodbc.so` en lugar del driver de Postgres directamente.

### Verificación

```sql
SELECT e.ename, e.job, e.sal
FROM emp e
WHERE e.sal > (SELECT AVG("sal") FROM "emp"@link_to_postgres);
```

**Resultado:**
```text
ENAME     JOB       SAL
--------- --------- ---------
JONES     MANAGER   2975
BLAKE     MANAGER   2850
CLARK     MANAGER   2450
SCOTT     ANALYST   3000
KING      PRESIDENT 5000
FORD      ANALYST   3000
```

---

## 4. Interconexión PostgreSQL-Oracle

Para conectar desde PostgreSQL hacia Oracle, utilicé la extensión `oracle_fdw`.

### Instalación

```bash
sudo apt-get install -y postgresql-server-dev-all build-essential unzip

# Descargar y compilar oracle_fdw
wget https://github.com/laurenz/oracle_fdw/archive/refs/heads/master.zip
unzip master.zip
cd oracle_fdw-master
export ORACLE_HOME=/opt/oracle/product/21c/dbhome_1
make
sudo make install
```

Configuré las librerías dinámicas para que PostgreSQL encuentre las de Oracle:

```bash
echo "/opt/oracle/product/21c/dbhome_1/lib" | sudo tee /etc/ld.so.conf.d/oracle.conf
sudo ldconfig
sudo systemctl restart postgresql
```

### Configuración en PostgreSQL

En la base de datos `prueba_db`:

```sql
CREATE EXTENSION oracle_fdw;

-- Crear el servidor foráneo
CREATE SERVER oracle_bd2 FOREIGN DATA WRAPPER oracle_fdw
OPTIONS (dbserver '//192.168.122.127:1521/ORCLPDB2');

-- Mapeo de usuario
CREATE USER MAPPING FOR serjaii SERVER oracle_bd2
OPTIONS (user 'serjaii', password '0191');

-- Importar esquema
IMPORT FOREIGN SCHEMA "SERJAII" LIMIT TO ("EMP", "DEPT")
FROM SERVER oracle_bd2 INTO public;
```

### Verificación

```sql
SELECT ename, job, sal FROM "EMP" WHERE deptno = 10;
```

**Resultado:**
```text
 ename  |    job    |   sal   
--------+-----------+---------
 CLARK  | MANAGER   | 2450.00
 KING   | PRESIDENT | 5000.00
 MILLER | CLERK     | 1300.00
```
