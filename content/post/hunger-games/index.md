---
title: "Hunger Games"
date: 2025-10-11T23:06:17+02:00
description: "Ejercicio de configuración de red y ACL - Hunger Games"
image: cover.jpg
categories:
  - Redes
tags:
  - Redes
  - ACL
  - DHCP
  - Cisco
---

# Hunger Games

Vas a participar en The Hunger Games, un juego de alianzas donde el objetivo es sobrevivir. El mundo se divide en distritos, numerados del 1 al 12 del más rico al más pobre. También se rumorea la existencia de un distrito 13, pero nadie está muy seguro de su existencia. En este momento solo quedan representantes de cuatro distritos.

El escenario del juego incluye todos los distritos anteriores y el distrito secreto, al que al principio nadie sabe llegar.

---

## Ejercicio 1: Configuración de red

**Realizar la configuración de la red que sea necesaria para que todos los participantes puedan comunicarse entre sí por la ruta más corta posible. Documenta el proceso y demuestra su funcionamiento.**

Para permitir la comunicación de todos los participantes en primer lugar le asignaremos direcciones IP tanto a estos como a las interfaces de los routers en el camino.

### Direcciones IP de los Participantes

```
Marvel: 10.0.1.2 /24
Glimmer: 10.0.1.3 /24
Cato: 10.0.2.2 /24
Clover: 10.0.2.3 /24
Thresh: 10.0.11.2 /24
Rue: 10.0.11.3 /24
Peeta: 10.0.12.2 /24
Katniss: 10.0.12.3 /24
```

### Direcciones IP de los Routers

```
R1 f0/0: 10.0.1.1 /24
R1 f0/1: 172.23.0.1 /24
R1 f1/0: 192.168.1.2 /24

R2 f0/0: 10.0.11.1 /24
R2 f0/1: 172.23.0.2 /24
R2 f1/0: 172.24.0.1 /24
R2 f1/1: 192.168.11.2 /24

R3 f0/0: 10.0.2.1 /24
R3 f0/1: 172.25.0.1 /24
R3 f1/0: 192.168.2.2 /24

R4 f0/0: 10.0.12.1 /24
R4 f0/1: 172.24.0.2 /24
R4 f1/0: 192.168.12.2 /24
R4 f1/1: 172.25.0.2 /24

R5 f0/0: 192.168.11.1 /24
R5 f0/1: 192.168.12.1 /24
R5 f1/0: 192.168.1.1 /24
R5 f1/1: 192.168.2.1 /24
R5 f2/0: 10.0.13.1 /24
```

Una vez asignadas las IP pasaremos con el direccionamiento de los routers.

### Configuración de Enrutamiento

**R1:**
Si el distrito 1 quiere comunicar con el distrito 11 el tráfico irá a R2, en el resto de casos saldrá por la salida por defecto hacia R5.

![Configuración R1](image1.png)

**R2:**
Como el Distrito 13 es aún desconocido por los participantes ignoraremos su presencia a la hora de hacer el enrutamiento, esto nos ahorrará momentáneamente una línea a la tabla. La comunicación para el distrito 1 saldrá hacia R1 y la salida por defecto será hacia R4.

![Configuración R2](image2.png)

**R3:**
Similar a R1, salida por defecto camino a R5, excepto mensajes para el distrito 12 que saldrán hasta R4.

![Configuración R3](image3.png)

**R4:**
Similar a R2, los mensajes a distrito 2 viajarán a R3, el resto hasta R2.

![Configuración R4](image4.png)

**R5:**
En este caso sí deberemos especificar las rutas hacia cada distrito, la salida por defecto la dejaré mirando hacia el distrito 13 pensando a futuro, pues en cualquier caso no nos va a ahorrar líneas a la tabla de enrutamiento.

![Configuración R5](image5.png)

### Comprobación de ping entre distritos

**Distrito 1:**

- **Distrito 2:**

![Ping Distrito 1 a 2](image6.png)

- **Distrito 11:**

![Ping Distrito 1 a 11](image7.png)

- **Distrito 12:**

![Ping Distrito 1 a 12](image8.png)

---

## Ejercicio 2: ACL según alianzas

**Establecer las ACL necesarias para reflejar la situación descrita. Documenta el proceso y demuestra su funcionamiento.**

A medida que avanza el juego se van modificando las alianzas y, por tanto, algunos participantes pasan a ser enemigos y dejan de tener comunicación entre ellos. Así, el segundo día la situación es la siguiente:

### Los superpijos se han peleado con todos

> Los superpijos se han peleado con todos y no se comunican con el resto de distritos, cuyos mensajes no quieren escuchar.

Para esta situación tenemos 2 opciones usando ACL:
- En el router de cada distrito bloquear el tráfico con destino 10.0.1.0, requiere crear una ACL en R2, R3 y R4.
- Cortar todo el tráfico de R1, en mi opinión la más eficiente y la que voy a usar, el inconveniente es que los mensajes provenientes de los demás distritos recorren un mayor camino antes de ser desechados por R1.

Con esto he creado una ACL estándar en el router del distrito 1, todo el tráfico que intente salir desde la interfaz del switch será denegado.

![ACL Distrito 1](image9.png)

**Ping desde fuera hacia Distrito 1:**

![Ping desde fuera](image10.png)

**Ping desde Distrito 1 hacia fuera:**

![Ping desde dentro](image11.png)

Como podemos ver el mensaje de error es distinto, si hacemos el ping desde un PC fuera del distrito 1 nos encontraremos de cara con la ACL que nos denegará el paso y nos devolverá el mensaje de 'administratively prohibited'. Sin embargo si probamos un ping desde dentro del distrito 1 el mensaje será timeout debido a que la comunicación sí está alcanzando el destino, pero a su vuelta esta se encuentra de nuevo con la ACL que ahora sí, le deniega el paso.

### Los indigentes y los demás distritos

> Los indigentes se comunican con los pobres, pero los demás distritos no quieren saber nada de ellos.

Crearemos una ACL extendida en la interfaz del switch de R4, para denegar todo el tráfico que se intente enviar a los distritos 1 y 2.

![ACL R4](image12.png)

Comprobamos ping a cada distrito desde el 12:

![Comprobación pings](image13.png)

### Alianza entre pobres y pijos

> Los pobres y los pijos han establecido una alianza un tanto sorprendente y pueden comunicarse aun entre ellos, aunque solo a través de R5.

Ahora sí deberemos modificar nuestras tablas de enrutamiento de R2 y R4. Enviaremos el tráfico por defecto a R5, tendremos que añadir la ruta entre R2 y R4 manualmente.

![Modificación enrutamiento R2](image14.png)

![Modificación enrutamiento R4](image15.png)

No será necesario configurar ACL en este punto ya que toda comunicación entre Distritos 2 y 11 pasará por R5.

![Comprobación comunicación](image16.png)

---

## Ejercicio 3: Servidor DHCP

Al día siguiente, los superpijos deciden que es supercansado poner las direcciones IP a mano, así que tienes que montarles un servidor DHCP en el router de su red para que sus máquinas reciban automáticamente una dirección IP de las cinco primeras de su rango de direcciones, reservando la primera para el propio router.

**Configura el servidor DHCP de los superpijos. Documenta el proceso y demuestra su funcionamiento.**

Excluimos la IP del router y las que no queremos que sean asignadas:

![Exclusión IPs](image17.png)

Ahora configuramos los parámetros del servidor DHCP:

![Configuración DHCP](image18.png)

Comprobamos su funcionamiento:

![Comprobación DHCP 1](image19.png)

![Comprobación DHCP 2](image20.png)

---

## Ejercicio 4: ACL por relaciones personales

**Configura las ACL (extendidas o no) que sean necesarias para representar este nuevo escenario. Documenta el proceso y demuestra su funcionamiento.**

Cuando pasa una semana, las alianzas y enemistades ya no son solo entre distritos sino entre participantes individuales.

- Peeta establece una alianza con Clove y debe poder comunicarse con él.
- Katniss deja de hablarse con Rue.
- Katniss y Cato están empezando una bonita relación y necesitan comunicarse entre ellos.

Como anteriormente se denegó todo el tráfico proveniente del Distrito 12 debemos reescribir dicha ACL, permitiendo las comunicaciones que se indican, será una ACL extendida.

![ACL extendida R4](image21.png)

Con esto:
- Katniss solo puede comunicarse con Peeta, Cato y Thresh.
- Peeta podrá comunicarse con Katniss, Clove y el Distrito 11.

**Comprobaciones:**

![Comprobación Katniss](image22.png)

![Comprobación Peeta](image23.png)

Si intentamos hacer un ping denegado en sentido contrario volveremos a encontrarnos con el mensaje de timeout anteriormente explicado.

### Cato y Thresh se pelean

> Cato y Thresh han acabado peleándose y ya no hay comunicación entre ellos.

Denegamos la comunicación con una ACL extendida, podemos colocarla tanto en R2 como R3 y R5, en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.

![ACL Cato-Thresh](image24.png)

![Comprobación Cato-Thresh 1](image25.png)

![Comprobación Cato-Thresh 2](image26.png)

---

## Ejercicio 5: Servidor web del distrito 13

Los juegos del hambre van avanzando y algunos participantes han descubierto al fin el secreto del distrito 13. No parece existir vida en él, pero hay un servidor web lleno de documentos muy útiles para sobrevivir.

**Monta un servidor web en el distrito 13 que sea accesible mediante ACL extendidas solo para los participantes de los distritos 11 y 12. La comunicación se establecerá por el puerto 80. Documenta el proceso y demuestra su funcionamiento.**

Para montar el servidor sustituiremos la máquina VPCS por un Debian al que le instalaremos Apache, le daremos acceso a una nube NAT momentáneamente.

![Instalación Apache](image27.png)

Instalamos Apache2 y le damos una IP estática, ya podemos quitar la nube:

![IP estática servidor](image28.png)

![Configuración Apache](image29.png)

Si hacemos ping desde las distintas máquinas veremos que tenemos acceso desde los Distritos 2 y 11.

![Ping inicial](image30.png)

En primer lugar modificaremos la ACL de R4 para permitirle el acceso al distrito 12.

Como las ACL se leen en orden debemos añadir la línea que permita el paso antes de 'deny ip any any'.

![Modificación ACL R4](image31.png)

El '45' colocará la regla justo antes del deny any.

**Comprobación:**

![Comprobación acceso D12](image32.png)

Ahora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida:

![Denegación D2](image33.png)

**Comprobación:**

![Comprobación acceso permitido](image34.png)

![Comprobación acceso denegado D2](image35.png)

Ahora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5:

![ACL puerto 80 R5](image36.png)

Si ahora probamos a volver a hacer un ping nos encontramos con que la ACL nos lo cortará, esto es debido a que el protocolo ICMP (ping) no trabaja en el puerto 80.

![Ping bloqueado](image37.png)

Para comprobar que el servidor web es accesible desde los distritos 11 y 12 vamos a añadir 1 tinycore con firefox al switch de dichos distritos.

![TinyCore setup](image38.png)

Será necesario configurar la IP de ambas máquinas en rango. Una vez hecho podremos acceder al servidor web.

![Acceso web Distrito 12](image39.png)

![Acceso web Distrito 11](image40.png)

---

**Fin del documento**
