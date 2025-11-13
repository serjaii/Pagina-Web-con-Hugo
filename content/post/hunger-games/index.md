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

## Introducción

Esta práctica simula un escenario de red complejo basado en la temática de *The Hunger Games*. A través de cinco ejercicios progresivos, implementaremos configuraciones de red avanzadas que incluyen enrutamiento estático, listas de control de acceso (ACL), servidor DHCP y un servidor web con restricciones de acceso.

Los objetivos principales son:
- Configurar el enrutamiento entre múltiples distritos (redes)
- Implementar políticas de seguridad mediante ACL estándar y extendidas
- Automatizar la asignación de direcciones IP con DHCP
- Gestionar accesos a servicios web mediante filtrado por puerto

Esta práctica permite aplicar conceptos fundamentales de redes en un contexto dinámico donde las alianzas (y por tanto, las políticas de acceso) cambian constantemente.

---

## Contexto del escenario

Vas a participar en *The Hunger Games*, un juego de alianzas donde el objetivo es sobrevivir.  
El mundo se divide en distritos, numerados del 1 al 12 del más rico al más pobre.  
También se rumorea la existencia de un distrito 13, pero nadie está muy seguro de su existencia.  
En este momento solo quedan representantes de cuatro distritos.

El escenario del juego incluye todos los distritos anteriores y el distrito secreto, al que al principio nadie sabe llegar.

![debajo del título](debajodeltítulo.png)

---

## Ejercicio 1: Configuración de red

Realizar la configuración de la red que sea necesaria para que todos los participantes puedan comunicarse entre sí por la ruta más corta posible.  
Documenta el proceso y demuestra su funcionamiento.

Para permitir la comunicación de todos los participantes en primer lugar asignaremos direcciones IP tanto a estos como a las interfaces de los routers en el camino.

### Direcciones IP

**Participantes:**

- Marvel: 10.0.1.2 /24  
- Glimmer: 10.0.1.3 /24  
- Cato: 10.0.2.2 /24  
- Clover: 10.0.2.3 /24  
- Thresh: 10.0.11.2 /24  
- Rue: 10.0.11.3 /24  
- Peeta: 10.0.12.2 /24  
- Katniss: 10.0.12.3 /24  

**Routers:**

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

### Direccionamiento de routers

**R1:**  
Si el distrito 1 quiere comunicar con el distrito 11 el tráfico irá a R2, en el resto de casos saldrá por la salida por defecto hacia R5.

![Si el distrito 1 quiere comunicar con el distrito 11 el tráfico irá a R2, en el resto de casos saldrá por la salida por defecto hacia R5.](debajodeSi el distrito 1 quiere comunicar con el distrito 11 el tráfico irá a R2, en el resto de casos saldrá por la salida por defecto hacia R5..png)

**R2:**  
Ignoramos el distrito 13, la comunicación para el distrito 1 saldrá hacia R1 y la salida por defecto será hacia R4.

![Como el Distrito 13 es aún desconocido por los participantes ignoraremos su presencia a la hora de hacer el enrutamiento,esto nos ahorrará momentáneamente una línea a la tabla.La comunicación para el distrito 1 saldrá hacia R1.](debajodeComo el Distrito 13 es aún desconocido por los participantes ignoraremos su presencia a la hora de hacer el enrutamiento,esto nos ahorrará momentáneamente una línea a la tabla.La comunicación para el distrito 1 saldrá hacia R1.png)

**R3:**  
Salida por defecto hacia R5, excepto mensajes para el distrito 12 que saldrán hasta R4.

![Similar a R1,salida por defecto camino a R5,excepto mensajes para el distrito 12 que saldrán hasta R4.](debajodeSimilar a R1,salida por defecto camino a R5,excepto mensajes para el distrito 12 que saldrán hasta R4..png)

**R4:**  
Mensajes al distrito 2 viajarán a R3, el resto hasta R2.

![Similar a R2, los mensajes a distrito 2 viajarán a R3, el resto hasta R2.](debajodeSimilar a R2, los mensajes a distrito 2 viajarán a R3, el resto hasta R2..png)

**R5:**  
Deberemos especificar rutas hacia cada distrito, salida por defecto hacia el distrito 13.

![En este caso sí deberemos especificar las rutas hacia cada distrito, la salida por defecto la dejaré mirando hacia el distrito 13 pensando a futuro,pues en cualquier caso no nos va a ahorrar líneas a la tabla de enrutamiento.](debajodeEn este caso sí deberemos especificar las rutas hacia cada distrito, la salida por defecto la dejaré mirando hacia el distrito 13 pensando a futuro,pues en cualquier caso no nos va a ahorrar líneas a la tabla de enrutamiento..png)

### Comprobación de conectividad

- Ping entre distritos:
  - Distrito 1 → Distrito 2  

![Comprobación de ping entre distritos: Distrito 1](debajode-Comprobación de ping entre distritos:Distrito1.png)

  - Distrito 1 → Distrito 11  

![Comprobación de ping entre distritos: distrito 11](debajode-Comprobación de ping entre distritos:distrito11.png)

  - Distrito 1 → Distrito 12

![Comprobación de ping entre distritos: distrito 12](debajode-Comprobación de ping entre distritos:distrito12.png)

![Comprobación de ping entre distritos: distrito 2](debajode-Comprobación de ping entre distritos:distrito2.png)

---

## Ejercicio 2: ACL según alianzas

A medida que avanza el juego se van modificando las alianzas.  
El segundo día la situación es la siguiente:

> Los superpijos se han peleado con todos y no se comunican con el resto de distritos.

### Opción 1
En el router de cada distrito bloquear tráfico destino `10.0.1.0`.

### Opción 2
Cortar todo el tráfico de R1 (más eficiente).  
Se crea una **ACL estándar** en R1 que deniega todo el tráfico saliente desde la interfaz del switch.

![Cortar todo el trafico de R1,en mi opinion la mas eficiente y la que voy a usar,el inconveniente es que los mensajes provenientes de los demas distritos recorren un mayor camino antes de ser desechados por R1.](debajodeCortar todo el trafico de R1,en mi opinion la mas eficiente y la que voy a usar,el inconveniente es que los mensajes provenientes de los demas distritos recorren un mayor camino antes de ser desechados por R1..png)

**Resultados:**

- Ping desde fuera → "administratively prohibited"

![Ping desde fuera hacia Distrito 1.](debajodePing desde fuera hacia Distrito 1..png)

- Ping desde dentro → timeout (por denegación al retorno)

![Ping desde Distrito 1 hacia fuera.](debajodePing desde Distrito 1 hacia fuera.png)

---

> Los indigentes se comunican con los pobres, pero los demás distritos no quieren saber nada de ellos.

Se crea una **ACL extendida** en R4 para denegar tráfico hacia los distritos 1 y 2.

![Crearemos una ACL extendida en la interfaz del switch de R4, para denegar todo el tráfico que se intente enviar a los distritos 1 y 2.](debajodeCrearemos una ACL extendida en la interfaz del switch de R4, para denegar todo el tráfico que se intente enviar a los distritos 1 y 2..png)

Comprobamos ping desde el distrito 12.

![Comprobamos ping a cada distrito desde el 12.](debajodeComprobamos ping a cada distrito desde el 12..png)

---

> Los pobres y los pijos se alían y pueden comunicarse solo a través de R5.

Se modifica el enrutamiento de R2 y R4 para enviar tráfico por defecto a R5.  
No se necesita ACL nueva.

![Ahora sí deberemos modificar nuestras tablas de enrutamiento de R2 y R4.Enviaremos el tráfico por defecto a R5, tendremos que añadir la ruta entre R2 y R4 manualmente.imagen1de2](debajodeAhora sí deberemos modificar nuestras tablas de enrutamiento de R2 y R4.Enviaremos el tráfico por defecto a R5, tendremos que añadir la ruta entre R2 y R4 manualmente.imagen1de2.png)

![Ahora sí deberemos modificar nuestras tablas de enrutamiento de R2 y R4.Enviaremos el tráfico por defecto a R5, tendremos que añadir la ruta entre R2 y R4 manualmente.imagen2de2](debajodeAhora sí deberemos modificar nuestras tablas de enrutamiento de R2 y R4.Enviaremos el tráfico por defecto a R5, tendremos que añadir la ruta entre R2 y R4 manualmente.imagen2de2.png)

---

## Ejercicio 3: DHCP para los superpijos

Se monta un **servidor DHCP** en el router del distrito 1.  
Las máquinas deben recibir IP automáticamente (cinco primeras del rango), reservando la primera para el router.

### Pasos:

1. Excluir la IP del router.

![Excluimos la IP del router y las que no queremos que sean asignadas.Excluimos la IP del router y las que no queremos que sean asignadas.](debajodeExcluimos la IP del router y las que no queremos que sean asignadas.Excluimos la IP del router y las que no queremos que sean asignadas..png)

2. Configurar parámetros del servidor DHCP.

![Ahora configuramos los parámetros del servidor DHCP.](debajodeAhora configuramos los parámetros del servidor DHCP.png)

3. Comprobar asignación automática de IPs.

![Comprobamos su funcionamiento imagen1de3](debajodeComprobamos su funcionamientoimagen1de3.png)

![Comprobamos su funcionamiento imagen2de3](debajodeComprobamos su funcionamientoimagen2de3.png)

![Comprobamos su funcionamiento imagen3de3](debajodeComprobamos su funcionamientoimagen3de3.png)

---

## Ejercicio 4: ACL por relaciones personales

> Peeta establece alianza con Clove.  
> Katniss deja de hablarse con Rue.  
> Katniss y Cato se comunican.

Como el tráfico del distrito 12 estaba bloqueado, se reescribe la **ACL extendida**:

![Como anteriormente se denegó todo el tráfico proveniente del Distrito 12 debemos reescribir dicha ACL,permitiendo las comunicaciones que se indican,será una ACL extendida.imagen1de2](debajodeComo anteriormente se denegó todo el tráfico proveniente del Distrito 12 debemos reescribir dicha ACL,permitiendo las comunicaciones que se indican,será una ACL extendida.imagen1de2.png)

![Como anteriormente se denegó todo el tráfico proveniente del Distrito 12 debemos reescribir dicha ACL,permitiendo las comunicaciones que se indican,será una ACL extendida.imagen2de2](debajodeComo anteriormente se denegó todo el tráfico proveniente del Distrito 12 debemos reescribir dicha ACL,permitiendo las comunicaciones que se indican,será una ACL extendida.imagen2de2.png)

- Katniss ↔ Peeta, Cato, Thresh  
- Peeta ↔ Katniss, Clove, Distrito 11  

![Katniss solo puede comunicarse con Peeta,Cato y Thresh.imagen1de2](debajode	-Katniss solo puede comunicarse con Peeta,Cato y Thresh.imagen1de2.png)

![Katniss solo puede comunicarse con Peeta,Cato y Thresh.imagen2de2](debajode	-Katniss solo puede comunicarse con Peeta,Cato y Thresh.imagen2de2.png)

**Comprobaciones:**  
Ping en ambos sentidos, con timeout cuando está denegado.



Si intentamos hacer un ping denegado en sentido contrario volveremos a encontrarnos con el mensaje de timeout anteriormente explicado.

![Si intentamos hacer un ping denegado en sentido contrario volveremos a encontrarnos con el mensaje de timeout anteriormente explicado.](debajodeSi intentamos hacer un ping denegado en sentido contrario volveremos a encontrarnos con el mensaje de timeout anteriormente explicado..png)

> Cato y Thresh se pelean.

Se deniega comunicación con una ACL extendida (puede estar en R2, R3 o R5).

![Denegamos la comunicación con una ACL extendida,podemos colocarla tanto en R2 como R3 y R5,en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.imagen1de3](debajodeDenegamos la comunicación con una ACL extendida,podemos colocarla tanto en R2 como R3 y R5,en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.imagen1de3.png)

![Denegamos la comunicación con una ACL extendida,podemos colocarla tanto en R2 como R3 y R5,en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.imagen2de3](debajodeDenegamos la comunicación con una ACL extendida,podemos colocarla tanto en R2 como R3 y R5,en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.imagen2de3.png)

![Denegamos la comunicación con una ACL extendida,podemos colocarla tanto en R2 como R3 y R5,en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.imagen3de3](debajodeDenegamos la comunicación con una ACL extendida,podemos colocarla tanto en R2 como R3 y R5,en cualquiera de los casos al menos uno de los mensajes tendrán que recorrer más de un router antes de ser eliminado.imagen3de3.png)

---

## Ejercicio 5: Servidor web del distrito 13

Se monta un **servidor Apache** accesible solo desde los distritos 11 y 12 (puerto 80).

### Pasos:

1. Sustituir VPCS por Debian con Apache2.

![Para montar el servidor sustituiremos la máquina VPCS por un Debian al que le instalaremos Apache,le daremos acceso a una nube NAT momentáneamente.](debajodePara montar el servidor sustituiremos la máquina VPCS por un Debian al que le instalaremos Apache,le daremos acceso a una nube NAT momentáneamente..png)

2. Asignar IP estática.

![Instalamos Apache2 y le damos una IP estática,ya podemos quitar la nube.imagen1de2](debajodeInstalamos Apache2 y le damos una IP estática,ya podemos quitar la nube.imagen1de2.png)

![Instalamos Apache2 y le damos una IP estática,ya podemos quitar la nube.imagen2de2](debajodeInstalamos Apache2 y le damos una IP estática,ya podemos quitar la nube.imagen2de2.png)

Si hacemos ping desde las distintas máquinas veremos que tenemos acceso desde los Distritos 2 y 11.

![Si hacemos ping desde las distintas máquinas veremos que tenemos acceso desde los Distritos 2 y 11.](debajodeSi hacemos ping desde las distintas máquinas veremos que tenemos acceso desde los Distritos 2 y 11..png)

En primer lugar modificaremos la ACL de R4 para permitirle el acceso al distrito 12.

3. Modificar ACLs:

   - En **R4** permitir acceso del distrito 12 antes del `deny ip any any`.

![Como las ACL se leen en orden debemos añadir la línea que permita el paso antes de 'deny ip any any'.imagen1de2](debajodeComo las ACL se leen en orden debemos añadir la línea que permita el paso antes de 'deny ip any any'.imagen1de2.png)

![Como las ACL se leen en orden debemos añadir la línea que permita el paso antes de 'deny ip any any'.imagen2de2](debajodeComo las ACL se leen en orden debemos añadir la línea que permita el paso antes de 'deny ip any any'.imagen2de2.png)

El '45' colocará la regla justo antes del deny any. - Comprobación:

![El '45' colocará la regla justo antes del deny any.-comprobacion:](debajodeEl '45' colocará la regla justo antes del deny any.-comprobacion:.png)

Ahora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida.

   - En **R3** denegar acceso del distrito 2.

![Ahora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida.](debajodeAhora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida..png)

Comprobación:

![Ahora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida.-comprobacion:](debajodeAhora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida.-comprobacion:.png)

Ahora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.

   - En **R5** permitir solo puerto 80.

![Ahora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.imagen1de2](debajodeAhora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.imagen1de2.png)

![Ahora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.imagen2de2](debajodeAhora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.imagen2de2.png)

### Comprobaciones:

- Ping bloqueado (ICMP ≠ puerto 80).

![Si ahora probamos a volver a hacer un ping nos encontramos con que la ACL nos lo cortará,esto es debido a que el protocolo ICMP(ping) no trabaja en el puerto 80.](debajodeSi ahora probamos a volver a hacer un ping nos encontramos con que la ACL nos lo cortará,esto es debido a que el protocolo ICMP(ping) no trabaja en el puerto 80..png)

- Acceso web permitido desde distritos 11 y 12 (navegador Firefox en TinyCore).

Para comprobar que el servidor web es accesible desde los distritos 11 y 12 vamos a añadir 1 tinycore con firefox al switch de dichos distritos.

![Para comprobar que el servidor web es accesible desde los distritos 11 y 12 vamos a añadir 1 tinycore con firefox al switch de dichos distritos.](debajodePara comprobar que el servidor web es accesible desde los distritos 11 y 12 vamos a añadir 1 tinycore con firefox al switch de dichos distritos..png)

Será necesario configurar la IP de ambas máquinas en rango. Una vez hecho podremos acceder al servidor web.

![Será necesario configurar la IP de ambas máquinas en rango.Una vez hecho podremos acceder al servidor web.](debajodeSerá necesario configurar la IP de ambas máquinas en rango.Una vez hecho podremos acceder al servidor web..png)

---

**Fin del documento**
