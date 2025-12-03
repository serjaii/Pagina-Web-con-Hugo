---
title: "Creación de un Sistema Automatizado de Instalación para Debian 13 (Trixie)"
author: "Sergio Jiménez"
date: "2025-12-02"
categories: ["Linux", "Debian", "Automation", "DevOps"]
tags: ["debian", "preseed", "xorriso", "bash", "uefi", "bios", "network-install"]
image: "cover.jpg"
---

# Automatización de Instalación de Debian 13 con Preseed y Custom ISO

En este artículo documentaré el proceso que he seguido para crear una imagen ISO de instalación totalmente desatendida para **Debian 13 (Trixie)**. El objetivo de este proyecto es configurar el sistema para que responda automáticamente a todas las preguntas del instalador, configure la red, usuarios, particiones y paquetes adicionales, generando una ISO híbrida compatible tanto con sistemas **BIOS** como **UEFI**.

## Objetivos del Proyecto

*   **Instalación Desatendida**: Automatizar respuestas (idioma, teclado, red, espejo, etc.).
*   **Seguridad**: Las contraseñas de usuario deben estar encriptadas, no en texto plano.
*   **Particionamiento**: Esquema personalizado (en este caso, particionado regular con separación de `/`, `/home` y `/boot`).
*   **Compatibilidad**: La ISO debe arrancar tanto en equipos con firmware BIOS como UEFI.
*   **Paquetes Adicionales**: Instalación automática de `firewalld`, `openssh-server` y entorno de escritorio GNOME.

## Herramientas Necesarias

Para realizar este trabajo, partimos de una imagen `netinst` oficial de Debian y utilizamos la herramienta `xorriso` para manipular la imagen.

```bash
sudo apt install xorriso
```

Descargamos la imagen base:

```bash
wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.1.0-amd64-netinst.iso
```

## El Corazón de la Automatización: `preseed.cfg`

El fichero *preseed* es donde definimos todas las respuestas para el instalador de Debian (`d-i`). A continuación, muestro la configuración final que he utilizado.

Puntos clave de mi configuración:
*   **Localización**: Configurado para España (`es_ES.UTF-8`, zona horaria `Europe/Madrid`).
*   **Red**: Configuración automática por DHCP.
*   **Usuario**: Creación del usuario `serjaii` con contraseña encriptada (generada con `mkpasswd -m sha-512`).
*   **Particionamiento**: He definido una receta personalizada `myregular` que crea particiones para EFI, `/boot` (ext2), `/` (ext4), `/home` (ext4) y `swap`.
*   **Paquetes**: Selección de `gnome-desktop`, `openssh-server`, `build-essential` y `firewalld`.

```conf
# preseed.cfg

# Localización y Teclado
d-i debian-installer/locale string es_ES.UTF-8
d-i debian-installer/language string es
d-i debian-installer/country string ES
d-i keyboard-configuration/xkb-keymap select es

# Red
d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string debian
d-i netcfg/get_domain string sergiojimenez.org
d-i netcfg/wireless_wep string

# Espejo (Mirror)
d-i mirror/country string manual
d-i mirror/http/hostname string ftp.es.debian.org
d-i mirror/http/directory string /debian
d-i mirror/http/proxy string

# Usuarios (Root deshabilitado, usuario serjaii creado)
d-i passwd/root-login boolean false
d-i passwd/user-fullname string Sergio Jimenez
d-i passwd/username string serjaii
# La contraseña debe ser el hash, no el texto plano
d-i passwd/user-password-crypted password $6$c3X/q67VgcznJhFw$uXRYRdnOpMeYtO/YGXJEXDvYj0njGYxBGbxTn5BZqHocFPCauvrGQm16QzqEUb1aEa1ZZu5NlrTIjznyP9D/y41

# Reloj
d-i clock-setup/utc boolean true
d-i time/zone string Europe/Madrid
d-i clock-setup/ntp boolean true

# Particionamiento
d-i partman-auto/method string regular
d-i partman-auto/expert_recipe string                         \
      myregular ::                                           \
              128 128 128 free                                     \
                      $iflabel{ gpt }                        \
                      $reusemethod{ }                        \
                      method{ efi }                          \
                      format{ }                              \
              .                                              \
              512 512 512 ext2                               \
                      $defaultignore{ }                      \
                      method{ format } format{ }             \
                      use_filesystem{ } filesystem{ ext2 }   \
                      mountpoint{ /boot }                    \
                      $bootable{ }                           \
              .                                              \
              5000 5050 -1 ext4                              \
                      $primary{ }                            \
                      method{ format } format{ }             \
                      use_filesystem{ } filesystem{ ext4 }   \
                      mountpoint{ / }                        \
              .                                              \
              2000 2030 -1 ext4                              \
                      method{ format } format{ }             \
                      use_filesystem{ } filesystem{ ext4 }   \
                      mountpoint{ /home }                    \
              .                                              \
              1024 1020 -1 linux-swap                        \
                      method{ swap } format{ }               \
        .
d-i partman-auto/choose_recipe select myregular
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

# Selección de Paquetes
d-i apt-setup/cdrom/set-first boolean false
tasksel tasksel/first multiselect standard, gnome-desktop
d-i pkgsel/include string openssh-server build-essential firewalld
popularity-contest popularity-contest/participate boolean false

# Cargador de Arranque (GRUB)
d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true
d-i grub-installer/bootdev  string default

# Finalización
d-i finish-install/reboot_in_progress note
```

## Automatización del Proceso: El Script

Para evitar realizar los pasos de extracción, modificación y reempaquetado manualmente cada vez que necesitaba ajustar el *preseed*, creé un script en Bash (`automatizado_preseed.sh`).

Este script realiza las siguientes tareas:
1.  **Limpia** el entorno de trabajo anterior.
2.  **Extrae** el contenido de la ISO original usando `xorriso`.
3.  **Inyecta** el fichero `preseed.cfg` dentro del archivo `initrd.gz` (esto es crucial para que el instalador cargue nuestra configuración automáticamente).
4.  **Modifica** los ficheros de configuración de arranque (`isolinux.cfg` para BIOS y `grub.cfg` para UEFI) estableciendo los *timeouts* a 0 para que no pida confirmación al usuario.
5.  **Regenera** la lista de sumas MD5 (`md5sum.txt`).
6.  **Construye** la nueva ISO híbrida bootable.

### Script `automatizado_preseed.sh`

```bash
#!/bin/bash

# Detener el script si hay algún error
set -e

# --- VARIABLES ---
ISO_ORIGINAL="debian-13.1.0-amd64-netinst.iso" 
ISO_FINAL="preseed-debian13.iso" 
DIR_TRABAJO="iso" 
PRESEED_FILE="preseed.cfg" 

echo "=== 0. Limpieza inicial y Chequeo de Espacio ===" 
# Verificamos espacio (mínimo 2GB libres recomendados)
FREE_SPACE=$(df . --output=avail | tail -1)
if [ "$FREE_SPACE" -lt 2000000 ]; then
    echo "ADVERTENCIA: Tienes menos de 2GB libres. Podría fallar." 
    df -h .
    echo "Esperando 3 segundos..." 
    sleep 3
fi

if [ -d "$DIR_TRABAJO" ]; then
    echo "-> Borrando directorio '$DIR_TRABAJO' existente..." 
    sudo rm -rf "$DIR_TRABAJO" 
fi

if [ -f "$ISO_FINAL" ]; then
    echo "-> Borrando archivo '$ISO_FINAL' existente..." 
    sudo rm -f "$ISO_FINAL" 
fi

# --- COMPROBACIONES ---
if [ ! -f "$ISO_ORIGINAL" ]; then
    echo "Error: No se encuentra la imagen $ISO_ORIGINAL" 
    exit 1
fi

if [ ! -f "$PRESEED_FILE" ]; then
    echo "Error: No se encuentra el fichero $PRESEED_FILE" 
    exit 1
fi

echo "=== 1. Extrayendo ISO original ===" 
# Usamos xorriso para extraer
sudo xorriso -osirrox on -indev "$ISO_ORIGINAL" -extract / "$DIR_TRABAJO/" 

echo "=== 2. Inyectando Preseed en initrd ===" 
sudo chmod +w -R "$DIR_TRABAJO/install.amd/" 
sudo gunzip "$DIR_TRABAJO/install.amd/initrd.gz" 

# Inyectamos el preseed.cfg
echo "$PRESEED_FILE" | sudo cpio -H newc -o -A -F "$DIR_TRABAJO/install.amd/initrd" 

sudo gzip "$DIR_TRABAJO/install.amd/initrd" 
sudo chmod -w -R "$DIR_TRABAJO/install.amd/" 

echo "=== 3. Configurando arranque BIOS (Isolinux) ===" 
CFG_ISOLINUX="$DIR_TRABAJO/isolinux/isolinux.cfg" 
sudo chmod +w "$CFG_ISOLINUX" 

# Modificaciones para Isolinux
sudo sed -i 's/^default/#default/g' "$CFG_ISOLINUX" 
sudo sed -i 's/^timeout.*/timeout 0/g' "$CFG_ISOLINUX" 
if grep -q "prompt" "$CFG_ISOLINUX"; then
    sudo sed -i 's/^prompt.*/prompt 0/g' "$CFG_ISOLINUX" 
else
    echo "prompt 0" | sudo tee -a "$CFG_ISOLINUX" > /dev/null
fi
sudo chmod -w "$CFG_ISOLINUX" 

echo "=== 4. Configurando arranque UEFI (GRUB) ===" 
CFG_GRUB="$DIR_TRABAJO/boot/grub/grub.cfg" 
sudo chmod +w "$CFG_GRUB" 

# Modificaciones para GRUB
if grep -q "set timeout=" "$CFG_GRUB"; then
    sudo sed -i 's/set timeout=.*/set timeout=0/g' "$CFG_GRUB" 
else
    echo "set timeout=0" | sudo tee -a "$CFG_GRUB" > /dev/null
fi

if grep -q "set default=" "$CFG_GRUB"; then
    sudo sed -i 's/set default=.*/set default=1/g' "$CFG_GRUB" 
else
    echo "set default=1" | sudo tee -a "$CFG_GRUB" > /dev/null
fi

if ! grep -q "set timeout_style=hidden" "$CFG_GRUB"; then
    sudo sed -i '1i set timeout_style=hidden' "$CFG_GRUB" 
fi
sudo chmod -w "$CFG_GRUB" 

echo "=== 5. Asegurando Permisos y Regenerando MD5 ===" 
# 1. Aseguramos que TODOS los archivos sean legibles por todos
sudo chmod -R u+w,a+r "$DIR_TRABAJO" 

cd "$DIR_TRABAJO" 
rm -f md5sum.txt

echo "Generando md5sum.txt limpio..." 
find . -type f -not -name 'md5sum.txt' -not -path '*/debian/*' -print0 | \
    xargs -0 md5sum | \
    sed 's| \./| |' > md5sum.txt

sudo chmod a-w md5sum.txt
cd ..

echo "=== 6. Creando ISO final ($ISO_FINAL) con XORRISO ===" 
cd "$DIR_TRABAJO" 
sudo xorriso -as mkisofs \
   -r -V 'Debian_Custom' \
   -o "../$ISO_FINAL" \
   -J -joliet-long \
   -b isolinux/isolinux.bin \
   -c isolinux/boot.cat \
   -boot-load-size 4 \
   -boot-info-table \
   -no-emul-boot \
   -eltorito-alt-boot \
   -e boot/grub/efi.img \
   -no-emul-boot \
   -isohybrid-gpt-basdat \
   .
cd ..

echo "=== ¡Proceso completado! ===" 
ls -lh "$ISO_FINAL" 
```

## Ejecución y Resultado

Para generar la ISO, simplemente ejecutamos el script con permisos de superusuario:

```bash
sudo bash automatizado_preseed.sh
```

El resultado es un archivo `preseed-debian13.iso` de aproximadamente 968MB. Esta imagen puede ser grabada en un USB o utilizada en una máquina virtual (VirtualBox, KVM, VMware). Al arrancar, el sistema iniciará automáticamente la instalación sin realizar ninguna pregunta, y al finalizar, tendremos un sistema Debian 13 con entorno GNOME, usuario configurado y particiones listas para usar.

## Instalación por Red

Además de la instalación mediante USB o imagen ISO directa, he habilitado la posibilidad de realizar la instalación a través de la red utilizando los recursos alojados en este mismo servidor.

He subido tanto la imagen ISO personalizada como el fichero `preseed.cfg` para que estén accesibles públicamente.

### Descarga de Recursos

*   **Imagen ISO Personalizada**: [preseed-debian13.iso](/isos/preseed-debian13.iso)
*   **Fichero Preseed**: [preseed.cfg](/isos/preseed.cfg)

### Cómo usar el Preseed por Red

Si dispones de una imagen de instalación estándar de Debian (netinst) y quieres aplicar mi configuración automatizada sin modificar la ISO, puedes hacerlo pasando la URL del preseed como parámetro de arranque.

1.  Arranca el instalador de Debian.
2.  En el menú de arranque (GRUB o Isolinux), presiona `TAB` o `e` para editar las opciones de arranque.
3.  Añade el siguiente parámetro a la línea de comandos del kernel:

    ```
    auto url=http://sergiojimenez.org/isos/preseed.cfg
    ```

4.  Inicia el arranque. El instalador descargará el fichero de configuración y procederá con la instalación desatendida tal como se ha definido.

Esto es especialmente útil para entornos de virtualización o instalaciones masivas donde no queremos mantener múltiples imágenes ISO modificadas.
