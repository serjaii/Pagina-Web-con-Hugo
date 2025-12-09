---
title: "Práctica Cooperativa: Despliegue Completo de Motores de Base de Datos"
author: "Sergio Jiménez, José María Oteo, David Dorante"
date: "2025-12-09"
categories: ["Base de Datos", "Oracle", "MariaDB", "PostgreSQL", "MongoDB", "DevOps"]
tags: ["oracle", "mysql", "postgresql", "mongodb", "neo4j", "redis", "cassandra", "memcached", "couchdb"]
image: "cover.png"
---

# Guía Cooperativa de Instalación y Configuración de Bases de Datos

Este documento recoge el trabajo realizado para la puesta en marcha de diversos sistemas gestores de bases de datos en **Debian 13**. A continuación se detallan los pasos para cada uno de ellos.

## Instalación de Oracle 21c sobre Debian 13

### 1.Configuración previa y dependencias

- En primer lugar actualizaremos los paquetes del sistema, para evitar posibles
conflictos de distintas versiones de paquetes durante la instalación de las
dependencias de Oracle.

```bash
serjaii@db:~$ sudo apt update && sudo apt upgrade -y
```
- Instalamos las dependencias de Oracle en nuestro sistema.
```bash
serjaii@db:~$ sudo apt policy libaio1t64 libaio-dev unixodbc rlwrap alien net-tools unzip bc ksh
```
- Usaje de cada dependencia
-

-

libaio1t64: dependencia de Entrada/Salida Asíncrona, obligatoria para
Oracle.
libaio-dev: contiene los archivos de cabecera y enlaces simbólicos para
que los desarrolladores puedan compilar programas que usen la librería
libaio.
unixodbc: librerías ODBC necesarias para Oracle.
rlwrap: mejora la experiencia de SQL*Plus en terminal.
bc: cálculos usados por scripts de Oracle.
ksh: KornShell, requerida por algunos scripts de instalación.
alien: convierte paquete .rpm a .deb.
not-tools: incluye netstat, usado por Oracle.
unzip: para SQL*Plus más tarde.

- Configuramos una ip estática para facilitar futuras conexiones remotas.

- En el hosts añadiremos una entrada apuntando hacia nuestra dirección privada.

- Oracle y SQL*Plus, necesitan la librería libaio.so.1, que no se encuentra en el
sistema ya que en Debian 13 ha cambiado el nombre del paquete y de la
librería, y por tanto para que no nos de error al intentar entrar en Oracle,
crearemos un enlace simbólico a partir de la librería libaio1t64 con nombre
libaio.so1, para que Oracle reconozca la librería.
Comprobación:
```bash
serjaii@db:~$ ls -l /usr/lib/x86_64-linux-gnu/libaio.so.1
```
lrwxrwxrwx 1 root root 40 oct 8 20:22 /usr/lib/x86_64-linuxgnu/libaio.so.1 -> /usr/lib/x86_64-linux-gnu/libaio.so.1t64

### 2.Instalación del servidor

- Posible Error: El proceso alien puede que requiera de más de 2GB de espacio
en /tmp, si no disponemos de ellos deberemos aumentar dicho tamaño

- Usamos el comando “alien” para convertir el paquete .rpm que acabamos de
descargarnos de Oracle 21c, a formato .deb, que es el formato de paquetes que
ejecuta Debian.

- Tras haber modificado la extensión del archivo a .deb, instalamos dicho
paquete de oracle manualmente.
```bash
serjaii@db:~$ sudo dpkg -i oracle-database-ee-21c_1.02_amd64.deb
```
- Ejecutamos el script de configuración creado por Oracle.
```bash
serjaii@db:~$ sudo /etc/init.d/oracledb_ORCLCDB-21c configure
```
- Para evitar que nos pida usuario y contraseña al entrar oracle, tendremos que
añadir nuestro usuario, en mi caso, david, al grupo dba.
```bash
serjaii@db:~$ sudo usermod -aG dba $USER
```
- Una vez que hemos instalado Oracle, tendremos que añadir las siguientes
variables de entorno en el bashrc de nuestra máquina donde hemos instalado el
servidor de Oracle.

```bash
serjaii@db:~$ grep '^export' ~/.bashrc export ORACLE_HOME=/opt/oracle/product/21c/dbhome_1 export ORACLE_SID=ORCLCDB export ORACLE_BASE=/opt/oracle export LD_LIBRARY_PATH=$ORACLE_HOME/lib:$LD_LIBRARY_PATH export PATH=$ORACLE_HOME/bin:$PATH export NLS_LANG=SPANISH_SPAIN.AL32UTF8
serjaii@db:~$ alias alias sqlplus='rlwrap sqlplus'
```
- Una vez añadida las variables de entorno, tendremos que recargar bashrc, para
que se apliquen las variables de entorno que acabamos de añadir.
```bash
serjaii@db:~$ source ~/.bashrc
```
- Comprobamos que podemos acceder como administrador a la base de datos.
```bash
serjaii@db:~$ sqlplus / as sysdba
```

### 3.Crear usuario y conceder permisos en Oracle 21c.
- Realizamos la siguiente configuración inicial para permitir la creación de
usuarios en Oracle.
```bash
SQL> STARTUP;
SQL> ALTER SESSION SET "_ORACLE_SCRIPT"=true;
```
- Nos creamos un usuario con el cuál vamos a probar a conectarnos después y le
aplicamos los permisos que consideremos al mismo.

```bash
SQL> CREATE USER dorante IDENTIFIED BY dorante;
SQL> GRANT ALL PRIVILEGES TO dorante;
```
- Para iniciar el servicio automáticamente al reiniciar vamos a modificar el
crontab (programador de tareas de linux).
```bash
serjaii@db:~$ sudo crontab -e
```
- Accedemos a la base de datos con el usuario que acabamos de crear.

### 4.Configuración del servidor Oracle para la conexión remota.
- Oracle por defecto, suele escuchar por localhost, por lo tanto vamos a modificar
el parámetro host del fichero listener.ora, para que escuche todas las peticiones
incluidas las peticiones remotas o externas.
```bash
serjaii@db:~$ sudo nano /opt/oracle/homes/OraDBHome21cEE/network/admin/li stener.ora
```
- También vamos a modificar el fichero tnsnames.ora, ya que es el que va a
indicar al cliente como conectarse a Oracle. En este caso, vamos a modificar el
valor “HOST” de “ORCLCDB”.
```bash
serjaii@db:~$ sudo nano /opt/oracle/homes/OraDBHome21cEE/network/admin/t nsnames.ora
```
- Reiniciamos la máquina para aplicar los cambios.
```bash
serjaii@db:~$ sudo reboot
```

### 5.Instalación y configuración del cliente de Oracle (SQL*Plus).
- Lo primero que vamos a hacer es actualizar los paquetes del sistema, para
evitar posibles conflictos de versiones de paquetes durante la instalación de las
dependencias de SQL*Plus.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos las dependencias necesarias que requiere la instalación del cliente
de Oracle.
```bash
serjaii@db:~$ sudo apt install libaio1t64 libaio-dev rlwrap wget p7zip-full -y -
```
libaio1t64: librería de I/O asíncrona, que lo necesita Oracle en tiempo
de ejecución.
libaio-dev: cabeceras y enlaces simbólicos para compilación.
rlwrap: permite usar historial y edición de comandos en sqlplus.
wget: para descargar los paquetes desde la web de Oracle.
p7zip-full: descomprime los .zip de Oracle.

- Al igual que en la instalación del servidor volveremos a crear el enlace
simbólico para ayudar a Debian a reconocer el paquete.
```bash
serjaii@db:~$ sudo ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64linux-gnu/libaio.so.1
```
- Creamos una carpeta que vamos a usar para trabajar con el cliente de Oracle.
```bash
serjaii@db:~$ mkdir
serjaii@db:~$ cd oracle oracle
```
- Descargamos los paquetes para poder trabajar con el cliente de Oracle, que son
Basic y SQL*Plus.
```bash
serjaii@db:~$ wget https://download.oracle.com/otn_software/linux/instant client/2119000/instantclient-basic-linux.x6421.19.0.0.0dbru.zip
serjaii@db:~$ wget https://download.oracle.com/otn_software/linux/instant client/2119000/instantclient-sqlplus-linux.x6421.19.0.0.0dbru.zip
```
- Comprobamos que se han descargado correctamente los paquetes y los
descomprimimos.
```bash
serjaii@db:~$ ls
serjaii@db:~$ 7z x instantclient-basic-linux.x6421.19.0.0.0dbru.zip
serjaii@db:~$ 7z x linux.x64-21.19.0.0.0dbru.zip instantclient-sqlplus-
```
- Añadimos las siguientes variables de entorno para que funcione correctamente
el cliente de Oracle.

```bash
serjaii@db:~$ sudo nano ~/.bashrc
```
- Ejecutamos el siguiente comando para aplicar los cambios que acabamos de
realizar en .bashrc.
```bash
serjaii@db:~$ source ~/.bashrc
```
- Nos conectamos desde el cliente al servidor Oracle.
```bash
serjaii@db:~$ sqlplus dorante/dorante@//192.168.122.79:1521/ORCLCDB
```

### 6.Creación de base de datos con tablas y datos en Oracle.
- Accedemos a la base de datos desde el servidor y accedemos como
administrador para poder crear la base de datos.

```bash
serjaii@db:~$ sqlplus / as sysdba SQL> ALTER SESSION SET "_ORACLE_SCRIPT"=true;
```
- Creamos la base de datos y le damos los privilegios necesarios.
```bash
SQL> CREATE USER hotel IDENTIFIED BY hotel123;
SQL> GRANT ALL PRIVILEGES TO hotel;
```
- Accedemos desde el cliente a la base de datos que acabamos de crear en
Oracle.
```bash
serjaii@db:~$ sqlplus hotel/hotel123@//192.168.122.79:1521/ORCLCDB
```
- Creamos las tablas que van a componer la base de datos ‘hotel’, para permitir
la gestión de un sistema de reservas de un hotel.
SQL

>

CREATE

TABLE
clientes(
id
INT,
nombre
VARCHAR(15)
NOT
NULL,
apellidos
VARCHAR(30)
NOT
NULL,
email
VARCHAR(50),
telefono
NUMBER(9),
CONSTRAINT pk_idCliente PRIMARY KEY (id),

CONSTRAINT

uq_email

UNIQUE

(email)

);

CREATE

TABLE

habitaciones(
id
INT,
numero
INT
NOT
NULL,
tipo
VARCHAR(20)
NOT
NULL,
precio
DECIMAL(10,2)
NOT
NULL,
CONSTRAINT pk_idHabitacion PRIMARY KEY (id),
CONSTRAINT uq_numero UNIQUE (numero),
CONSTRAINT ck_tipoHabitacion CHECK (tipo IN
('Individual',
'Doble',
'Suite',
'Familiar'))
);

CREATE

TABLE

reservas(
id
INT,
idCliente
INT
NOT
NULL,
idHabitacion
INT
NOT
NULL,
fecha_entrada
DATE
NOT
NULL,
fecha_salida
DATE
NOT
NULL,
CONSTRAINT pk_idReservas PRIMARY KEY (id),
CONSTRAINT fk_idCliente FOREIGN KEY (idCliente)
REFERENCES
clientes(id),
CONSTRAINT fk_idHabitacion FOREIGN KEY
(idHabitacion)
REFERENCES
habitaciones(id)
);

CREATE

TABLE
id
idReserva
INT
NOT
metodoPago
VARCHAR(20)
NOT
precio
DECIMAL(10,2)
NOT

pagos(
INT,
NULL,
NULL,
NULL,

fechaPago
DATE
NOT
NULL,
CONSTRAINT pk_idPagos PRIMARY KEY (id),
CONSTRAINT
fk_idReserva
FOREIGN
KEY
(idReserva)
REFERENCES
reservas(id),
CONSTRAINT ck_metodoPago CHECK (metodoPago
IN
('Tarjeta',
'Efectivo',
'PayPal'))
);

- Introducimos datos a la base de datos que acabamos de crear.
Datos Tabla clientes:
```bash
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(1, 'David', 'Dorado López', 'davidd@gmail.com',
600111222);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(2, 'María', 'Gómez Pérez', 'mariagom@gmail.com',
600333444);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(3, 'Jorge', 'Santos Díaz', 'jogesantos@gmail.com',
600555666);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(4, 'Lucía', 'Romero García', 'luciarom@yahoot.es',
600777888);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(5,
'Pablo',
'Ruiz
Torres',
'pablo@gmail.com',
600999000);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(6, 'Sofía', 'Martínez León', 'sofleon@yahoot.es',
601111222);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(7, 'Alberto', 'Navas Cruz', 'albertonavas@yahoot.es',
601333444);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(8,
'Marta',
'López
Gil',
'marta@gmail.com',
601555666);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(9, 'Raúl', 'Castro Vega', 'raulcastro@gmail.com',
601777888);
INSERT INTO clientes (id, nombre, apellidos, email,
telefono)
VALUES
(10, 'Laura', 'Morales Cano', 'laura@gmail.com',
601999000);
Datos tabla habitaciones:
INSERT INTO habitaciones (id, numero, tipo, precio)
VALUES
(1,
101,
'Individual',
50);
INSERT INTO habitaciones (id, numero, tipo, precio)
VALUES
(2,
102,
'Doble',
80);
INSERT INTO habitaciones (id, numero, tipo, precio)
VALUES
(3,
103,
'Suite',
150);
INSERT INTO habitaciones (id, numero, tipo, precio)
VALUES
(4,
104,
'Individual',
50);
INSERT INTO habitaciones (id, numero, tipo, precio)
VALUES
(5,
105,
'Doble',
80);
INSERT INTO habitaciones (id, numero, tipo, precio)
VALUES
(6, 106, 'Suite', 150);
Datos tabla reservas:
INSERT INTO reservas (id, idCliente, idHabitacion,
fecha_entrada, fecha_salida) VALUES (1, 1, 1,
TO_DATE('2025-10-01',
'YYYY-MM-DD'),
TO_DATE('2025-10-05',
'YYYY-MM-DD'));
INSERT INTO reservas (id, idCliente, idHabitacion,
fecha_entrada, fecha_salida) VALUES (2, 2, 2,
TO_DATE('2025-10-03',
'YYYY-MM-DD'),
TO_DATE('2025-10-06',
'YYYY-MM-DD'));
INSERT INTO reservas (id, idCliente, idHabitacion,
fecha_entrada, fecha_salida) VALUES (3, 3, 3,
TO_DATE('2025-10-02',
TO_DATE('2025-10-04',
'YYYY-MM-DD'),
'YYYY-MM-DD'));
INSERT INTO reservas (id, idCliente, idHabitacion,
fecha_entrada, fecha_salida) VALUES (4, 4, 4,
TO_DATE('2025-10-05',
'YYYY-MM-DD'),
TO_DATE('2025-10-10',
'YYYY-MM-DD'));
INSERT INTO reservas (id, idCliente, idHabitacion,
fecha_entrada, fecha_salida) VALUES (5, 5, 5,
TO_DATE('2025-10-07',
'YYYY-MM-DD'),
TO_DATE('2025-10-12',
'YYYY-MM-DD'));
INSERT INTO reservas (id, idCliente, idHabitacion,
fecha_entrada, fecha_salida) VALUES (6, 6, 6,
TO_DATE('2025-10-01',
'YYYY-MM-DD'),
TO_DATE('2025-10-03', 'YYYY-MM-DD'));
Datos tabla pagos:
INSERT INTO pagos (id, idReserva, metodoPago, precio,
fechaPago)
VALUES
(1,
1,
'Tarjeta',
200,
TO_DATE('2025-10-01',
'YYYY-MM-DD'));
INSERT INTO pagos (id, idReserva, metodoPago,
precio, fechaPago) VALUES (2, 2, 'Efectivo', 240,
TO_DATE('2025-10-03',
'YYYY-MM-DD'));
INSERT INTO pagos (id, idReserva, metodoPago,
precio, fechaPago) VALUES (3, 3, 'PayPal', 300,
TO_DATE('2025-10-02',
'YYYY-MM-DD'));
INSERT INTO pagos (id, idReserva, metodoPago,
precio, fechaPago) VALUES (4, 4, 'Tarjeta', 400,
TO_DATE('2025-10-05',
'YYYY-MM-DD'));
INSERT INTO pagos (id, idReserva, metodoPago,
precio, fechaPago) VALUES (5, 5, 'Efectivo', 320,
TO_DATE('2025-10-07',
'YYYY-MM-DD'));
INSERT INTO pagos (id, idReserva, metodoPago,
precio, fechaPago) VALUES (6, 6, 'PayPal', 150,
TO_DATE('2025-10-01', 'YYYY-MM-DD'));
```
- Comprobamos que todo se ha creado correctamente.
```bash
SELECT * FROM clientes;
```
Las interrogaciones que aparecen se deben a las tildes, ya que las base de datos
no entienden bien las tildes.

```bash
SELECT * FROM habitaciones;
SELECT * FROM reservas;
SELECT * FROM pagos;
```

## Instalación Servidor PostgreSQL en Debian 13.

### 1.Configuración previa y dependencias
- Antes de comenzar con la instalación de PostgreSQL, tendremos que actualizar
los paquetes del sistema.
```bash
serjaii@db:~$ sudo apt update
```

### 2.Instalación del servidor
- Instalamos el paquete de postgresql.
```bash
serjaii@db:~$ sudo apt install postgresql -y
```
- Comprobamos que se ha instalado el servidor revisando el estado de
PostgreSQL.
```bash
serjaii@db:~$ systemctl status postgresql
```
- Vamos a configurar postgreSQL para que se inicie siempre automáticamente al
iniciar el sistema. Para ello, ejecutaremos el siguiente comando.
```bash
serjaii@db:~$ sudo systemctl enable postgresql
```
- Comprobamos que podemos acceder al servidor postgres desde la propia
máquina donde está instalado.
```bash
serjaii@db:~$ sudo -u postgres psql
```

### 3.Configuración del servidor PostgreSQL para la conexión
remota.
- Modificamos el fichero “/etc/postgresql/17/main/postgresql.conf”, para permitir
conexiones remotas al servidor postgresql, descomentando la línea
“listen_addresses” en “CONNECTIONS AND AUTHENTICATION”, y
sustituyendo “localhost” por “*”, para permitir todas las conexiones. Una vez
realizado estos cambios, guardamos los cambios en el fichero y salimos.

```bash
serjaii@db:~$ sudo nano /etc/postgresql/17/main/postgresql.conf
```
Como vemos también podemos modificar el número máximo de conexiones. Por
defecto, PostgreSQL suele permitir la conexión de 100 dispositivos.

- Modificamos el fichero “/etc/postgresql/17/main/pg_hba.conf”, agregando la
siguiente línea final, para configurar permisos y permitir conexiones remotas.
```bash
sudo nano /etc/postgresql/17/main/pg_hba.conf
```
- Reiniciamos el servicio de postgresql, ejecutando el siguiente comando.
```bash
serjaii@db:~$ sudo systemctl restart postgresql
```

### 4.Crear base de datos, usuario y conceder permisos en
PostgreSQL.
- Accedemos a la base de datos como usuario privilegiado.
```bash
serjaii@db:~$ sudo -u postgres psql
```
- Con el siguiente comando vamos a crear una base de datos.
```bash
postgres=# CREATE DATABASE prueba_db;
```
- Creamos un usuario con contraseña.
```bash
postgres=# CREATE ROLE
PASSWORD 'dorante';
dorante
WITH
LOGIN
```
- Le damos los privilegios que consideremos necesarios. En mi caso le voy a dar
todos los privilegios.
```bash
postgres=# GRANT ALL PRIVILEGES ON DATABASE
prueba_db TO dorante;
postgres=# GRANT ALL PRIVILEGES ON ALL TABLES IN
SCHEMA public TO david;
postgres=# GRANT ALL PRIVILEGES ON ALL
SEQUENCES IN SCHEMA public TO david;
```
- Intentamos conectarnos a la base de datos que acabamos de crear desde nuestra
máquina local.
```bash
serjaii@db:~$ psql -h localhost -p 5432 -U dorante -d prueba_db
```

### 5.Instalación y configuración del cliente de PostgreSQL.
- Actualizamos los paquetes del sistema para evitar posibles conflictos durante la
instalación del cliente de PostgreSQL.
```bash
serjaii@db:~$ sudo apt update
```
- Una vez actualizados los paquetes del sistema, vamos a ejecutar el siguiente
comando, para instalar el cliente de postgreSQL.

```bash
serjaii@db:~$ sudo apt install postgresql-client -y
```
- Comprobamos que podemos acceder al servidor de PostgreSQL remotamente.
```bash
serjaii@db:~$ psql -h 192.168.122.79 -p 5432 -U dorante -d prueba_db
```

### 6.Creación de base de datos con tablas y datos en PostgreSQL.

- Accedemos al servidor de PostgreSQL desde la misma máquina donde se
encuentra instalado, accediendo como superusuario a la base de datos.
```bash
serjaii@db:~$ sudo -u postgres psql
```
- Creamos la base de datos, el usuario con el vamos a acceder a la base de datos
y dotamos de los privilegios necesarios para que ese usuario pueda acceder a
los datos de la base de datos.
```bash
postgres=# CREATE DATABASE hotel;
postgres=# CREATE USER david WITH PASSWORD
'david';
postgres=# GRANT ALL PRIVILEGES ON DATABASE
hotel TO david;
hotel=# GRANT ALL PRIVILEGES ON ALL TABLES IN
SCHEMA public TO david;
hotel=# GRANT ALL PRIVILEGES ON ALL SEQUENCES IN
SCHEMA public TO david;
hotel=# ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON TABLES TO david;
hotel=# ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON SEQUENCES TO david;
```
- Desde el cliente remoto accedemos a la base de datos que acabamos de crear
con el usuario que hemos creado también ahora, y comenzamos con la creación
de tablas e inserción de datos.
```bash
serjaii@db:~$ psql -h IP_ServidorPostgreSQL -p 5432 -U nombreUsuarioPostgreSQL -d baseDatosPostgreSQL Creación de la tabla clientes. CREATE nombre apellidos TABLE id VARCHAR(15) VARCHAR(30) clientes( NUMERIC, NOT NULL, NOT NULL, email VARCHAR(50), telefono NUMERIC(9), CONSTRAINT pk_idCliente PRIMARY KEY (id), CONSTRAINT uq_email UNIQUE (email) ); Creación de la tabla habitaciones. CREATE TABLE habitaciones( id NUMERIC, numero NUMERIC NOT NULL, tipo VARCHAR(20) NOT NULL, precio NUMERIC(10,2) NOT NULL, CONSTRAINT pk_idHabitacion PRIMARY KEY (id), CONSTRAINT uq_numero UNIQUE (numero), CONSTRAINT ck_tipoHabitacion CHECK (tipo IN ('Individual', 'Doble', 'Suite', 'Familiar')) ); Creación de la tabla reservas. CREATE TABLE reservas( id NUMERIC, idCliente NUMERIC NOT NULL, idHabitacion NUMERIC NOT NULL, fecha_entrada DATE NOT NULL, fecha_salida DATE NOT NULL, CONSTRAINT pk_idReservas PRIMARY KEY (id), CONSTRAINT fk_idCliente FOREIGN KEY (idCliente) REFERENCES clientes(id), CONSTRAINT fk_idHabitacion FOREIGN KEY (idHabitacion) REFERENCES habitaciones(id) ); Creación de la tabla pagos. CREATE TABLE pagos( id NUMERIC, idReserva NUMERIC NOT NULL, metodoPago VARCHAR(20) NOT NULL, precio NUMERIC(10,2) NOT NULL, fechaPago DATE NOT NULL, CONSTRAINT pk_idPagos PRIMARY KEY (id), CONSTRAINT fk_idReserva FOREIGN KEY (idReserva) REFERENCES reservas(id), CONSTRAINT ck_metodoPago CHECK (metodoPago IN ('Tarjeta', 'Efectivo', 'PayPal')) ); Inserción de datos en la tabla clientes. INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (1, 'David', 'Dorado Lopez', 'davidd@gmail.com', 600111222); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (2, 'Maria', 'Gomez Perez', 'mariagom@gmail.com', 600333444); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (3, 'Jorge', 'Santos Diaz', 'jogesantos@gmail.com', 600555666); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (4, 'Lucia', 'Romero Garcia', 'luciarom@yahoot.es', 600777888); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (5, 'Pablo', 'Ruiz Torres', 'pablo@gmail.com', 600999000); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (6, 'Sofia', 'Martinez Leon', 'sofleon@yahoot.es', 601111222); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (7, 'Alberto', 'Navas Cruz', 'albertonavas@yahoot.es', 601333444); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (8, 'Marta', 'Lopez Gil', 'marta@gmail.com', 601555666); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (9, 'Raul', 'Castro Vega', 'raulcastro@gmail.com', 601777888); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (10, 'Laura', 'Morales Cano', 'laura@gmail.com', 601999000); Inserción de datos en la tabla habitaciones. INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (1, 101, 'Individual', 50); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (2, 102, 'Doble', 80); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (3, 103, 'Suite', 150); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (4, 104, 'Individual', 50); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (5, 105, 'Doble', 80); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (6, 106, 'Suite', 150); Inserción de datos en la tabla reservas. INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (1, 1, 1, TO_DATE('2025-10-01', 'YYYY-MM-DD'), TO_DATE('2025-10-05', 'YYYY-MM-DD')); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (2, 2, 2, TO_DATE('2025-10-03', 'YYYY-MM-DD'), TO_DATE('2025-10-06', 'YYYY-MM-DD')); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) TO_DATE('2025-10-02', TO_DATE('2025-10-04', VALUES (3, 3, 3, 'YYYY-MM-DD'), 'YYYY-MM-DD')); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (4, 4, 4, TO_DATE('2025-10-05', 'YYYY-MM-DD'), TO_DATE('2025-10-10', 'YYYY-MM-DD')); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (5, 5, 5, TO_DATE('2025-10-07', 'YYYY-MM-DD'), TO_DATE('2025-10-12', 'YYYY-MM-DD')); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (6, 6, 6, TO_DATE('2025-10-01', 'YYYY-MM-DD'), TO_DATE('2025-10-03', 'YYYY-MM-DD')); Inserción de datos en la tabla pagos. INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (1, 1, 'Tarjeta', 200, TO_DATE('2025-10-01', 'YYYY-MM-DD')); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (2, 2, 'Efectivo', 240, TO_DATE('2025-10-03', 'YYYY-MM-DD')); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (3, 3, 'PayPal', 300, TO_DATE('2025-10-02', 'YYYY-MM-DD')); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (4, 4, 'Tarjeta', 400, TO_DATE('2025-10-05', 'YYYY-MM-DD')); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (5, 5, 'Efectivo', 320, TO_DATE('2025-10-07', 'YYYY-MM-DD')); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (6, 6, 'PayPal', 150, TO_DATE('2025-10-01', 'YYYY-MM-DD'));
```

## Instalación Servidor MySQL en Debian 13.

### 1.Instalación del servidor
- Primero vamos a actualizar el sistema y comprobar que no tenga
actualizaciones, para que no de error al instalar los nuevos paquetes del
servidor mariaDB.
```bash
serjaii@db:~$ sudo apt update
```
- Una vez actualizados los paquetes del sistema, vamos a ejecutar el siguiente
comando, para instalar “mariaDB”.

```bash
serjaii@db:~$ sudo apt install mariadb-server -y
```
- Comprobamos que se ha instalado correctamente el servidor de MariaDB y que
está levantado.
```bash
serjaii@db:~$ sudo systemctl status mariadb
```
- Ejecutamos el siguiente comando para que se inicie el servidor mariadb cada
vez que iniciemos la máquina.
```bash
serjaii@db:~$ sudo systemctl enable mariadb
```
- Comprobamos que podemos entrar en MySQL.

```bash
serjaii@db:~$ sudo mysql -u root -p
```

### 2.Configuración del servidor MySQL para la conexión remota.
- Modificamos el fichero “/etc/mysql/mariadb.conf.d/50-server.cnf”, para
permitir conexiones remotas al servidor mariaDB, modificamos la línea “bindaddress”, para permitir que pueda tener conexión remota. Una vez modificado
esto, guardamos los cambios y salimos.
```bash
serjaii@db:~$ sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
```
- Reiniciamos el servidor para que se apliquen los cambios.
```bash
serjaii@db:~$ sudo systemctl restart mariadb
```

### 3.Crear base de datos de prueba, usuario y conceder permisos
en MySQL.
- Entramos en Mysql.
```bash
serjaii@db:~$ sudo mysql -u root -p
```
- Creamos un usuario con contraseña.
MariaDB [(none)]>
CREATE
IDENTIFIED BY 'dorante';

USER

'dorante'@'%'

- Damos los privilegios necesarios para poder conectarnos remotamente también
con el usuario que acabamos de crear.
MariaDB [(none)]> GRANT ALL PRIVILEGES ON *.* TO
'dorante'@'%' WITH GRANT OPTION;

- Probamos que podemos conectarnos con el usuario que acabamos de crear
desde nuestra propia máquina local.
```bash
serjaii@db:~$ sudo mysql -h localhost -P 3306 -u dorante -p
```

### 4.Instalación y configuración del cliente de MySQL.
- Actualizamos los paquetes del sistema para evitar conflictos durante la
instalación del cliente de MySQL.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos el cliente de MySQL.
```bash
serjaii@db:~$ sudo apt install mariadb-client -y
```
- Probamos a conectarnos al servidor de MySQL, desde el cliente.
```bash
serjaii@db:~$ mysql -h 192.168.122.79 -P 3306 -u dorante -p
```

### 5.Creación de base de datos con tablas y datos en MySQL.
- Accedemos al servidor de MySQL desde la misma máquina donde se encuentra
instalado, accediendo como superusuario a la base de datos.
```bash
serjaii@db:~$ sudo mysql -u root -p
```
- Creamos la base de datos, el usuario con el vamos a acceder a la base de datos
y dotamos de los privilegios necesarios para que ese usuario pueda acceder a
los datos de la base de datos.
MariaDB [(none)]> CREATE DATABASE hotel;

MariaDB
[(none)]>
CREATE
IDENTIFIED BY 'david';

USER

'david'@'%'

MariaDB [(none)]> GRANT ALL PRIVILEGES ON hotel.*
TO 'david'@'%';

MariaDB [(none)]> FLUSH PRIVILEGES;

- Desde el cliente remoto accedemos a la base de datos que acabamos de crear
con el usuario que hemos creado también ahora, y comenzamos con la creación
de tablas e inserción de datos.
```bash
serjaii@db:~$ mysql -h IP_SERVIDOR_MYSQL -P 3306 -u usuario -p MariaDB [(none)]> USE hotel; Creación de la tabla clientes. CREATE TABLE clientes( id NUMERIC, nombre VARCHAR(15) NOT NULL, apellidos VARCHAR(30) NOT NULL, email VARCHAR(50), telefono NUMERIC(9), CONSTRAINT pk_idCliente PRIMARY KEY (id), CONSTRAINT uq_email UNIQUE (email) ); Creación de la tabla habitaciones. CREATE TABLE habitaciones( id NUMERIC, numero NUMERIC NOT NULL, tipo VARCHAR(20) NOT NULL, precio NUMERIC(10,2) NOT NULL, CONSTRAINT pk_idHabitacion PRIMARY KEY (id), CONSTRAINT uq_numero UNIQUE (numero), CONSTRAINT ck_tipoHabitacion CHECK (tipo IN ('Individual', 'Doble', 'Suite', 'Familiar')) ); Creación de la tabla reservas. CREATE TABLE reservas( id NUMERIC, idCliente NUMERIC NOT NULL, idHabitacion NUMERIC NOT NULL, fecha_entrada DATE NOT NULL, fecha_salida DATE NOT NULL, CONSTRAINT pk_idReservas PRIMARY KEY (id), CONSTRAINT fk_idCliente FOREIGN KEY (idCliente) REFERENCES clientes(id), CONSTRAINT fk_idHabitacion FOREIGN KEY (idHabitacion) REFERENCES habitaciones(id) ); Creación de la tabla pagos. CREATE TABLE pagos( id NUMERIC, idReserva NUMERIC NOT NULL, metodoPago VARCHAR(20) NOT NULL, precio NUMERIC(10,2) NOT NULL, fechaPago DATE NOT NULL, CONSTRAINT pk_idPagos PRIMARY KEY (id), CONSTRAINT fk_idReserva FOREIGN KEY (idReserva) REFERENCES reservas(id), CONSTRAINT ck_metodoPago CHECK (metodoPago IN ('Tarjeta', 'Efectivo', 'PayPal')) ); Inserción de datos en la tabla clientes. INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (1, 'David', 'Dorado Lopez', 'davidd@gmail.com', 600111222); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (2, 'Maria', 'Gomez Perez', 'mariagom@gmail.com', 600333444); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (3, 'Jorge', 'Santos Diaz', 'jogesantos@gmail.com', 600555666); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (4, 'Lucia', 'Romero Garcia', 'luciarom@yahoot.es', 600777888); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (5, 'Pablo', 'Ruiz Torres', 'pablo@gmail.com', 600999000); INSERT INTO clientes (id, nombre, apellidos, email, telefono) (6, 'Sofia', 601111222); 'Martinez Leon', VALUES 'sofleon@yahoot.es', INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (7, 'Alberto', 'Navas Cruz', 'albertonavas@yahoot.es', 601333444); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (8, 'Marta', 'Lopez Gil', 'marta@gmail.com', 601555666); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (9, 'Raul', 'Castro Vega', 'raulcastro@gmail.com', 601777888); INSERT INTO clientes (id, nombre, apellidos, email, telefono) VALUES (10, 'Laura', 'Morales Cano', 'laura@gmail.com', 601999000); Inserción de datos en la tabla habitaciones. INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (1, 101, 'Individual', 50); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (2, 102, 'Doble', 80); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (3, 103, 'Suite', 150); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (4, 104, 'Individual', 50); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (5, 105, 'Doble', 80); INSERT INTO habitaciones (id, numero, tipo, precio) VALUES (6, 106, 'Suite', 150); Inserción de datos en la tabla reservas. INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (1, 1, 1, '2025-1063 01', '2025-10-05'); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (2, 2, 2, '2025-1003', '2025-10-06'); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (3, 3, 3, '2025-1002', '2025-10-04'); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (4, 4, 4, '2025-1005', '2025-10-10'); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (5, 5, 5, '2025-1007', '2025-10-12'); INSERT INTO reservas (id, idCliente, idHabitacion, fecha_entrada, fecha_salida) VALUES (6, 6, 6, '2025-1001', '2025-10-03'); Inserción de datos en la tabla pagos. INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (1, 1, 'Tarjeta', 200, '2025-10-01'); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (2, 2, 'Efectivo', 240, '2025-1064 03'); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (3, 3, 'PayPal', 300, '2025-10-02'); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (4, 4, 'Tarjeta', 400, '2025-10-05'); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (5, 5, 'Efectivo', 320, '2025-1007'); INSERT INTO pagos (id, idReserva, metodoPago, precio, fechaPago) VALUES (6, 6, 'PayPal', 150, '2025-10-01');
```
- Comprobación de la creación de tablas e inserción de datos.
```bash
SELECT * FROM clientes;
MariaDB [hotel]> SELECT * FROM habitaciones;
MariaDB [hotel]> SELECT * FROM reservas;
MariaDB [hotel]> SELECT * FROM pagos;
```

## Instalación Servidor MongoDB en Debian 13.

### 1.Dependencias y configuración previa
- Actualizamos los paquetes del sistema para evitar posibles conflictos de
versiones durante la instalación del servidor de MongoDB.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos las siguientes dependencias.
```bash
serjaii@db:~$ sudo apt install curl gnupg -y - curl: sirve para descargar archivos desde Internet. gnupg: permite manejar claves criptográficas como las claves GPG.
```
- Ejecutamos el siguiente comando para descargar la clave pública GPG oficial
de MongoDB, y con “gpg --dearmor” la convertimos en formato binario para
que apt pueda usarla.
```bash
serjaii@db:~$ sudo curl -fsSL https://pgp.mongodb.com/server-8.0.asc | sudo gpg -dearmor -o /usr/share/keyrings/mongodbserver-8.0.gpg
```
- Con el siguiente comando voy a añadir el repositorio de MongoDB. El
siguiente comando lo que hace es crear un nuevo archivo de lista de
repositorios (mongodb-org-8.0.list) en “/etc/apt/sources.list.d/”, escribiendo
dentro del fichero una línea que le dice a apt lo siguiente:
-

Usa el repositorio de MongoDB.
Está en https://repo.mongodb.org/apt/debian.
Usa la versión bookworm, que es equivalente tanto para Debian 12
como para Debian 13.
La sección es main.
Los
paquetes
deben
estar
firmados
con
la
clave
“/usr/share/keyrings/mongodb-server-8.0.gpg”.

```bash
serjaii@db:~$ sudo echo "deb [signed-by=/usr/share/keyrings/mongodbserver-8.0.gpg] https://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-8.0.list
```
- Volvemos a actualizar los paquetes e instalamos MongoDB.
```bash
serjaii@db:~$ sudo apt update
```

### 2.Instalación del servidor

```bash
serjaii@db:~$ sudo apt install mongodb-org -y
```
- Iniciamos y habilitamos MongoDB para que se inicie cada vez que se inicie la
máquina.
```bash
serjaii@db:~$ sudo systemctl start mongod
serjaii@db:~$ sudo systemctl enable mongod
```
- Verificamos el estado del servidor de MongoDB.
```bash
serjaii@db:~$ sudo systemctl status mongod
```
- Comprobamos que podemos entrar en mongodb desde el local.
```bash
serjaii@db:~$ mongosh
```

### 3.Configuración del servidor MongoDB para la conexión
remota.
- Para permitir el acceso remoto al servidor de MongoDB, tendremos que
modificar el parámetro “bindIp” a “0.0.0.0”, en el fichero “/etc/mongod.conf”.

```bash
serjaii@db:~$ sudo nano /etc/mongod.conf
```
- Reiniciamos el servicio de MongoDB para aplicar los cambios.
```bash
serjaii@db:~$ sudo systemctl restart mongod
```

### 4.Crear base de datos de prueba, usuario y conceder permisos
en MongoDB.
- Accedemos al servidor de mongoDB en el mismo equipo.
```bash
serjaii@db:~$ mongosh
```
- Creamos una base de datos de prueba.
test> use pruebadb

- Vamos a crear un usuario de prueba también con contraseña, que solo pueda
operar sobre la base de datos que acabamos de crear. Pero para ello, tenemos
que hacerlo usando la base de datos que acabamos de crear.
pruebadb> db.createUser({
... user: "dorante",
... pwd: "dorante",
... roles: [
...
{ role: "readWrite", db: "pruebadb" }
... ]
... })

- En el fichero “/etc/mongod.config”, vamos a habilitar para que se fuerce la
autenticación.

```bash
serjaii@db:~$ sudo nano /etc/mongod.conf
```
- Reiniciamos el servicio de MongoDB para aplicar los cambios.
```bash
serjaii@db:~$ sudo systemctl restart mongod
```
- Comprobamos que podemos conectarnos al usuario que acabamos de crear y a
la base de datos.
```bash
serjaii@db:~$ mongosh -u dorante -p dorante -authenticationDatabase pruebadb
```

### 5.Instalación y configuración del cliente de MongoDB.
- Actualizamos los paquetes del sistema para evitar posibles conflictos de
versiones durante la instalación del servidor de MongoDB.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos las siguientes dependencias.
```bash
serjaii@db:~$ sudo apt install curl gnupg -y
```
- Ejecutamos el siguiente comando para descargar la clave pública GPG oficial
de MongoDB, y con “gpg --dearmor” la convertimos en formato binario para
que apt pueda usarla.
```bash
serjaii@db:~$ sudo curl -fsSL https://pgp.mongodb.com/server-8.0.asc | sudo gpg -75 dearmor -o server-8.0.gpg /usr/share/keyrings/mongodb-
```
- A continuación, vamos a añadir el repositorio de MongoDB con el siguiente
comando.
```bash
sudo echo "deb [signed-by=/usr/share/keyrings/mongodbserver-8.0.gpg]
https://repo.mongodb.org/apt/debian
bookworm/mongodb-org/8.0
main"
|
sudo
tee
/etc/apt/sources.list.d/mongodb-org-8.0.list
```
- Volvemos a actualizar los paquetes.
```bash
serjaii@db:~$ sudo apt update
```
- Con el siguiente comando vamos a instalar mongoDB, pero solo el cliente
moderno de MongoDB, ya que tenemos el servidor instalado en la máquina
remota.
```bash
serjaii@db:~$ sudo apt install -y mongodb-mongosh
```
- Comprobamos que podemos conectarnos desde el cliente en nuestro local al
servidor remoto.
```bash
serjaii@db:~$ mongosh "mongodb://usuario:contraseña@IP_DEL_SERVIDOR:2 7017/pruebadb?authSource=pruebadb"
```

### 6.Creación de usuario, base de datos con tablas y datos en
MongoDB.
- Nos conectamos al servidor desde su propia máquina y creamos la base de
datos y el usuario con el que vamos a acceder a la base de datos remotamente.
```bash
serjaii@db:~$ mongosh test> use hotel hotel> db.createUser({ user: "david", pwd: "david", roles: [{ role: "readWrite", db: "hotel" }] }) { ok: 1 }
```
- Volvemos a activar la autenticación en “/etc/mongod.conf”.

```bash
serjaii@db:~$ sudo systemctl restart mongod
```
- Nos conectamos remotamente, y comenzamos a crear colecciones e insertar
datos.

```bash
serjaii@db:~$ mongosh "mongodb://usuario:contraseña@IP_DEL_SERVIDOR:2 7017/pruebadb?authSource=pruebadb" Creación de la colección clientes e inserción de datos. db.clientes.insertMany([ {_id:1, nombre:"David", apellido1:"Dorado", apellido2:"Lopez", email:"davidd@gmail.com", telefono:600111222}, {_id:2, nombre:"Maria", apellido1:"Gomez", apellido2:"Perez", email:"mariagom@gmail.com", telefono:600333444}, {_id:3, nombre:"Jorge", apellido1:"Santos", apellido2:"Diaz", email:"jorgesantos@gmail.com", telefono:600555666}, {_id:4, nombre:"Lucia", apellido1:"Romero", apellido2:"Garcia", email:"luciarom@yahoo.es", telefono:600777888}, {_id:5, nombre:"Pablo", apellido1:"Ruiz", apellido2:"Torres", email:"pablo@gmail.com", telefono:600999000}, {_id:6, nombre:"Sofia", apellido1:"Martinez", apellido2:"Leon", email:"sofleon@yahoo.es", telefono:601111222}, {_id:7, nombre:"Alberto", apellido1:"Navas", apellido2:"Cruz", email:"albertonavas@yahoo.es", telefono:601333444}, {_id:8, nombre:"Marta", apellido1:"Lopez", apellido2:"Gil", email:"marta@gmail.com", telefono:601555666}, {_id:9, nombre:"Raul", apellido1:"Castro", apellido2:"Vega", email:"raulcastro@gmail.com", telefono:601777888}, {_id:10, nombre:"Laura", apellido1:"Morales", apellido2:"Cano", email:"laura@gmail.com", telefono:601999000}, ]); Creación de la colección habitaciones e inserción de datos. db.habitaciones.insertMany([ {_id:1, numero:101, tipo:"Individual", precio:50}, {_id:2, numero:102, tipo:"Doble", precio:80}, {_id:3, numero:103, tipo:"Suite", precio:150}, {_id:4, numero:104, tipo:"Individual", precio:50}, {_id:5, numero:105, tipo:"Doble", precio:80}, {_id:6, numero:106, tipo:"Suite", precio:150} ]); Creación de la colección servicios e inserción de datos. db.servicios.insertMany([ { _id:1, servicio:"Desayuno", precio:5 }, { _id:2, servicio:"Spa", precio:20 }, { _id:3, servicio:"Gimnasio", precio:0 }, { _id:4, servicio:"Piscina cubierta", precio:0 }, { _id:5, servicio:"Aparcamiento", precio:10 }, { _id:6, servicio:"Limpieza extra", precio:15 }, { _id:7, servicio:"Wi-Fi Premium", precio:3 }, { _id:8, servicio:"Transporte aeropuerto", precio:25 }, { _id:9, servicio:"Cuna para bebé", precio:5 }, { _id:10, servicio:"Late check-out", precio:12 }, ]);
```
- Comprobamos que se han creado las colecciones con los datos correctamente.
Colección clientes.
hotel> db.clientes.find();

Colección habitaciones.
hotel> db.habitaciones.find();

Colección servicios.
hotel> db.servicios.find();

## Instalación Servidor Neo4J en Debian 13.

### 1.Instalación de dependencias
- Actualizamos los paquetes del sistema para evitar conflictos durante la
instalación de paquetes y dependencias.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos las dependencias y utilidades básicas para Neo4J.
```bash
serjaii@db:~$ sudo apt install -y wget curl gnupg lsb-release ca-certificates apt-transport-https - wget/curl: descargar archivos desde internet. gnupg: manejar claves de seguridad (GPG). lsb-release: saber la versión del sistema. ca-certificates y apt-transport-https: permiten usar repositorios HTTPS de forma segura.
```
- Neo4j necesita java para funcionar. En mi caso, voy a instalar Temurin Java 21,
usando una versión mantenida por Adoptium.
```bash
serjaii@db:~$ wget -qO https://packages.adoptium.net/artifactory/api/gpg/key/p ublic | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/adoptium.gpg > /dev/null
```
Con este comando, estamos descargando y guardando la clave GPG para poder
confiar en los paquetes de Adoptium.
- Añadimos el repositorio de Adoptium desde donde apt puede descargar los
paquetes Temurin (Java 21).
```bash
serjaii@db:~$ echo [signed-by=/etc/apt/trusted.gpg.d/adoptium.gpg] https://packages.adoptium.net/artifactory/deb (lsb_release -cs) main" | sudo /etc/apt/sources.list.d/adoptium.list "deb $ tee
```
- Volvemos a actualizar los repositorios antes de instalar java 21.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos Java Development Kit 21, necesario para ejecutar Neo4j.
```bash
serjaii@db:~$ sudo apt install -y temurin-21-jdk
```
- Comprobamos que se ha descargado java correctamente.
```bash
serjaii@db:~$ java -version
```
- Añadimos la clave de Neo4j, descargando y guardando la clave oficial de
Neo4j para verificar los paquetes.
```bash
serjaii@db:~$ wget -qO https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/neo4j.gpg > /dev/null
```
- Añadimos el repositorio oficial de dónde se descargará Neo4j.

```bash
serjaii@db:~$ echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
```

### 2.Instalación del servidor
- Actualizamos los paquetes, para refrescar la lista de paquetes antes de instalar
Neo4j.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos Neo4j.
```bash
serjaii@db:~$ sudo apt install neo4j -y
```
- Antes de iniciar por primera vez el servidor de Neo4j, hay que definir la
contraseña del usuario administrador de Neo4j. Para ello, vamos a asegurarnos
que el servicio esté apagado antes.
```bash
serjaii@db:~$ sudo systemctl status neo4j
```
- Fijamos la contraseña inicial para el usuario neo4j.
```bash
serjaii@db:~$ sudo neo4j-admin dbms set-initialpassword 'root1234'
```
- Iniciamos el servicio de Neo4j y comprobamos que podemos acceder a la base
de datos de Neo4j.
```bash
serjaii@db:~$ sudo systemctl start neo4j
serjaii@db:~$ sudo systemctl status neo4j
serjaii@db:~$ sudo systemctl enable neo4j
serjaii@db:~$ cypher-shell -u neo4j -p 'root1234'
```

### 3.Configuración del Servidor Neo4J en Debian 13 para la
conexión remota.

- Por defecto Neo4j escucha sólo en localhost. Por lo tanto, vamos a modificar en
el fichero “/etc/neo4j/neo4j.conf”, las siguientes líneas para permitir la
conexión remota.
```bash
serjaii@db:~$ sudo nano /etc/neo4j/neo4j.conf
serjaii@db:~$ grep -E 'server.default_listen_address| server.bolt.listen_address|server.http.listen_address' /etc/neo4j/neo4j.conf - 0.0.0.0: escuchar todas las interfaces de red.
```
Puerto 7687: activar protocolo Bolt en el puerto 7687, usado por
clientes como cypher-shell.
Puerto 7474: interfaz web de Neo4j accesible desde el navegador.

- Reiniciamos el servicio de Neo4j para que se apliquen los cambios de
configuración remota.
```bash
serjaii@db:~$ sudo systemctl restart neo4j
```
- Verificamos que el servicio está escuchando por los puertos que hemos
activado.
```bash
serjaii@db:~$ ss -tlnp | grep 7687
serjaii@db:~$ curl -I http://localhost:7474
```

### 4.Instalación y configuración del cliente de Neo4j en Debian 13.
- Actualizamos los paquetes del sistema para evitar conflictos durante la
instalación del cliente.
```bash
serjaii@db:~$ sudo apt update && sudo apt upgrade -y
```
- Nos descargamos los repositorios oficiales y clave gpg del cliente de Neo4j.
```bash
serjaii@db:~$ wget -qO https://debian.neo4j.com/neotechnology.gpg.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/neo4j.gpg > /dev/null
```
- Añadimos la clave de Neo4j.
```bash
serjaii@db:~$ echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
```
- Actualizamos los paquetes del sistema para que se incluyan los repositorios y la
clave de Neo4j al sistema.
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos el cliente de línea de comandos de Neo4j.
```bash
serjaii@db:~$ sudo apt install -y cypher-shell
```
- Comprobamos que podemos conectar remotamente desde el cliente al servidor
de Neo4j.
```bash
serjaii@db:~$ cypher-shell bolt://IP_SERVIDOR:7687 -u neo4j -p 'root1234' -a
```

### 5.Creación de usuario, base de datos con nodos e inserción de
datos de Neo4j.
Durante la instalación de Neo4j se ha utilizado la edición Community, que es la
versión gratuita y de código abierto.
Esta edición no permite la creación base de datos adicionales, por lo que todas las
pruebas y ejercicios las realizaremos sobre la base de datos por defecto llamada
“neo4j”.

- Accedemos a la base de datos desde el cliente, y creamos un nuevo usuario y le
otorgamos los permisos necesarios adecuados al usuario creado para que pueda
interactuar sobre la base de datos por defecto. En este caso, al igual que hemos
explicado antes con la creación de la base de datos, la edición Community
tampoco tiene las opciones de darle privilegios a los usuarios, sino que durante
la creación del usuario, el usuario tiene todos los permisos por defecto, como si
fuera admin.
```bash
serjaii@db:~$ cypher-shell bolt://192.168.122.79:7687 -u neo4j -p 'root1234' neo4j@neo4j> PASSWORD REQUIRED; -a CREATE USER nombreUsuario SET 'contraseñaUsuario' CHANGE NOT
```
Con la opción “CHANGE NOT REQUIRED”, hemos indicado que no necesita
cambiar la contraseña en su primer inicio de sesión.
- Creamos los nodos correspondientes con sus datos.
Creación de clientes.
```bash
CREATE (:Cliente {id: 1, nombre: "David", apellido1:
"Dorado",
apellido2:
"Lopez",
email:
"davidd@gmail.com",
telefono:
600111222});
CREATE (:Cliente {id: 2, nombre: "Maria", apellido1:
"Dorado",
apellido2:
"Lopez",
email:
"davidd@gmail.com",
telefono:
600333444});
CREATE (:Cliente {id: 3, nombre: "Jorge", apellido1:
"Santos",
apellido2:
"Diaz",
email:
"jorgesantos@gmail.com",
telefono:
600555666});
CREATE (:Cliente {id: 4, nombre: "Lucia", apellido1:
"Romero",
apellido2:
"Garcia",
email:
"luciarom@yahoot.es",
telefono:
600777888});
CREATE (:Cliente {id: 5, nombre: "Pablo", apellido1:
"Ruiz", apellido2: "Torres", email: "pablo@gmail.com",
telefono:
600999000});
CREATE (:Cliente {id: 6, nombre: "Sofia", apellido1:
"Martinez",
apellido2:
"Leon",
email:
"sofleon@yahoot.es",
telefono:
601111222});
CREATE (:Cliente {id: 7, nombre: "Roberto", apellido1:
"Navas",
apellido2:
"Cruz",
email:
"albertonavas@yahoot.es",
telefono:
601333444});
CREATE (:Cliente {id: 8, nombre: "Marta", apellido1:
"Lopez", apellido2: "Gil", email: "marta@gmail.com",
telefono:
601555666});
CREATE (:Cliente {id: 9, nombre: "Raul", apellido1:
"Castro",
apellido2:
"Vega",
email:
"raulcastro@gmail.com",
telefono:
601777888});
CREATE (:Cliente {id: 10, nombre: "laura", apellido1:
"Morales",
apellido2:
"Cano",
email:
"laura@gmail.com", telefono: 601999000});
Creación de habitaciones.
CREATE (:Habitacion {id: 1, numero: 101,
"Individual"});
CREATE (:Habitacion {id: 2, numero: 102,
"Doble"});
CREATE (:Habitacion {id: 3, numero: 103,
"Suite"});
CREATE (:Habitacion {id: 4, numero: 104,
"Individual"});
CREATE (:Habitacion {id: 5, numero: 105,
"Doble"});
CREATE (:Habitacion {id: 6, numero: 106,
tipo:
tipo:
tipo:
tipo:
tipo:
tipo:
"Suite"});
CREATE (:Habitacion {id: 7, numero:
"Individual"});
CREATE (:Habitacion {id: 8, numero:
"Doble"});
CREATE (:Habitacion {id: 9, numero:
"Suite"});
CREATE (:Habitacion {id: 10, numero:
"Doble"});
107,
tipo:
108,
tipo:
109,
tipo:
110, tipo:
Creación de servicios.
CREATE (:Servicio {id: 1, nombre: "Restaurante", precio:
15});
CREATE (:Servicio {id: 2, nombre: "Piscina", precio:
5});
CREATE (:Servicio {id: 3, nombre: "Spa", precio: 25});
CREATE (:Servicio {id: 4, nombre: "Gimnasio", precio:
10});
CREATE (:Servicio {id: 5, nombre: "Parking", precio:
8});
CREATE (:Servicio {id: 6, nombre: "Transporte",
precio:
12});
CREATE (:Servicio {id: 7, nombre: "WiFi Premium",
precio:
3});
CREATE (:Servicio {id: 8, nombre: "Canguro", precio:
20});
CREATE (:Servicio {id: 9, nombre: "Excursión", precio:
30});
CREATE (:Servicio {id: 10, nombre: "Alquiler
Bicicleta", precio: 7});
Creación de Pagos.
CREATE (:Pagos {id: 1, monto: 100, metodo: "Tarjeta"});
CREATE (:Pagos {id: 2, monto: 200, metodo:
"Efectivo"});
CREATE (:Pagos {id: 3, monto: 150, metodo:
"Transferencia"});
CREATE (:Pagos {id: 4, monto: 120, metodo:
"Tarjeta"});
CREATE (:Pagos {id: 5, monto: 250, metodo:
"Efectivo"});
CREATE (:Pagos {id: 6, monto: 180, metodo:
"Tarjeta"});
CREATE (:Pagos {id: 7, monto: 90, metodo:
"Transferencia"});
CREATE (:Pagos {id: 8, monto: 300, metodo:
"Efectivo"});
CREATE (:Pagos {id: 9, monto: 50, metodo: "Tarjeta"});
CREATE (:Pagos {id: 10, monto: 75, metodo:
"Efectivo"});
```
- Creamos las relaciones entre los nodos que hemos creado antes.
Cliente reserva Habitación.
MATCH
(c:Cliente
CREATE
MATCH (c:Cliente
CREATE

{id:1}),

(h:Habitacion
{id:1})
(c)-[:Reserva]->(h);

{id:2}),

(h:Habitacion {id:3})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:3}),

(h:Habitacion {id:4})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:4}),

(h:Habitacion {id:2})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:5}),

(h:Habitacion {id:6})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:6}),

(h:Habitacion {id:8})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:7}),

(h:Habitacion {id:5})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:8}),

(h:Habitacion {id:7})
(c)-[:Reserva]->(h);

MATCH (c:Cliente
CREATE

{id:9}),

(h:Habitacion {id:9})
(c)-[:Reserva]->(h);

MATCH (c:Cliente {id:10}), (h:Habitacion {id:10})
```bash
CREATE (c)-[:Reserva]->(h);
Cliente utiliza Servicio.
MATCH
(c:Cliente
CREATE
{id:1}),
(s:Servicio
{id:1})
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:2}),
(s:Servicio
{id:4})
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:3}),
(s:Servicio
{id:5})
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:4}),
(s:Servicio
{id:2})
(c)-[:USA]->(s);
MATCH
(c:Cliente
{id:5}),
(s:Servicio
{id:3})
CREATE
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:6}),
(s:Servicio
{id:8})
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:7}),
(s:Servicio
{id:6})
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:8}),
(s:Servicio
{id:7})
(c)-[:USA]->(s);
MATCH
CREATE
(c:Cliente
{id:9}),
(s:Servicio
{id:9})
(c)-[:USA]->(s);
MATCH (c:Cliente {id:10}),
CREATE (c)-[:USA]->(s);
(s:Servicio
{id:10})
Cliente realiza Pago.
MATCH
(c:Cliente
CREATE
{id:1}),
(p:Pagos
{id:1})
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:2}),
(p:Pagos
{id:2})
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:3}),
(p:Pagos
{id:3})
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:4}),
(p:Pagos
{id:4})
(c)-[:PAGA]->(p);
MATCH
(c:Cliente
{id:5}),
(p:Pagos
{id:5})
CREATE
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:6}),
(p:Pagos
{id:6})
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:7}),
(p:Pagos
{id:7})
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:8}),
(p:Pagos
{id:8})
(c)-[:PAGA]->(p);
MATCH
CREATE
(c:Cliente
{id:9}),
(p:Pagos
{id:9})
(c)-[:PAGA]->(p);
MATCH
(c:Cliente
{id:10}),
CREATE (c)-[:PAGA]->(p);
(p:Pagos
{id:10})
```

### 6.Pruebas del funcionamiento básico de Neo4j.
- Obtener todos los nodos de un tipo. En mi caso, voy a obtener todos los nodos
de Cliente y todos los nodos de Servicio.
MATCH
RETURN c;

(c:Cliente)

MATCH
RETURN s;

(s:Servicio)

- Obtener un nodo concreto. En mi caso voy a obtener el Cliente con id 1, y las
habitaciones de tipo individual ordenados descendentemente por el número de
habitación. Además, también voy a obtener los pagos de 90€ que se hayan
realizado por transferencia.
MATCH
RETURN c;

(c:Cliente

{id:1}

MATCH
(h:Habitacion
RETURN h
ORDER BY h.numero DESC;

{tipo:'Individual'})

MATCH (p:Pagos {monto: 90, metodo:'Transferencia'})
RETURN p;

- Contar cuántos nodos Habitación hay que sean de tipo Suite.
MATCH
(h:Habitacion
{tipo:'Suite'})
RETURN COUNT(h) AS habitaciones_suite;

- Mostrar todas las relaciones de un nodo. En mi caso, voy a realizar la siguiente
consulta de ejemplo: Mostrar las habitaciones que ha reservado el cliente cuyo
nombre es Jorge y cuyo primer apellido es Santos.
MATCH (c:Cliente {nombre:"Jorge", apellido1:"Santos"})[r]->(h:Habitacion)
RETURN c.nombre, c.apellido1, r, h.numero, h.tipo;

- Obtener las habitaciones que ha reservado y los servicios que ha utilizado la
clienta Marta Lopez Gil.
MATCH (c:Cliente {nombre:"Marta", apellido1:"Lopez",
apellido2:"Gil"})-[r]->(h:Habitacion),
(c)-[u]->(s:Servicio)
RETURN
c.nombre,
c.apellido1,
c.apellido2,
r,
h.numero, h.tipo, u, s.nombre, s.precio;

- Obtener el número de servicios que ha utilizado cada cliente.
MATCH
(c:Cliente)-[u]->(s:Servicio)
RETURN
c.nombre,
c.apellido1,
c.apellido2,
u,
COUNT(s) AS Total_Servicios;

- Obtener los clientes que realizaron pagos mayores a 100.
MATCH
(c:Cliente)-[:PAGA]->(p:Pagos)
WHERE
p.monto
>
RETURN c.nombre, c.apellido1, c.apellido2, p.monto;

- Modificar el precio del servicio Spa de 25€ a 20€.
MATCH
(s:Servicio
{nombre:
SET
s.precio
=
RETURN s.id, s.nombre, s.precio;

"Spa"})

- Agregar una nueva relación entre Cliente y Habitación.
MATCH
(c:Cliente
{id:2}),
(h:Habitacion
{id:2})
```bash
CREATE (c)-[:Reserva {fecha_entrada: date("2025-1010"), fecha_salida:date("2025-10-15")}]->(h);
```
- Borrar un nodo junto con sus relaciones.
MATCH
DETACH DELETE p;

(p:Pagos

{id:1})

- Listar los clientes ordenados por número de reservas.
MATCH

(c:Cliente)-[:Reserva]->(h:Habitacion)

RETURN c.nombre, COUNT(h)
ORDER BY Total_Reservas DESC;

AS

Total_Reservas

- Sumar todos los pagos de un cliente.
MATCH
(c:Cliente
{id:3})-[:PAGA]->(p:Pagos)
RETURN
c.nombre,
c.apellido1,
c.apellido2,
SUM(p.monto) AS total_pagado;

## Instalación Servidor Redis en Debian 13

### 1.Dependencias y configuración previa
- En primer lugar usaremos apt para instalar las dependencias necesarias para
Redis
```bash
serjaii@db:~$ sudo apt update
```
- Para añadir el repositorio de Redis a nuestra máquina será necesaria una clave
GPG.
```bash
serjaii@db:~$ curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archivekeyring.gpg && sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
```
- Ahora si podemos añadir el repositorio de Redis y realizar un apt update
```bash
serjaii@db:~$ echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list && sudo apt update
```

### 2.Instalación del servidor
- Instalamos el servidor Redis
```bash
serjaii@db:~$ sudo apt install redis
```
- Iniciamos el servicio de Redis con systemctl
```bash
serjaii@db:~$ sudo systemctl enable redis-server
serjaii@db:~$ sudo systemctl start redis-server
```
- Comprobamos que podemos acceder al servidor y ejecutar instrucciones sobre
él

```bash
serjaii@db:~$ redis-cli
```

### 3.Configuración del servidor Redis para acceso remoto
- Por defecto Redis escucha sólo en localhost. Por lo tanto, vamos a modificar en
el fichero “/etc/redis/redis.conf” en el que buscaremos comentar la linea “bind
127.0.0.1 -::1 la cual hará que se acepten conexiones externas” y la cambiamos
```bash
serjaii@db:~$ sudo nano /etc/redis/redis.conf
```
- De igual forma la linea protected-mode la vamos a deshabilitar y a su vez
añadiremos una password para el acceso remoto

### 4.Configuración del cliente Redis-cli para acceso remoto
- En primer lugar actualizamos los paquetes del sistema

serjaii ~ 10:57 : sudo apt update
Obj:1 https://apt.releases.hashicorp.com trixie InRelease
Obj:2 http://deb.debian.org/debian trixie InRelease
Obj:3 http://security.debian.org/debian-security trixiesecurity InRelease
Obj:4 http://deb.debian.org/debian trixie-updates InRelease
Obj:5 https://dl.google.com/linux/chrome/deb stable
InRelease
Obj:6 https://packages.microsoft.com/repos/code stable
InRelease
Todos los paquetes están actualizados.

- E instalamos el paquete de redis-tools el cual incluye el cliente redis
serjaii ~ 10:57 sudo apt install redis-tools

- Comprobamos que podemos acceder remotamente

serjaii ~ 10:57 redis-cli -h bd -p 6379 -a clienteredis

### 5.Creación de usuario,base de datos e inserción de datos
- Ingresamos a la base de datos y creamos el usuario
serjaii ~ 18:37 redis
bd:6379> ACL SETUSER serjaii on >serjaii ~* +@all
OK
bd:6379>

- Accedemos con el nuevo usuario
serjaii ~ 19:01 redis-cli -h bd -p 6379 -a serjaii --user serjaii
Warning: Using a password with '-a' or '-u' option on the
command line interface may not be safe.
bd:6379>
- Redis no trabaja con bases de datos ni tablas sino grafos y nodos,crearemos un
grafo de ejemplo e insertaremos datos
-Clientes:
HSET cliente:1 id 1 nombre "David" apellido1 "Dorado"
apellido2 "Lopez" email "davidd@gmail.com" telefono

"600111222"
HSET cliente:2 id 2 nombre "Maria" apellido1 "Dorado"
apellido2 "Lopez" email "maria@gmail.com" telefono
"600333444"
HSET cliente:3 id 3 nombre "Jorge" apellido1 "Santos"
apellido2 "Diaz" email "jorgesantos@gmail.com" telefono
"600555666"
HSET cliente:4 id 4 nombre "Lucia" apellido1 "Romero"
apellido2 "Garcia" email "luciarom@yahoot.es" telefono
"600777888"
HSET cliente:5 id 5 nombre "Pablo" apellido1 "Ruiz"
apellido2 "Torres" email "pablo@gmail.com" telefono
"600999000"
HSET cliente:6 id 6 nombre "Sofia" apellido1 "Martinez"
apellido2 "Leon" email "sofleon@yahoot.es" telefono
"601111222"
HSET cliente:7 id 7 nombre "Roberto" apellido1 "Navas"
apellido2 "Cruz" email "albertonavas@yahoot.es" telefono
"601333444"
HSET cliente:8 id 8 nombre "Marta" apellido1 "Lopez"
apellido2 "Gil" email "marta@gmail.com" telefono
"601555666"
HSET cliente:9 id 9 nombre "Raul" apellido1 "Castro"
apellido2 "Vega" email "raulcastro@gmail.com" telefono
"601777888"
HSET cliente:10 id 10 nombre "Laura" apellido1 "Morales"
apellido2 "Cano" email "laura@gmail.com" telefono
"601999000"

-Habitacion:
HSET habitacion:1 id 1 numero 101 tipo "Individual"

HSET habitacion:2 id 2 numero 102 tipo "Doble"
HSET habitacion:3 id 3 numero 103 tipo "Suite"
HSET habitacion:4 id 4 numero 104 tipo "Individual"
HSET habitacion:5 id 5 numero 105 tipo "Doble"
HSET habitacion:6 id 6 numero 106 tipo "Suite"
HSET habitacion:7 id 7 numero 107 tipo "Individual"
HSET habitacion:8 id 8 numero 108 tipo "Doble"
HSET habitacion:9 id 9 numero 109 tipo "Suite"
HSET habitacion:10 id 10 numero 110 tipo "Doble"

-Servicio
HSET servicio:1 id 1 nombre "Restaurante" precio 15
HSET servicio:2 id 2 nombre "Piscina" precio 5
HSET servicio:3 id 3 nombre "Spa" precio 25
HSET servicio:4 id 4 nombre "Gimnasio" precio 10
HSET servicio:5 id 5 nombre "Parking" precio 8

HSET servicio:6 id 6 nombre "Transporte" precio 12
HSET servicio:7 id 7 nombre "WiFi Premium" precio 3
HSET servicio:8 id 8 nombre "Canguro" precio 20
HSET servicio:9 id 9 nombre "Excursión" precio 30
HSET servicio:10 id 10 nombre "Alquiler Bicicleta" precio 7

-Pago:
HSET pago:1 id 1 monto 100 metodo "Tarjeta"
HSET pago:2 id 2 monto 200 metodo "Efectivo"
HSET pago:3 id 3 monto 150 metodo "Transferencia"
HSET pago:4 id 4 monto 120 metodo "Tarjeta"
HSET pago:5 id 5 monto 250 metodo "Efectivo"
HSET pago:6 id 6 monto 180 metodo "Tarjeta"
HSET pago:7 id 7 monto 90 metodo "Transferencia"
HSET pago:8 id 8 monto 300 metodo "Efectivo"
HSET pago:9 id 9 monto 50 metodo "Tarjeta"

HSET pago:10 id 10 monto 75 metodo "Efectivo"

### 6.Pruebas de funcionamiento
- Listar todas las claves creadas
bd:6379> KEYS *

- Comprobar un cliente
bd:6379> HGETALL cliente:4

- Buscar por campo
bd:6379> SCAN 0 MATCH cliente:* COUNT 100

## Instalación Servidor Cassandra en Debian 13

### 1.Dependencias y configuración previa
- Como siempre, comenzamos actualizando los repositorios del sistema:
```bash
sudo apt update
sudo apt upgrade -y
```
- Instalar Java 11
  - Cassandra 4.1.5 requiere Java 11. Como Debian Trixie no lo tiene en sus
repositorios oficiales, lo instalaremos desde Adoptium:
- Instalamos las dependencias necesarias
```bash
sudo apt install -y wget apt-transport-https gpg
```
- Añadir la clave GPG del repositorio de Adoptium
```bash
wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public
| sudo gpg --dearmor -o /usr/share/keyrings/adoptium.gpg
```
- Añadir el repositorio
echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg]
https://packages.adoptium.net/artifactory/deb bookworm main" | sudo
tee /etc/apt/sources.list.d/adoptium.list

- Actualizar e instalar Java 11
```bash
sudo apt update
sudo apt install -y temurin-11-jdk
```
- Verificar instalación
java -version

```bash
serjaii@db:~$ java -version openjdk version "11.0.28" 2025-07-15 OpenJDK Runtime Environment Temurin-11.0.28+6 (build 11.0.28+6) OpenJDK 64-Bit Server VM Temurin-11.0.28+6 (build 11.0.28+6, mixed mode)
```
- Instalar dependencias adicionales
  - Necesitamos herramientas para compilar drivers de Python:
```bash
sudo apt install -y python3-pip python3-dev python3-six buildessential libev-dev libssl-dev libffi-dev unzip zip wget
```
- Explicación:
  - python3-pip → Gestor de paquetes de Python
  - python3-dev → Archivos de desarrollo de Python
  - python3-six → Librería de compatibilidad Python 2/3
  - build-essential → Herramientas de compilación (gcc, make)
  - libev-dev → Librería para event loops
  - unzip/zip → Para manipular archivos comprimidos

### 2.Instalación del servidor
- Descargamos Cassandra desde el archivo oficial de Apache y lo extraemos
en /opt/cassandra para tener una instalación limpia y organizada.

- Entramos al directorio /opt
cd /opt
- Descargar Cassandra 4.1.5
```bash
sudo wget https://archive.apache.org/dist/cassandra/4.1.5/apachecassandra-4.1.5-bin.tar.gz
```
- Extraer el archivo
```bash
sudo tar -xzf apache-cassandra-4.1.5-bin.tar.gz
```
- Renombrar para facilitar el acceso
```bash
sudo mv apache-cassandra-4.1.5 cassandra
```
- Eliminar el archivo comprimido

```bash
sudo rm apache-cassandra-4.1.5-bin.tar.gz
```
- Crear usuario para Cassandra
  - Por seguridad, Cassandra no debe ejecutarse como root:
```bash
sudo useradd -r -s /bin/false cassandra
sudo chown -R cassandra:cassandra /opt/cassandra
```
- Explicación:
  - -r → Crea un usuario del sistema (sin directorio home)
  - -s /bin/false → Sin shell de login (más seguro)

Configurar Cassandra como servicio systemd
- Creamos un servicio para que Cassandra se inicie automáticamente:
```bash
sudo nano /etc/systemd/system/cassandra.service
```
- Tenemos que añadir lo siguiente
[Unit]
Description=Apache Cassandra
After=network.target
[Service]
Type=forking
User=cassandra
Group=cassandra
ExecStart=/opt/cassandra/bin/cassandra -p
/opt/cassandra/cassandra.pid
ExecStop=/bin/kill -TERM $MAINPID
Environment=JAVA_HOME=/usr/lib/jvm/temurin-11-jdk-amd64

Restart=always
LimitNOFILE=100000
[Install]
WantedBy=multi-user.target

- Explicación de las opciones:
- Type=forking → Cassandra se ejecuta en segundo plano
- User=cassandra → Se ejecuta con el usuario cassandra
- Environment=JAVA_HOME → Define dónde está Java instalado
- LimitNOFILE=100000 → Aumenta el límite de archivos abiertos
(necesario para Cassandra)
Iniciar Cassandra
- Recargar systemd
```bash
sudo systemctl daemon-reload
```
- Habilitar inicio automático
```bash
sudo systemctl enable cassandra
```
- Iniciar Cassandra
```bash
sudo systemctl start cassandra
```
- Verificar estado
```bash
sudo systemctl status cassandra
```
- Ahora esperamos unos 30 segundos para que se inicie todo bien y
comprobamos que esté escuchando en localhost:
```bash
sudo ss -tulpn | grep 9042
```
- Nos debería salir algo como lo siguiente
```bash
serjaii@db:~$ sudo ss -tulpn | grep 9042 tcp LISTEN 0 127.0.0.1:9042 0.0.0.0:* users:(("java",pid=3393,fd=154)) Instalar y configurar cqlsh (Cliente de Cassandra)
```
- Instalar drivers de Python
- Instalar el driver de Cassandra desde código fuente

pip3 install --user --break-system-packages --no-cache-dir --nobinary :all: cassandra-driver
- Instalar eventlet y futurist (necesarios para Python 3.13)
pip3 install --user --break-system-packages eventlet futurist
- Python 3.13 eliminó el módulo asyncore, por lo que necesitamos usar eventlet
como reactor de eventos alternativo.
Configurar el driver para Python 3.13
- El driver de Cassandra no es compatible con Python 3.13 por defecto.
Necesitamos modificarlo:
```bash
# Modificar cluster.py automáticamente
python3 << 'EOF'
import re
site_packages = __import__('site').USER_SITE
cluster_file = f"{site_packages}/cassandra/cluster.py"
with open(cluster_file, 'r') as f:
content = f.read()
# Buscar y reemplazar el bloque problemático
pattern = r'if not conn_class:.*?raise DependencyException\([^)]+
\)'
replacement = '''if not conn_class:
from cassandra.io.eventletreactor import EventletConnection
default_connection_class = EventletConnection
conn_class = EventletConnection
DefaultConnection = conn_class'''
content_modified = re.sub(pattern, replacement, content,
flags=re.DOTALL)
with open(cluster_file, 'w') as f:
f.write(content_modified)
print("✓ cluster.py modificado correctamente")
EOF
```
- Este script modifica el driver para usar Eventlet en lugar de libev o asyncore.
Solucionar problema del driver interno de Cassandra
- El driver interno que viene con Cassandra (en formato ZIP) no puede encontrar
el módulo six. Vamos a extraerlo e insertar six:
cd /opt/cassandra/lib
- Hacer backup del ZIP original
```bash
sudo cp cassandra-driver-internal-only-3.25.0.zip cassandradriver-internal-only-3.25.0.zip.backup
```
- Extraer el ZIP permanentemente
```bash
sudo unzip -q cassandra-driver-internal-only-3.25.0.zip
```
- Copiar el módulo six desde el sistema
```bash
sudo cp /usr/lib/python3/dist-packages/six.py cassandradriver-3.25.0/
```
- Copiar también la metadata de six
```bash
sudo cp -r /usr/lib/python3/dist-packages/six-*.dist-info cassandradriver-3.25.0/ 2>/dev/null || true
```
- IMPORTANTE: Eliminar el ZIP para que Python use el directorio extraído
```bash
sudo rm -f cassandra-driver-internal-only-3.25.0.zip
```
- Ajustar permisos
```bash
sudo chown -R cassandra:cassandra cassandra-driver-3.25.0
```
- El driver empaquetado en ZIP no puede importar módulos externos. Al
extraerlo y copiar six.py dentro, solucionamos el problema.
Crear wrapper para cqlsh
```bash
sudo nano /usr/local/bin/cqlsh
```
- tenemos que pegar el siguiente contenido
#!/bin/bash
export
PYTHONPATH=/usr/lib/python3/dist-packages:$HOME/.local/lib/python
3.13/site-packages
exec /opt/cassandra/bin/cqlsh "$@"

- Lo guardamos y lo hacemos ejecutable con lo siguiente
```bash
sudo chmod +x /usr/local/bin/cqlsh
```
- Este wrapper configura el PYTHONPATH correctamente para que cqlsh
encuentre todas las librerías necesarias.
Configurar variables de entorno
echo '' >> ~/.bashrc
echo '# Cassandra configuración' >> ~/.bashrc
echo 'export CASSANDRA_HOME=/opt/cassandra' >> ~/.bashrc
echo 'export PATH=$PATH:$CASSANDRA_HOME/bin' >>
~/.bashrc
- Aplicamos los cambios
source ~/.bashrc
- Ya podríamos entrar al servidor localmente ejecutando :
cqlsh

### 3.Configuración del servidor Cassandra para acceso remoto
- Primero tenemos que ver la ip de nuestro servidor , simplemente con un ip a y
quedarnos con la ip
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu
1500 qdisc fq_codel state UP group default qlen 1000
link/ether 52:54:00:c1:44:60 brd ff:ff:ff:ff:ff:ff
altname enx525400c14460
inet 192.168.122.161/24 brd 192.168.122.255 scope global
- Tenemos que editar el siguiente fichero

```bash
serjaii@db:~$ sudo nano /opt/cassandra/conf/cassandra.yaml
```
- y cambiar lo siguientes parámetros de localhost a la ip de nuestro servidor

- Esa línea está por defecto comentada la descomentamos y ponemos también la
ip del servidor

Es importante que en este caso no podemos usar 0.0.0.0 ya que cassandra no lo
permite tenemos que poner siempre la ip de nuestro servidor
Ya con todo eso modificamos guardamos y salimos del fichero
- Reiniciamos cassandra
```bash
sudo systemctl restart cassandra
```
- Esperamos unos segundos y verificamos que está escuchando
```bash
sudo ss -tulpn | grep 9042
```
- Podemos ver que la ip ha cambiado ahora esta la ip de nuestro servidor en vez
de localhost que es la 127.0.0.1
```bash
serjaii@db:~$ sudo ss -tulpn | grep 9042 tcp LISTEN 0 192.168.122.161:9042 0.0.0.0:* users:(("java",pid =4057,fd=159))
```

### 4.Configuración del cliente Cassandra para acceso remoto
- Actualizar el sistema cliente
```bash
sudo apt update
```
- Instalar cqlsh en el cliente
pip3 install --user --break-system-packages cqlsh
- Instalar dependencias necesarias
pip3 install --user --break-system-packages eventlet futurist
- Configurar el driver en el cliente es igual que lo que hemos hecho en el
servidor

python3 << 'EOF'
import re
site_packages = __import__('site').USER_SITE
cluster_file = f"{site_packages}/cassandra/cluster.py"
with open(cluster_file, 'r') as f:
content = f.read()
pattern = r'if not conn_class:.*?raise DependencyException\([^)]+
\)'
replacement = '''if not conn_class:
from cassandra.io.eventletreactor import EventletConnection
default_connection_class = EventletConnection
conn_class = EventletConnection
DefaultConnection = conn_class'''

content_modified = re.sub(pattern, replacement, content,
flags=re.DOTALL)
with open(cluster_file, 'w') as f:
f.write(content_modified)
print("✓ cluster.py modificado correctamente")
EOF
- Añadir cqlsh al PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
- Aplicamos los cambios
source ~/.bashrc
- Ya podemos conectarnos desde el cliente al servidor
cqlsh 192.168.122.161

### 5.Funcionamiento básico de Cassandra
-Conceptos fundamentales
- ¿Qué es un Keyspace?
  - Un keyspace en Cassandra es equivalente a una base de datos en SQL.
Contiene las tablas y define la estrategia de replicación de datos.
- ¿Qué es la replicación?
  - Cassandra distribuye copias de los datos en múltiples nodos para
garantizar disponibilidad y tolerancia a fallos.
-Gestión de usuario en Cassandra

- Por defecto, Cassandra NO requiere usuario/contraseña. Para habilitarla:
```bash
sudo nano /opt/cassandra/conf/cassandra.yaml
Tenemos que cambiar las siguientes líneas
```
Reiniciamos el sistema y comprobamos desde remoto con usuario y contraseña

Para crear usuario con permisos de root usamos lo siguiente
Para ver los usuarios que tenemos creados

También podemos cambiar la contraseña por defecto de cassandra o cualquier usuario
con :

- Dar los permisos de esta tabla a un usuario especifico

- Podemos ver también los permisos que tiene el usuario que queramos y sobre
qué base de datos tiene permisos

- Si queremos darle un permisos específico sobre una base de datos a un usuario
lo hacemos de la siguiente forma
```bash
GRANT SELECT ON KEYSPACE (base de datos) TO (usuario);
```
- Ahora si listamos los permisos podemos ver que se le han aplicado permisos de
lectura al usuario bibliotecario sobre tienda

- Tipos de permisos
  - CREATE →Crear nuevas tablas, tipos, índices
  - ALTER → Modificar estructura de tablas
  - DROP → Eliminar tablas, tipos
  - SELECT → Leer datos (consultas)
  - MODIFY → Insertar, actualizar, eliminar datos
  - AUTHORIZE → Dar/quitar permisos a otros usuarios
  - ALL →Todos los permisos anteriores

- Quitar un permiso específico
REVOKE SELECT ON KEYSPACE biblioteca FROM usuario;
- Quitar múltiples permisos
REVOKE SELECT, MODIFY ON KEYSPACE biblioteca FROM
usuario;
- Quitar todos los permisos
REVOKE ALL PERMISSIONS ON KEYSPACE biblioteca FROM
usuario;
- Quitar permisos sobre tabla específica
REVOKE SELECT ON biblioteca.libros FROM usuario;
- Para eliminar usuarios

DROP USER usuario;

-Gestión de Keyspaces
- Crear un keyspace
Keyspace simple (un solo datacenter, para desarrollo)

```bash
CREATE KEYSPACE biblioteca
WITH replication = {
'class': 'SimpleStrategy',
'replication_factor': 1
};
```
- Explicación:
  - SimpleStrategy: Para un solo datacenter
  - replication_factor: 1: Mantiene 1 copia de los datos (sin redundancia)

- Crear keyspace con replicación (producción)
Keyspace con 3 réplicas (recomendado para producción)
```bash
CREATE KEYSPACE produccion
WITH replication = {
'class': 'SimpleStrategy',
'replication_factor': 3
};
```
- Explicación:
  - Con 3 réplicas, los datos se copian en 3 nodos
  - Si un nodo falla, los otros 2 siguen sirviendo datos

- Crear keyspace multi-datacenter
Para clusters en múltiples datacenters
```bash
CREATE KEYSPACE global_app
WITH replication = {
'class': 'NetworkTopologyStrategy',
'datacenter1': 3,
'datacenter2': 2
};
```
- Explicación:
  - NetworkTopologyStrategy: Para múltiples datacenters
  - 3 réplicas en datacenter1, 2 en datacenter2

- Ver keyspaces existentes
DESCRIBE KEYSPACES;

- Ver información de un keyspace específico
DESCRIBE KEYSPACE biblioteca;

- Usar un keyspace
USE biblioteca;

- Cambiar factor de replicación de un KEYSPACE
```bash
ALTER KEYSPACE biblioteca
WITH replication = {
'class': 'SimpleStrategy',
'replication_factor': 3
};
```
- Eliminar un KEYSPACE y todas sus tablas
DROP KEYSPACE biblioteca;

-Gestión de tablas en Cassandra
- Seleccionamos el KEYSPACE que queremos usar

- Creamos las tablas e introducimos los datos

- Creación de tabla autores
```bash
CREATE TABLE autores (
id_autor int PRIMARY KEY,
nombre text,
nacionalidad text
);
```
- Introducir datos
```bash
INSERT INTO autores (id_autor, nombre, nacionalidad) VALUES (1,
'Homero', 'Griega');
INSERT INTO autores (id_autor, nombre, nacionalidad) VALUES (2,
'Gabriel García Márquez', 'Colombiana');
INSERT INTO autores (id_autor, nombre, nacionalidad) VALUES (3,
'Miguel de Cervantes', 'Española');
```
- Creación de tabla libros
```bash
CREATE TABLE libros (
isbn text PRIMARY KEY,
titulo text,
id_autor int,
anio int,
categoria text
);
```
- Introducir datos

```bash
INSERT INTO libros (isbn, titulo, id_autor, anio, categoria) VALUES
('9780140449136', 'La Odisea', 1, -700, 'Clásico');
INSERT INTO libros (isbn, titulo, id_autor, anio, categoria) VALUES
('9788499890944', 'Cien años de soledad', 2, 1967, 'Novela');
INSERT INTO libros (isbn, titulo, id_autor, anio, categoria) VALUES
('9788437604947', 'Don Quijote de la Mancha', 3, 1605, 'Clásico');
```
- Creación de tabla prestamos
```bash
CREATE TABLE prestamos (
id_usuario int,
fecha_prestamo timestamp,
isbn text,
fecha_devolucion timestamp,
PRIMARY KEY (id_usuario, fecha_prestamo)
) WITH CLUSTERING ORDER BY (fecha_prestamo DESC);
```
- Introducir datos
```bash
INSERT INTO prestamos (id_usuario, fecha_prestamo, isbn,
fecha_devolucion) VALUES (1, toTimestamp(now()), '9780140449136',
null);
INSERT INTO prestamos (id_usuario, fecha_prestamo, isbn,
fecha_devolucion) VALUES (2, toTimestamp(now()), '9788499890944',
'2025-10-10T00:00:00Z');
INSERT INTO prestamos (id_usuario, fecha_prestamo, isbn,
fecha_devolucion) VALUES (3, toTimestamp(now()), '9788437604947',
null);
```
- Para eliminar todos los datos de una tabla lo hacemos con TRUNCATE
TRUNCATE autores;

Ver información de las tablas
- En Cassandra se pueden consultar los datos de una tabla utilizando sentencias
SELECT, de manera similar a otros sistemas de gestión de bases de datos. No
obstante, a diferencia de los sistemas relacionales, Cassandra no admite
operaciones JOIN ni relaciones entre tablas, ya que su modelo de datos está

desnormalizado y orientado a las consultas. Por este motivo, cada tabla se
diseña específicamente para responder a un tipo de consulta determinado, sin
depender de otras tablas.

## Aplicación Web que conecte con el servidor
MySQL y comprobación de las vulnerabilidad
a SQL Injection.
En este enlace se encuentra mi trabajo sobre el servidor web conectado a MySQL al
igual que la comprobación a la vulnerabilidad SQL Injection

## Aplicación Web que conecte con el servidor
MongoDB
En el siguiente enlace esta el codigo de la aplicación web de MongoDB : enlace

## Aplicación Web que conecte con el servidor
PostgreSQL tras autenticarse.
Este es el enlace de GitHub donde tengo subida mi aplicación web:
https://github.com/ddorluc760/aplicacionWebHotel.git
Dentro del directorio “server”, tengo el fichero .sql, con las consultas de creación de
tablas e inserción de datos que he usado para mi aplicación Web.

SQL Injection sobre Aplicación Web en
PostgreSQL.
Un ataque SQL Injection ocurre cuando un atacante puede insertar o manipular
consultas SQL a través de entradas no validadas, lo que puede llevar a la exposición
de datos sensibles o incluso a la manipulación de la base de datos

### 1.Cambios realizados sobre mi aplicación web para hacerla
vulnerable.
Para la práctica he introducido cambios deliberados en “/server/server.js” para que la
comprobación de login sea vulnerable a SQL Injection en un entorno de laboratorio
controlado. Concretamente, en la ruta “/login” he sustituido la consulta parametrizada
por una construcción por concatenación:

He realizado la misma acción en las rutas “/menu/tablaHabitaciones”,
“/menu/tablaReservas”,
“/menu/tablaPagos”,
“/menu/tablaClientes”
y
“/menu/tablaUsuarios”:

Al concatenar valores procedentes del cliente (usuario, password) directamente en la
cadena SQL, los valores dejan de ser únicamente datos y pueden pasar a formar parte
de la estructura de la sentencia SQL. Esto permite que entradas especialmente
formateadas influyan sobre la sintaxis y la lógica de la consulta, es decir, que un
atacante pueda alterar la consulta original. Este comportamiento es conocido como
SQL Injection.
Esto provoca que la entrada del cliente deje de ser tratada solo como datos y pase a
formar parte de la estructura de la sentencia SQL, lo que permite manipular la
consulta si se introducen contenidos especiales en los campos.
Para que la inyección de errores y la inyección de funciones funcionen, es decir, que
mi página web también sea vulnerable a estos ataques, voy a realizar las siguientes
modificaciones en el catch, en dónde además de devolver el mensaje del error,
también devolverá el detalle del error.

### 2.Tipos de ataques SQL Injection sobre mi aplicación web.
Inyección Básica.
Intenta manipular la consulta SQL básica para obtener acceso no autorizado. En caso
de que la aplicación sea vulnerable, deberías poder iniciar sesión sin conocer la
contraseña real.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.

usuario: admin
password: ' OR '1'='1

Inyección de comentarios.
Utiliza comentarios SQL para ignorar el resto de la consulta, y permitiendo de este
modo el acceso. Para ello, necesitaremos un usuario existente solamente, ya que con
los parámetros ‘ --, vamos a ignorar la comprobación de la contraseña en la consulta
```bash
SELECT de nuestro login.
```
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.
usuario: usuarioVálido' -password: "cualquierContraseña"

Inyección de Unión (UNION Injection).
Combina resultados de otra consulta para obtener datos adicionales, como por
ejemplo, todos los usuarios y contraseñas.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.
usuario: admin' UNION SELECT null, usuario,password,null
FROM usuarios -password: [cualquiercontraseña]
Antes de pasar con la ejecución de la inyección SQL, vamos a abrir la herramienta
para desarrolladores, y en mi caso, voy a aplicar un punto de depuración antes de
cambiar de página, para ver si en la respuesta del login, nos muestra todos los usuarios
y sus contraseñas de la tabla usuarios.

Probamos a loguearnos, ejecutando la inyección SQL.

Nos vamos a “Red” o “Network” y pulsamos sobre la última respuesta del login. Tras
haber hecho esto, si todo se ha ejecutado correctamente, nos mostrará los datos que
hemos solicitado en el UNION.

Inyección de Tiempo (Time-Based Blind SQL Injection).
Usa una función como “pg_sleep” para confirmar la vulnerabilidad mediante retrasos
en la respuesta. En este caso, la respuesta tardará 5 segundos en llegar.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.

usuario: admin' || pg_sleep(5) -password: [cualquierContraseña]

Para verificar que esto funciona correctamente, voy a facilitar capturas en la cuál se
muestra un ejemplo en el que se intenta hacer un inicio de sesión con un usuario o
contraseña que no existen, y comprobaremos el tiempo que tarda en enviar la
respuesta el login.

Inyección de Cadenas.
Con este ataque SQL, se intenta manipular cadenas para forzar una condición
verdadera.

Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.
usuario: admin' OR 'a'='a' -contraseña: [cualquierContraseña]

Inyección de Subconsultas.
Usa subconsultas para obtener datos adicionales.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente. En este caso, en el caso de que cumpla con la subconsulta las
tablas, nos va a permitir loguearnos. Es decir, que en este ejemplo, en el caso de que la
tabla no tenga algún dato nos va a permitir loguearnos. En el caso de que no lo
tuviera, no nos va a permitir loguearnos.
usuario: admin' OR (SELECT COUNT(*) FROM usuarios) > 0 -password: [cualquierContraseña]

En el siguiente caso, no deberíamos de poder entrar, ya que la tabla Clientes tiene
datos.

usuario: admin' OR (SELECT COUNT(*) FROM usuarios) < 0 -password: [cualquierContraseña]

Inyección de Errores.
Provoca un error para obtener información sobre la base de datos. Si la aplicación es
vulnerable, deberíamos obtener un error que revele información sobre la base de
datos.

Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.
usuario: admin' AND 1=(CAST((SELECT string_agg(nombre || ':'
|| primerApellido || ':' || segundoApellido || ':' || telefono || ':' ||
email, ', ') FROM clientes) AS INT)) -password: [cualquierContraseña]

En la herramienta de desarrollador del navegador web, nos vamos a la opción Red, y
vemos como en la respuesta 500, que nos da el error “Error en la conexión a la base de
datos”, también nos proporciona detalles sobre la versión del servidor PostgreSQL.

Inyección de Datos.
Con esta inyección SQL, tratamos de intentar insertar datos en la base de datos.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.

usuario: admin' ; INSERT INTO usuarios (usuario, password)
VALUES ('hacker', '123'); -password: [cualquierContraseña]

Comprobamos que podemos acceder con el usuario y contraseña que hemos insertado.

Inyección de Funciones.
Usa funciones de PostgreSQL para obtener información.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.
usuario: admin' AND 1=(SELECT CAST(version() AS INT)) -contraseña: [cualquierContraseña]

En la herramienta de desarrollador del navegador web, nos vamos a la opción Red, y
vemos como en la respuesta 500, que nos da el error “Error en la conexión a la base de
datos”, también nos proporciona detalles sobre la versión del servidor PostgreSQL.

Inyección de Datos Sensibles

Intenta extraer datos sensibles con UNION.
Vamos a ponerlo en práctica. Para ello, en el formulario de inicio de sesión,
ingresamos en usuario lo siguiente, y en el caso de la contraseña introducimos
también lo siguiente.
usuario: admin' UNION SELECT 1, json_build_object( 'id', id,
'email', email, 'nombre_completo', nombre || ' ' || primerApellido ||
' ' || COALESCE(segundoApellido, ''), 'telefono', telefono)::text,
'CLIENTE', id FROM clientes -contraseña: [cualquierContraseña]
Antes de pasar con la ejecución de la inyección SQL, vamos a abrir la herramienta
para desarrolladores, y en mi caso, voy a aplicar un punto de depuración antes de
cambiar de página, para ver si en la respuesta del login, nos muestra todos los usuarios
y sus contraseñas de la tabla usuarios.

Probamos a loguearnos, ejecutando la inyección SQL.

Nos vamos a “Red” o “Network” y pulsamos sobre la última respuesta del login. Tras
haber hecho esto, si todo se ha ejecutado correctamente, nos mostrará los datos que
hemos solicitado en el UNION.

### 3.Cambios realizados para que mi aplicación no sea vulnerable.
Para eliminar la vulnerabilidad de tipo SQL Injection introducida en las consultas, he
realizado los siguientes cambios principales:

### 1. Reemplazar todas las consultas que concatenan directamente valores de entrada
por consultas parametrizadas usando placeholders ($1, $2, …) y pasando un
array de parámetros al driver “pg”.

### 2. Usar un usuario de aplicación (app user) con permisos mínimos en la base de
datos en lugar de una cuenta con privilegios amplios, usando para el login en
postgreSQL directamente el usuario y contraseña que pasamos parámetros en el
login.

### 3. Quitar “console.log” que imprime consultas con valores sensibles en entornos
de producción.
Quedando el “/server/server.js” con el siguiente contenido:

### 4.Comprobación de que mi aplicación no sea vulnerable.
Tras haber modificado las partes del código vulnerable de mi aplicación, para que mi
página web no sea vulnerable, no nos deberá funcionar las siguientes inyecciones
SQL.
Inyección Básica.
usuario: admin
password: ' OR '1'='1

Inyección de comentarios.
usuario: usuarioVálido' -password: "cualquierContraseña"

Inyección de Unión (UNION Injection).
usuario: admin' UNION SELECT null, usuario,password,null
FROM usuarios -password: [cualquiercontraseña]

Antes de pasar con la ejecución de la inyección SQL, vamos a abrir la herramienta
para desarrolladores, y en mi caso, voy a aplicar un punto de depuración antes de
cambiar de página, para ver si en la respuesta del login, nos muestra todos los usuarios
y sus contraseñas de la tabla usuarios.

Probamos a loguearnos, ejecutando la inyección SQL.

Nos vamos a “Red” o “Network” y pulsamos sobre la última respuesta del login. Tras
haber hecho esto, si todo se ha ejecutado correctamente, nos mostrará los datos que
hemos solicitado en el UNION.

Inyección de Tiempo (Time-Based Blind SQL Injection).
usuario: admin' || pg_sleep(5) -password: [cualquierContraseña]

Como vemos en la siguiente captura, no se ha retardado la respuesta de nuestra página
web.

Inyección de Cadenas.
usuario: admin' OR 'a'='a' -contraseña: [cualquierContraseña]

Inyección de Subconsultas.
usuario: admin' OR (SELECT COUNT(*) FROM usuarios) > 0 -password: [cualquierContraseña]

usuario: admin' OR (SELECT COUNT(*) FROM usuarios) < 0 -password: [cualquierContraseña]

Inyección de Errores.
usuario: admin' AND 1=(CAST((SELECT string_agg(nombre || ':'
|| primerApellido || ':' || segundoApellido || ':' || telefono || ':' ||
email, ', ') FROM clientes) AS INT)) -password: [cualquierContraseña]

Inyección de Datos.

usuario: admin' ; INSERT INTO usuarios (usuario, password)
VALUES ('aaa', 'bbb'); -password: [cualquierContraseña]

Comprobamos que no se haya insertado el usuario, no pudiendo loguearnos con el
usuario que hemos intentado insertar con la vulnerabilidad.

Inyección de Funciones.
usuario: admin' AND 1=(SELECT CAST(version() AS INT)) --

contraseña: [cualquierContraseña]

Inyección de Datos Sensibles

usuario: admin' UNION SELECT 1, json_build_object( 'id', id,
'email', email, 'nombre_completo', nombre || ' ' || primerApellido ||
' ' || COALESCE(segundoApellido, ''), 'telefono', telefono)::text,
'CLIENTE', id FROM clientes -contraseña: [cualquierContraseña]
Antes de pasar con la ejecución de la inyección SQL, vamos a abrir la herramienta
para desarrolladores, y en mi caso, voy a aplicar un punto de depuración antes de
cambiar de página, para ver si en la respuesta del login, nos muestra todos los usuarios
y sus contraseñas de la tabla usuarios.

Probamos a loguearnos, ejecutando la inyección SQL.

Nos vamos a “Red” o “Network” y pulsamos sobre la última respuesta del login. Tras
haber hecho esto, si todo se ha ejecutado correctamente, nos mostrará los datos que
hemos solicitado en el UNION. En este caso, no nos va a mostrar datos ya que mi
página no es vulnerable a este tipo de ataques.

## Instalación Servidor Memcached en Debian 13

### 1.Instalación de Paquetes
- En primer lugar, actualizamos los repositorios
```bash
serjaii@db:~$ sudo apt update
```
- Instalamos el servidor memcached con la biblioteca cliente y herramientas
```bash
serjaii@db:~$ sudo apt install memcached libmemcachedtools
```
- Comprobamos el estado del servicio

- Esto ocurre porque en versiones recientes de Memcached, no admite dos
directivas -l en el mismo archivo; eso causa exactamente el error
status=71.Editamos el fichero /etc/memcached.conf y comentamos la segunda
línea que hace referencia a -l
```bash
serjaii@db:~$ sudo nano /etc/memcached.conf
```
- Reiniciamos y omprobamos de nuevo el estado del servicio
```bash
serjaii@db:~$ sudo systemctl restart memcached && sudo systemctl status memcached
```

### 2.Memcached en un Servidor Web
Primero que nada debemos saber que es Memcached,ya que está no es en sí una base
de datos, podemos entenderla como un servicio que funciona de caché de la base de

datos cuando esta se conecta con una aplicación web. Para probar su funcionalidad
voy a implementarla en un Servidor Web que accede a una base de datos MySQL.

- Como estamos trabajando en un escenario demasiado pequeño como para notar
una diferencia cuando la información llega desde memcached o desde el propio
servidor de base de datos he añadido un aviso en el servidor web para poder
reconocerlo.
{% if cached %}
<div
style="background:#ffc107;color:#212529;padding:6px
10px;border-radius:6px;font-weight:600;">Servido desde
cache</div>
{% endif %}

### 3.Implementación en Flask
Partiendo del siguiente proyecto repasaré los pasos que he seguido para
implementar memcached en un servidor web,aunque bien hay que decir que este
proceso puede ser diferente dependiendo si se ha realizado con Flask o cualquier
otra aplicacion

En primer lugar empezaremos añadiendo al entorno virtual pymemcache==4.0.8
esto lo haremos en requirements.txt

El resto de cambios los haremos sobre el fichero app.py
- Importar librería

- Iniciar el cliente memcached

Instalación, uso básico y explicación del
funcionamiento de CouchDB en Debian 13
Apache CouchDB es una base de datos NoSQL orientada a documentos que almacena
documentos JSON, expone una API HTTP/REST y una vistas MapReduce y un
sistema de replicación eficiente. Está escrita en Erlang y usa un almacenamiento
append-only sobre B-trees, lo que facilita la tolerancia a fallos y lecturas concurrentes.
Fauxton es su interfaz web integrada para administración y pruebas.

### 1.Instalación de dependencias y servidor de CouchDB.
El repositorio oficial de CouchDB aún no tiene paquetes específicos para Debian 13,
ya que es una versión muy reciente. Por tanto, usaremos los paquetes de Debian 12

para la instalación de CouchDB de forma temporal, hasta que CouchDB publique
paquetes específicos para su instalación en Debian 13.
- Actualizamos los paquetes del sistema, asegurando que los paquetes y
metadatos APT estén actualizados y así evitar conflictos.
```bash
serjaii@db:~$ sudo apt update && sudo apt upgrade -y
```
- Instalamos las dependencias necesarias para la instalación de CouchDB, para
poder añadir repositorios HTTPS y gestionar claves GPG.
```bash
serjaii@db:~$ sudo apt install -y curl gnupg ca-certificates lsb-release apttransport-https - curl: para descargar la clave GPG. gnupg: para convertir la clave GPG a formato apt (dearmor). lsb-release: para obtener “VERSION_CODENAME”.
```
- Añadimos el repositorio oficial de CouchDB, donde se encuentran los paquetes
oficiales de CouchDB. Además, añadimos también su clave GPG para que apt
confíe en el repo. Para ello, en este paso, descargamos la clave y la guardamos
en formato apt (.gpg).
```bash
serjaii@db:~$ curl -fsSL https://couchdb.apache.org/repo/keys.asc | gpg --dearmor | sudo tee /usr/share/keyrings/couchdb-archive-keyring.gpg >/dev/null
```
- Añadimos la entrada al sources list.
```bash
serjaii@db:~$ echo "deb [signed-by=/usr/share/keyrings/couchdb-archivekeyring.gpg] https://apache.jfrog.io/artifactory/couchdb-deb/ bookworm main" | sudo tee /etc/apt/sources.list.d/couchdb.list
```
- Actualizamos los índices APT, para que el sistema reconozca la clave GPG.
```bash
serjaii@db:~$ sudo apt update
```
- Lanzamos la instalación de CouchDB.
```bash
serjaii@db:~$ sudo apt install couchdb
```
- Como vemos, nos ha salido dos errores típicos, debido a que está intentando
instalar CouchDB en Debian 12, usando dependencias que en Debian 13
pueden estar obsoletas. Para que podamos instalar CouchDB, tendremos que
descargarnos e instalar las dependencias “libicu72” y “libmozjs-78-0”
previamente, que son las dependencias que nos están fallando durante la
instalación de CouchDB.
```bash
serjaii@db:~$ wget http://ftp.debian.org/debian/pool/main/i/icu/libicu72_72.13+deb12u1_amd64.deb
serjaii@db:~$ wget http://ftp.debian.org/debian/pool/main/m/mozjs78/libmozjs-7 8-0_78.15.0-7_amd64.deb
serjaii@db:~$ sudo apt install ./libicu72_72.13+deb12u1_amd64.deb ./libmozjs-78-0_78.15.07_amd64.deb -
```
El ./ delante del nombre del archivo le dice a apt que instale desde un
archivo local, no desde los repositorios.
Esto también resolverá las dependencias automáticamente si falta algo
más.

- Volvemos a actualizar el sistema para actualizar la paquetería y ejecutamos el
comando para instalar “CouchDB”.
```bash
serjaii@db:~$ sudo apt update
serjaii@db:~$ sudo apt install couchdb
```
- Seleccionamos “Aceptar”.

- Seleccionamos la opción “Standalone”, ya que CouchDB funcionará en esta
máquina solamente. Además, es la opción habitual para pruebas y entornos
locales.

- Ponemos un valor de CouchDB Erlang magic cookie.

- En la siguiente página, como quiero que mi servidor escuche conexiones
remotas, voy a configurar para que la interfaz de CouchDB sea la interfaz
“0.0.0.0”.

- Añadimos una contraseña para el usuario admin, en mi caso “admin”.

- Volvemos a repetir la contraseña.

- Comprobamos que podemos acceder a CouchDB.
```bash
serjaii@db:~$ curl http://localhost:5984/
```

### 2. Configuración para conexión remota.
- Editamos la sección “[httpd]” en el fichero “/etc/couchdb/local.ini”, indicando
con el valor “0.0.0.0”, que CouchDB escuchará en todas las interfaces de red,
no solo en localhost. Además, también le vamos a añadir una contraseña para
cuando nos conectemos al usuario admin desde el remoto.
```bash
serjaii@db:~$ sudo nano /opt/couchdb/etc/local.ini
serjaii@db:~$ grep -Ev "^;|^$" /opt/couchdb/etc/local.ini
```
- Verificamos que CouchDB escucha en todas las interfaces.
```bash
serjaii@db:~$ ss -tuln | grep 5984
```

### 3. Instalación del Cliente de CouchDB.
A diferencia de otros sistemas de bases de datos, CouchDB no requiere la instalación
de un cliente independiente. Esto se debe a que CouchDB está diseñado como un
servidor HTTP/REST, lo que significa que todas las operaciones de gestión y
manipulación de datos se realizan mediante peticiones HTTP en formato JSON.
Tenemos las siguientes opciones de clientes disponibles:
- CouchDB incluye un cliente web llamado Fauxton que se ejecuta directamente
en el navegador.
Se requiere el usuario administrador configurado durante la instalación
de CouchDB. Además, no requiere instalación adicional, es multiplataforma y
se accede desde cualquier navegador moderno.
Permite realizar las siguientes acciones:
-

Crear y eliminar bases de datos.

-

Insertar, actualizar y eliminar documentos.
Gestionar usuarios y permisos.
Consultar vistas y realizar replicaciones.
Ejemplo de acceso a Fauxton desde otra máquina:

http://IP_DEL_SERVIDOR:5984/_utils/

- CouchDB se puede controlar completamente usando curl, una herramienta
estándar para enviar peticiones HTTP.
Funciona en cualquier sistema operativo, no necesita instalación extra y
permite la automatización mediante scripts.
Ejemplo de acceso remoto haciendo uso de curl:
```bash
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/_all_dbs
```

### 4. Uso básico de CouchDB.
- Después de instalar CouchDB y configurar la conexión remota, lo primero es
verificar que el servidor esté activo.
```bash
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/
```
- También podemos crear y listar bases de datos. Para ello, primero vamos a
crear una base de datos de prueba y a continuación vamos a listar todas las
bases de datos para comprobar que se ha creado correctamente.
```bash
serjaii@db:~$ curl -X PUT -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/_all_dbs
```
- Creación de un documento con ID automático.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"tipo":"persona","nombre":"Ana","edad":29}' -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1
```
- Creación de un documento con ID conocido.
```bash
serjaii@db:~$ curl -X PUT -H "Content-Type: application/json" -d '{"tipo":"persona","nombre":"Juan","edad":35}' -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/juan
```
- Lectura de los documentos creados previamente.
```bash
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/_all_docs
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/juan
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/4d8a13414adb24b 358662682d0000e13
```
- Borrado de un documento.
```bash
serjaii@db:~$ curl -X DELETE "http://IP_DEL_SERVIDOR:5984/prueba1/juan?rev=175f7db8e2f472106529dba1e056feb54" -u admin:miContraseña
```
- Creación de un índice sobre los campos “tipo” y “edad”, usando consultas
Mango, para acelerar consultas que filtren por “tipo” y “edad”. Las consultas
Mango son consultas JSON similares a MongoDB.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"index":{"fields": ["tipo","edad"]},"name":"idx_tipo_edad","type":"json"}' -u admin:miContraseña http://IP_DEL_SERVIDOR/prueba1/_index
```
- Ejecución de una consulta Mango. En la siguiente consulta, va a devolver un
JSON con todos los documentos que cumplen los criterios de que sean de tipo
“persona” y con “edad” mayor a 25 años, usando los índices si existen para
acelerar la búsqueda.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"selector":{"tipo":"persona","edad": {"$gt":25}},"fields":["_id","nombre","edad"]}' -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/_find
```
- Creación de vistas con MapReduce.
```bash
serjaii@db:~$ curl -X PUT -H "Content-Type: application/json" -d '{"views":{"by_tipo": {"map":"function(doc) {if(doc.tipo)emit(doc.tipo,null);}"}},"language":"javascript"} ' -u admin:admin http://192.168.122.79:5984/prueba1/_design/people
```
- Listamos la vista o la podemos ejecutar también.
```bash
serjaii@db:~$ curl -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/_design/people
serjaii@db:~$ curl -u admin:miContraseña "http://IP_DEL_SERVIDOR:5984/prueba1/_design/people/_vie w/by_tipo"
```
- Replicación local de la base de datos.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"source":"prueba1","target":"prueba1_backup","create_targ et":true}' -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/_replicate
```
- Creación de un usuario en CouchDB.
```bash
serjaii@db:~$ curl -X POST -H "Content-Type: application/json" -d '{"_id":"org.couchdb.user:david","name":"david","roles": ["admin"],"type":"user","password":"david"}' -u admin:admin http://192.168.122.79:5984/_users
```
- Asignación de permisos al usuario sobre la base de datos.
```bash
serjaii@db:~$ curl -X PUT -H "Content-Type: application/json" -d '{"admins":{"names": [],"roles": []},"members":{"names":["david"],"roles":["admin"]}}' -u admin:miContraseña http://IP_DEL_SERVIDOR:5984/prueba1/_security
```
- Comprobación de que podemos acceder a la base de datos y ejecutar acciones
sobre la base de datos de prueba con el nuevo usuario.
```bash
serjaii@db:~$ curl -u david:david http://192.168.122.79:5984/prueba1/_all_docs
```

### 5. Funcionamiento interno de CouchDB.
Arquitectura.
- CouchDB está escrito en Erlang/OTP, usando la VM beam.smp.
- Toda la comunicación es HTTP/REST, usando JSON como formato de
datos.
- Cada documento tiene un _id único y un _rev (revisión), permitiendo
control de versiones y concurrencia.
Almacenamiento.
- CouchDB usa B-trees append-only (copy-on-write).
- Cada modificación crea un nuevo nodo en el B-tree, garantizando
lecturas consistentes sin bloqueos.
MVCC (Multi-Version Concurrency Control).
- Cada documento tiene varias revisiones (_rev).
- Permite lecturas concurrentes sin bloqueos y detecta conflictos de
escritura.
- Los conflictos se resuelven por la aplicación, CouchDB mantiene ambas
versiones.
Replicación.
- Modelo push/pull: CouchDB compara secuencias (_changes) y replica
solo diferencias.
- Soporta replicación continua, ideal para bases distribuidas o offline-first.
- Conflictos se detectan en el destino y la app decide cómo resolverlos.
- Vistas MapReduce: índices persistentes para consultas predefinidas.

- Mango: API JSON para consultas más amigables.
- Sin índice, las consultas requieren full-scan de documentos.
Compaction y mantenimiento.
- Debido al modelo append-only, los archivos crecen continuamente.
- Se utiliza compactación periódica de DB y vistas para liberar espacio.

Instalación de SQL Developer como cliente
remoto de ORACLE usando una conexión
TNS.

### 1.Instalación de Java 17
SQL Developer requiere Java 17. Como Debian Trixie no lo tiene en sus repositorios
oficiales, lo instalaremos desde Adoptium:
- Instalamos las dependencias necesarias
```bash
sudo apt install -y wget apt-transport-https gpg
```
- Añadir la clave GPG del repositorio de Adoptium
```bash
wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public
| sudo gpg --dearmor -o /usr/share/keyrings/adoptium.gpg
```
- Añadir el repositorio
echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg]
https://packages.adoptium.net/artifactory/deb bookworm main" | sudo
tee /etc/apt/sources.list.d/adoptium.list

- Actualizar e instalar Java 17
```bash
sudo apt update
sudo apt install -y temurin-17-jdk
```
- Verificar instalación
java -version

### 2.Descarga SQL Developer desde Oracle
- Lo hacemos a través del siguiente enlace SQL Developer

- Una vez descargada descomprimimos el .zip
```bash
serjaii@db:~$ unzip sqldeveloper-24.3.1.347.1826-no-jre.zip
```
- Tendremos una carpeta con todos los archivos que hemos descomprimidos ,
ahora tenemos que darle permisos de ejecución a un .sh que hay en ese
directorio
```bash
serjaii@db:~$ chmod +x sqldeveloper/sqldeveloper.sh
serjaii@db:~$ ./sqldeveloper.sh
```
- Creamos el tnsnames.ora
```bash
serjaii@db:~$ nano .oracle/tnsnames.ora
```
- En mi caso con el siguiente contenido dentro dependiendo de el hostname de el
servidor y la ip tendremos que hacer algún cambio

ORCLCDB =
(DESCRIPTION =
(ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.122.78)(PORT = 1521))
(CONNECT_DATA =
(SERVER = DEDICATED)
(SERVICE_NAME = ORCLCDB)
)
)

- Tendremos que introducir algunas variables de entorno de oracle dentro
de .bashrc
```bash
serjaii@db:~$ nano ~/.bashrc export ORACLE_HOME=$HOME/oracle/instantclient_21_19 export TNS_ADMIN=$HOME/.oracle export PATH=$ORACLE_HOME:$PATH export LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH alias sqlplus='rlwrap sqlplus'
```
- Algunas líneas ya las tenía yo en .bashrc por la conexión que hacemos de
normal en oracle la línea importante es :
export TNS_ADMIN=$HOME/.oracle

- Aplicamos los cambios en bashrc y comprobamos que las variables se han
establecido correctamente
echo $TNS_ADMIN

- Debe mostrar algo como lo siguiente

```bash
serjaii@db:~$ echo $TNS_ADMIN /home/oteo/SQL-Developer/.oracle
```
- Comprobamos también que tnsnames.ora es accesible
```bash
serjaii@db:~$ cat $TNS_ADMIN/tnsnames.ora ORCLCDB = (DESCRIPTION = (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.122.78)(PORT = 1521)) (CONNECT_DATA = (SERVER = DEDICATED) (SERVICE_NAME = ORCLCDB) ) )
```

### 3.Conexión con SQL Developer
- Ejecutamos el sqldeveloper.sh para abrirlo y seguimos los siguientes pasos para
hacer la conexión TNS

- Abrimos el tnsnames.ora que hemos creado antes

- Ahora donde nos aparecía cargar archivo TNS nos aparecerá ORCLCDB
clicamos hay y tendremos que poner el usuario y la contraseña de la base de
datos

- Después de haber hecho esto ya tendremos cargado toda la base de datos de
oracle

## Herramientas de Administración Web
- Postgre

- MySQL

- MongoDB

## Videocomparativa
- Enlace a YouTube

