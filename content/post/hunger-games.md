---
title: "Hunger Games"
date: 2025-10-11T23:06:17+02:00
description: "Ejercicio de configuración de red y ACL - Hunger Games"
image: img/hunger-games-cover.jpg
categories:
  - Redes
  - Práctica
tags:
  - Redes
  - ACL
  - DHCP
  - Cisco
---

# Hunger Games

Vas a participar en *The Hunger Games*, un juego de alianzas donde el objetivo es sobrevivir.  
El mundo se divide en distritos, numerados del 1 al 12 del más rico al más pobre.  
También se rumorea la existencia de un distrito 13, pero nadie está muy seguro de su existencia.  
En este momento solo quedan representantes de cuatro distritos.

El escenario del juego incluye todos los distritos anteriores y el distrito secreto, al que al principio nadie sabe llegar.

![Esquema de red](/img/debajodeltítulo.png)

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

![Configuración R1](/img/debajodeSi%20el%20distrito%201%20quiere%20comunicar%20con%20el%20distrito%2011%20el%20tráfico%20irá%20a%20R2,%20en%20el%20resto%20de%20casos%20saldrá%20por%20la%20salida%20por%20defecto%20hacia%20R5..png)

**R2:**  
Ignoramos el distrito 13, la comunicación para el distrito 1 saldrá hacia R1 y la salida por defecto será hacia R4.

![Configuración R2](/img/debajodeComo%20el%20Distrito%2013%20es%20aún%20desconocido%20por%20los%20participantes%20ignoraremos%20su%20presencia%20a%20la%20hora%20de%20hacer%20el%20enrutamiento,esto%20nos%20ahorrará%20momentáneamente%20una%20línea%20a%20la%20tabla.La%20comunicación%20para%20el%20distrito%201%20saldrá%20hacia%20R1.png)

**R3:**  
Salida por defecto hacia R5, excepto mensajes para el distrito 12 que saldrán hasta R4.

![Configuración R3](/img/debajodeSimilar%20a%20R1,salida%20por%20defecto%20camino%20a%20R5,excepto%20mensajes%20para%20el%20distrito%2012%20que%20saldrán%20hasta%20R4..png)

**R4:**  
Mensajes al distrito 2 viajarán a R3, el resto hasta R2.

![Configuración R4](/img/debajodeSimilar%20a%20R2,%20los%20mensajes%20a%20distrito%202%20viajarán%20a%20R3,%20el%20resto%20hasta%20R2..png)

**R5:**  
Deberemos especificar rutas hacia cada distrito, salida por defecto hacia el distrito 13.

![Configuración R5](/img/debajodeEn%20este%20caso%20sí%20deberemos%20especificar%20las%20rutas%20hacia%20cada%20distrito,%20la%20salida%20por%20defecto%20la%20dejaré%20mirando%20hacia%20el%20distrito%2013%20pensando%20a%20futuro,pues%20en%20cualquier%20caso%20no%20nos%20va%20a%20ahorrar%20líneas%20a%20la%20tabla%20de%20enrutamiento..png)

### Comprobación de conectividad

- Ping entre distritos:
  - Distrito 1 → Distrito 2  

![Ping Distrito 1](/img/debajode-Comprobación%20de%20ping%20entre%20distritos:Distrito1.png)

  - Distrito 1 → Distrito 11  

![Ping Distrito 2](/img/debajode-Comprobación%20de%20ping%20entre%20distritos:distrito2.png)

![Ping Distrito 11](/img/debajode-Comprobación%20de%20ping%20entre%20distritos:distrito11.png)

  - Distrito 1 → Distrito 12

![Ping Distrito 12](/img/debajode-Comprobación%20de%20ping%20entre%20distritos:distrito12.png)

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

![ACL R1](/img/debajodeCortar%20todo%20el%20trafico%20de%20R1,en%20mi%20opinion%20la%20mas%20eficiente%20y%20la%20que%20voy%20a%20usar,el%20inconveniente%20es%20que%20los%20mensajes%20provenientes%20de%20los%20demas%20distritos%20recorren%20un%20mayor%20camino%20antes%20de%20ser%20desechados%20por%20R1..png)

**Resultados:**

- Ping desde fuera → "administratively prohibited"

![Ping desde fuera hacia Distrito 1](/img/debajodePing%20desde%20fuera%20hacia%20Distrito%201..png)

- Ping desde dentro → timeout (por denegación al retorno)

![Ping desde Distrito 1 hacia fuera](/img/debajodePing%20desde%20Distrito%201%20hacia%20fuera.png)

---

> Los indigentes se comunican con los pobres, pero los demás distritos no quieren saber nada de ellos.

Se crea una **ACL extendida** en R4 para denegar tráfico hacia los distritos 1 y 2.

![ACL R4](/img/debajodeCrearemos%20una%20ACL%20extendida%20en%20la%20interfaz%20del%20switch%20de%20R4,%20para%20denegar%20todo%20el%20tráfico%20que%20se%20intente%20enviar%20a%20los%20distritos%201%20y%202..png)

Comprobamos ping desde el distrito 12.

![Comprobación ping desde distrito 12](/img/debajodeComprobamos%20ping%20a%20cada%20distrito%20desde%20el%2012..png)

---

> Los pobres y los pijos se alían y pueden comunicarse solo a través de R5.

Se modifica el enrutamiento de R2 y R4 para enviar tráfico por defecto a R5.  
No se necesita ACL nueva.

![Modificación enrutamiento 1](/img/debajodeAhora%20sí%20deberemos%20modificar%20nuestras%20tablas%20de%20enrutamiento%20de%20R2%20y%20R4.Enviaremos%20el%20tráfico%20por%20defecto%20a%20R5,%20tendremos%20que%20añadir%20la%20ruta%20entre%20R2%20y%20R4%20manualmente.imagen1de2.png)

![Modificación enrutamiento 2](/img/debajodeAhora%20sí%20deberemos%20modificar%20nuestras%20tablas%20de%20enrutamiento%20de%20R2%20y%20R4.Enviaremos%20el%20tráfico%20por%20defecto%20a%20R5,%20tendremos%20que%20añadir%20la%20ruta%20entre%20R2%20y%20R4%20manualmente.imagen2de2.png)

---

## Ejercicio 3: DHCP para los superpijos

Se monta un **servidor DHCP** en el router del distrito 1.  
Las máquinas deben recibir IP automáticamente (cinco primeras del rango), reservando la primera para el router.

### Pasos:

1. Excluir la IP del router.

![Excluir IP del router](/img/debajodeExcluimos%20la%20IP%20del%20router%20y%20las%20que%20no%20queremos%20que%20sean%20asignadas.Excluimos%20la%20IP%20del%20router%20y%20las%20que%20no%20queremos%20que%20sean%20asignadas..png)

2. Configurar parámetros del servidor DHCP.

![Configurar DHCP](/img/debajodeAhora%20configuramos%20los%20parámetros%20del%20servidor%20DHCP.png)

3. Comprobar asignación automática de IPs.

![Comprobación DHCP 1](/img/debajodeComprobamos%20su%20funcionamientoimagen1de3.png)

![Comprobación DHCP 2](/img/debajodeComprobamos%20su%20funcionamientoimagen2de3.png)

![Comprobación DHCP 3](/img/debajodeComprobamos%20su%20funcionamientoimagen3de3.png)

---

## Ejercicio 4: ACL por relaciones personales

> Peeta establece alianza con Clove.  
> Katniss deja de hablarse con Rue.  
> Katniss y Cato se comunican.

Como el tráfico del distrito 12 estaba bloqueado, se reescribe la **ACL extendida**:

![ACL extendida 1](/img/debajodeComo%20anteriormente%20se%20denegó%20todo%20el%20tráfico%20proveniente%20del%20Distrito%2012%20debemos%20reescribir%20dicha%20ACL,permitiendo%20las%20comunicaciones%20que%20se%20indican,será%20una%20ACL%20extendida.imagen1de2.png)

![ACL extendida 2](/img/debajodeComo%20anteriormente%20se%20denegó%20todo%20el%20tráfico%20proveniente%20del%20Distrito%2012%20debemos%20reescribir%20dicha%20ACL,permitiendo%20las%20comunicaciones%20que%20se%20indican,será%20una%20ACL%20extendida.imagen2de2.png)

- Katniss ↔ Peeta, Cato, Thresh  
- Peeta ↔ Katniss, Clove, Distrito 11  

**Comprobaciones:**  
Ping en ambos sentidos, con timeout cuando está denegado.

![Comprobación Katniss 1](/img/debajode%20%20%20%20%20%20%20-Katniss%20solo%20puede%20comunicarse%20con%20Peeta,Cato%20y%20Thresh.imagen1de2.png)

![Comprobación Katniss 2](/img/debajode%20%20%20%20%20%20%20-Katniss%20solo%20puede%20comunicarse%20con%20Peeta,Cato%20y%20Thresh.imagen2de2.png)

Si intentamos hacer un ping denegado en sentido contrario volveremos a encontrarnos con el mensaje de timeout anteriormente explicado.

![Timeout ping inverso](/img/debajodeSi%20intentamos%20hacer%20un%20ping%20denegado%20en%20sentido%20contrario%20volveremos%20a%20encontrarnos%20con%20el%20mensaje%20de%20timeout%20anteriormente%20explicado..png)

> Cato y Thresh se pelean.

Se deniega comunicación con una ACL extendida (puede estar en R2, R3 o R5).

![Denegar Cato-Thresh 1](/img/debajodeDenegamos%20la%20comunicación%20con%20una%20ACL%20extendida,podemos%20colocarla%20tanto%20en%20R2%20como%20R3%20y%20R5,en%20cualquiera%20de%20los%20casos%20al%20menos%20uno%20de%20los%20mensajes%20tendrán%20que%20recorrer%20más%20de%20un%20router%20antes%20de%20ser%20eliminado.imagen1de3.png)

![Denegar Cato-Thresh 2](/img/debajodeDenegamos%20la%20comunicación%20con%20una%20ACL%20extendida,podemos%20colocarla%20tanto%20en%20R2%20como%20R3%20y%20R5,en%20cualquiera%20de%20los%20casos%20al%20menos%20uno%20de%20los%20mensajes%20tendrán%20que%20recorrer%20más%20de%20un%20router%20antes%20de%20ser%20eliminado.imagen2de3.png)

![Denegar Cato-Thresh 3](/img/debajodeDenegamos%20la%20comunicación%20con%20una%20ACL%20extendida,podemos%20colocarla%20tanto%20en%20R2%20como%20R3%20y%20R5,en%20cualquiera%20de%20los%20casos%20al%20menos%20uno%20de%20los%20mensajes%20tendrán%20que%20recorrer%20más%20de%20un%20router%20antes%20de%20ser%20eliminado.imagen3de3.png)

---

## Ejercicio 5: Servidor web del distrito 13

Se monta un **servidor Apache** accesible solo desde los distritos 11 y 12 (puerto 80).

### Pasos:

1. Sustituir VPCS por Debian con Apache2.

![Montar servidor](/img/debajodePara%20montar%20el%20servidor%20sustituiremos%20la%20máquina%20VPCS%20por%20un%20Debian%20al%20que%20le%20instalaremos%20Apache,le%20daremos%20acceso%20a%20una%20nube%20NAT%20momentáneamente..png)

2. Asignar IP estática.

![Instalar Apache 1](/img/debajodeInstalamos%20Apache2%20y%20le%20damos%20una%20IP%20estática,ya%20podemos%20quitar%20la%20nube.imagen1de2.png)

![Instalar Apache 2](/img/debajodeInstalamos%20Apache2%20y%20le%20damos%20una%20IP%20estática,ya%20podemos%20quitar%20la%20nube.imagen2de2.png)

Si hacemos ping desde las distintas máquinas veremos que tenemos acceso desde los Distritos 2 y 11.

![Ping inicial](/img/debajodeSi%20hacemos%20ping%20desde%20las%20distintas%20máquinas%20veremos%20que%20tenemos%20acceso%20desde%20los%20Distritos%202%20y%2011..png)

En primer lugar modificaremos la ACL de R4 para permitirle el acceso al distrito 12.

3. Modificar ACLs:

   - En **R4** permitir acceso del distrito 12 antes del `deny ip any any`.

![ACL R4 orden 1](/img/debajodeComo%20las%20ACL%20se%20leen%20en%20orden%20debemos%20añadir%20la%20línea%20que%20permita%20el%20paso%20antes%20de%20%27deny%20ip%20any%20any%27.imagen1de2.png)

![ACL R4 orden 2](/img/debajodeComo%20las%20ACL%20se%20leen%20en%20orden%20debemos%20añadir%20la%20línea%20que%20permita%20el%20paso%20antes%20de%20%27deny%20ip%20any%20any%27.imagen2de2.png)

El '45' colocará la regla justo antes del deny any. - Comprobación:

![Comprobación ACL R4](/img/debajodeEl%20%2745%27%20colocará%20la%20regla%20justo%20antes%20del%20deny%20any.-comprobacion:.png)

Ahora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida.

   - En **R3** denegar acceso del distrito 2.

![Denegar distrito 2](/img/debajodeAhora%20denegamos%20el%20paso%20al%20distrito%202%20desde%20R3%20de%20igual%20forma%20modificando%20la%20ACL%20ya%20establecida..png)

Comprobación:

![Comprobación denegación](/img/debajodeAhora%20denegamos%20el%20paso%20al%20distrito%202%20desde%20R3%20de%20igual%20forma%20modificando%20la%20ACL%20ya%20establecida.-comprobacion:.png)

Ahora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.

   - En **R5** permitir solo puerto 80.

![ACL puerto 80 - 1](/img/debajodeAhora%20que%20solo%20tienen%20acceso%20los%20Distritos%2011%20y%2012%20cortaremos%20este%20a%20únicamente%20el%20puerto%2080%20mediante%20una%20ACL%20en%20R5.imagen1de2.png)

![ACL puerto 80 - 2](/img/debajodeAhora%20que%20solo%20tienen%20acceso%20los%20Distritos%2011%20y%2012%20cortaremos%20este%20a%20únicamente%20el%20puerto%2080%20mediante%20una%20ACL%20en%20R5.imagen2de2.png)

### Comprobaciones:

- Ping bloqueado (ICMP ≠ puerto 80).

![Ping bloqueado](/img/debajodeSi%20ahora%20probamos%20a%20volver%20a%20hacer%20un%20ping%20nos%20encontramos%20con%20que%20la%20ACL%20nos%20lo%20cortará,esto%20es%20debido%20a%20que%20el%20protocolo%20ICMP(ping)%20no%20trabaja%20en%20el%20puerto%2080..png)

- Acceso web permitido desde distritos 11 y 12 (navegador Firefox en TinyCore).

Para comprobar que el servidor web es accesible desde los distritos 11 y 12 vamos a añadir 1 tinycore con firefox al switch de dichos distritos.

![Añadir TinyCore](/img/debajodePara%20comprobar%20que%20el%20servidor%20web%20es%20accesible%20desde%20los%20distritos%2011%20y%2012%20vamos%20a%20añadir%201%20tinycore%20con%20firefox%20al%20switch%20de%20dichos%20distritos..png)

Será necesario configurar la IP de ambas máquinas en rango. Una vez hecho podremos acceder al servidor web.

![Acceso web desde distritos](/img/debajodeSerá%20necesario%20configurar%20la%20IP%20de%20ambas%20máquinas%20en%20rango.Una%20vez%20hecho%20podremos%20acceder%20al%20servidor%20web..png)

---

**Fin del documento**
