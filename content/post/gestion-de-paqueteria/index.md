---
title: "Ejercicios de Gestión de Paquetería"
date: 2025-11-22T14:00:00+01:00
description: "Ejercicios prácticos sobre gestión de paquetería en Debian: apt, dpkg, repositorios y ficheros .deb"
image: cover.png
categories:
  - Sistemas
tags:
  - Debian
  - Apt
  - Dpkg
  - Repositorios
---

# Ejercicios de Gestión de Paquetería

**Por:** Sergio Jimenez Suarez
**Curso:** 2ºASIR - IES Gonzalo Nazareno

---

## Trabajo con apt, aptitude, dpkg

Prepara una máquina virtual con Debian trixie, realizar las siguientes acciones:

### 1. Que acciones consigo al realizar apt update y apt upgrade. Explica detalladamente.

El comando `apt update` constituye el primer paso esencial al actualizar paquetes. Este procedimiento lleva a cabo las siguientes funciones:

*   **Obtención de Metadatos Externos:** `apt update` establece comunicación con los repositorios de software en línea para obtener los metadatos de los paquetes que están disponibles. Esta información incluye detalles sobre las últimas versiones, sus dependencias y otros datos importantes.
*   **Renovación de la Copia Local de Metadatos:** Posteriormente, `apt` actualiza su copia local con estos metadatos. Esto permite que el sistema tenga acceso inmediato a la información acerca de los paquetes sin necesidad de volver a descargarla.

```bash
sudo apt update
```

Tras haber actualizado la información sobre los paquetes disponibles, el siguiente paso a seguir es ejecutar el comando `apt upgrade`. Este comando abarca una serie de acciones clave:

*   **Elección de Versiones Disponibles:** `apt` selecciona las versiones que se considerarán para los paquetes disponibles. Normalmente, estas son las versiones más recientes, aunque pueden hacerse algunas excepciones.
*   **Resolución de Dependencias:** `apt` se encarga de verificar y manejar las dependencias entre los paquetes para asegurar que la actualización se efectúe de forma coherente y que todas las dependencias sean cumplidas.
*   **Descarga de Paquetes:** Si se detectan nuevas versiones de paquetes, `apt` procede a descargarlas desde los repositorios en línea a la caché local del sistema.
*   **Extracción de Paquetes:** `apt` realiza la extracción de los paquetes binarios descargados.
*   **Ejecución de Scripts Preinstalación:** Durante el proceso de actualización, se llevan a cabo los scripts de preinstalación, que pueden incluir configuraciones y ajustes necesarios antes del proceso de instalación.
*   **Instalación de Paquetes Binarios:** A continuación, se instalan los archivos binarios de las nuevas versiones de los paquetes en el sistema.
*   **Ejecución de Scripts Postinstalación:** Finalmente, se ejecutan los scripts de postinstalación, que pueden llevar a cabo configuraciones adicionales después de que se complete la instalación.

```bash
sudo apt upgrade
```

### 2. Lista la relación de paquetes que pueden ser actualizados. ¿Qué información puedes sacar a tenor de lo mostrado en el listado?

Como ya upgradeamos no nos encuentra paquetes pero la sintaxis sería la siguiente:

```bash
apt list --upgradable
```

**Formato:** Nombre del paquete/Versión actual - Versión Disponible - Estado - Descripción del paquete

### 3. Indica la versión instalada, candidata así como la prioridad del paquete openssh-client.

```bash
apt policy openssh-client
```

### 4. ¿Cómo puedes sacar información de un paquete oficial instalado o que no este instalado?

```bash
apt show openssh-client
```

### 5. Saca toda la información que puedas del paquete openssh-client que tienes actualmente instalado en tu máquina.

```bash
dpkg -s openssh-client
```

### 6. Saca toda la información que puedas del paquete openssh-client candidato a actualizar en tu máquina.

```bash
apt show openssh-client
```

Como vemos no hay candidatos nuevos.

### 7. Lista todo el contenido referente al paquete openssh-client actual de tu máquina. Utiliza para ello tanto dpkg como apt.

Con `dpkg`:

```bash
dpkg -L openssh-client
```

Con `apt-file` (si está instalado):

```bash
apt-file list openssh-client
```

### 8. Listar el contenido de un paquete sin la necesidad de instalarlo o descargarlo.

```bash
apt-file list openssh-client
```

### 9. Simula la instalación del paquete openssh-client.

```bash
sudo apt install -s openssh-client
```

Ya cuento con openssh-client, pruebo otro paquete ya que el funcionamiento es el mismo.

### 10. ¿Qué comando te informa de los posible bugs que presente un determinado paquete?

```bash
apt-listbugs list openssh-client
```

### 11. Después de realizar un apt update && apt upgrade. Si quisieras actualizar únicamente los paquetes que tienen de cadena openssh. ¿Qué procedimiento seguirías?

Realiza esta acción, con las estructuras repetitivas que te ofrece bash, así como con el comando xargs.

```bash
apt list --installed | grep openssh | cut -d/ -f1 | xargs sudo apt install --only-upgrade -y
```

### 12. ¿Cómo encontrarías qué paquetes dependen de un paquete específico?

```bash
apt-cache rdepends openssh-client
```

### 13. ¿Cómo procederías para encontrar el paquete al que pertenece un determinado fichero?

```bash
dpkg -S /usr/bin/ssh
```

### 14. ¿Que procedimientos emplearías para liberar la caché en cuanto a descargas de paquetería?

```bash
sudo apt clean
```

### 15. Realiza la instalación del paquete keyboard-configuration pasando previamente los valores de los parámetros de configuración como variables de entorno.

```bash
echo "keyboard-configuration keyboard-configuration/layoutcode string es" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt install keyboard-configuration
```

### 16. Reconfigura el paquete locales de tu equipo, añadiendo una localización que no exista previamente.

Comprueba a modificar las variables de entorno correspondientes para que la sesión del usuario utilice otra localización.

```bash
sudo dpkg-reconfigure locales
```

Comprobación:

```bash
locale
```

### 17. Interrumpe la configuración de un paquete y explica los pasos a dar para continuar la instalación.

Interrumpimos con `Ctl+C`, para reanudarla simplemente:

```bash
sudo dpkg --configure -a
```

### 18. Explica la instrucción que utilizarías para hacer una actualización completa de todos los paquetes de tu sistema de manera completamente no interactiva.

```bash
sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y
```

### 19. Bloquea la actualización de determinados paquetes.

```bash
sudo apt-mark hold apache2
sudo apt-mark showhold
```

---

## Trabajo con ficheros .deb

### 1. Descarga un paquete sin instalarlo, es decir, descarga el fichero .deb correspondiente. Indica diferentes formas de hacerlo.

Copiando el enlace desde los repositorios debian y usando wget:

```bash
wget http://ftp.es.debian.org/debian/pool/main/a/apache2/apache2_2.4.65-2_amd64.deb
```

Con apt:

```bash
sudo apt download apache2
```

### 2. ¿Cómo puedes ver el contenido, que no extraerlo, de lo que se instalará en el sistema de un paquete deb?

```bash
dpkg -c apache2_2.4.65-2_amd64.deb
```

### 3. Sobre el fichero .deb descargado, utiliza el comando ar.

`ar` permite extraer el contenido de una paquete deb. Indica el procedimiento para visualizar con ar el contenido del paquete deb. Con el paquete que has descargado y utilizando el comando ar, descomprime el paquete. ¿Qué información dispones después de la extracción?. Indica la finalidad de lo extraído.

Visualizar contenido:

```bash
ar t apache2_2.4.65-2_amd64.deb
```

Extraer contenido:

```bash
ar x apache2_2.4.65-2_amd64.deb
```

Contenido extraído:
*   `debian-binary`: Versión del formato deb.
*   `control.tar.xz`: Metadatos del paquete (dependencias, scripts, etc).
*   `data.tar.xz`: Archivos del programa.

### 4. Indica el procedimiento para descomprimir lo extraído por ar del punto anterior. ¿Qué información contiene?

```bash
tar -tf data.tar.xz
```

---

## Trabajo con repositorios

### 1. Añade a tu fichero sources.list los repositorios de trixie-backports y sid.

```bash
cat /etc/apt/sources.list
```

### 2. Configura el sistema APT para que los paquetes de debian trixie tengan mayor prioridad y por tanto sean los que se instalen por defecto.

Archivo `/etc/apt/preferences.d/trixie`:

```text
Package: *
Pin: release n=trixie
Pin-Priority: 900
```

### 3. Configura el sistema APT para que los paquetes de trixie-backports tengan mayor prioridad que los de unstable.

Archivo `/etc/apt/preferences.d/trixie`:

```text
Package: *
Pin: release n=trixie
Pin-Priority: 900

Package: *
Pin: release n=trixie-backports
Pin-Priority: 750

Package: *
Pin: release n=unstable
Pin-Priority: 500
```

### 4. ¿Cómo añades la posibilidad de descargar paquetería de la arquitectura i386 en tu sistema?

¿Que comando has empleado?. Lista arquitecturas no nativas. ¿Cómo procederías para desechar la posibilidad de descargar paquetería de la arquitectura i386?

Añadir arquitectura:

```bash
sudo dpkg --add-architecture i386
sudo apt update
```

Eliminar arquitectura:

```bash
sudo dpkg --remove-architecture i386
sudo apt update
```

### 5. Si quisieras descargar un paquete, ¿cómo puedes saber todas las versiones disponible de dicho paquete?

```bash
apt policy apache2
```

### 6. Indica el procedimiento para descargar un paquete del repositorio stable.

```bash
sudo apt download --target-release stable apache2
```

### 7. Indica el procedimiento para descargar un paquete del repositorio de trixie-backports.

```bash
sudo apt download --target-release trixie-backports apache2
```

### 8. Indica el procedimiento para descargar un paquete del repositorio de sid.

```bash
sudo apt download --target-release sid apache2
```

### 9. Indica el procedimiento para descargar un paquete de arquitectura i386.

```bash
sudo apt download apache2:i386
```

---

## Trabajo con directorios

### 1. Que cometidos tienen:

**`/var/lib/apt/lists/`**
Este directorio guarda las listas de los paquetes que ofrecen los repositorios configurados en tu sistema. Los ficheros, con extensión .list, incluyen datos como el nombre del paquete, la versión y la dirección del repositorio. Al ejecutar `apt update`, se renuevan estas listas con la información más reciente.

**`/var/lib/dpkg/available`**
Este archivo recoge información de los paquetes que están disponibles e instalados en tu sistema junto con sus versiones. Lo utiliza `dpkg` para llevar el inventario de lo que tienes instalado y para consultar detalles sobre dependencias.

**`/var/lib/dpkg/status`**
También contiene información sobre los paquetes instalados, pero de forma más completa que available. Indica el estado actual de cada paquete: instalado, eliminado, pendiente de configurar o con errores, ofreciendo así un control más preciso al gestor de paquetes.

**`/var/cache/apt/archives/`**
Aquí se almacenan los archivos .deb descargados antes de instalarse. Cuando haces un `apt-get install` o `apt-get upgrade`, los paquetes primero se bajan a este directorio y luego se instalan. Conservarlos resulta útil si necesitas reinstalar un paquete sin tener que volver a descargarlo, lo que ahorra tiempo y conexión.
