---
title: "Hunger Games"
date: 2025-10-11T23:06:17+02:00
description: "Ejercicio de configuración de red y ACL - Hunger Games"
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


**R2:**  
Ignoramos el distrito 13, la comunicación para el distrito 1 saldrá hacia R1 y la salida por defecto será hacia R4.


**R3:**  
Salida por defecto hacia R5, excepto mensajes para el distrito 12 que saldrán hasta R4.


**R4:**  
Mensajes al distrito 2 viajarán a R3, el resto hasta R2.


**R5:**  
Deberemos especificar rutas hacia cada distrito, salida por defecto hacia el distrito 13.


### Comprobación de conectividad

- Ping entre distritos:
  - Distrito 1 → Distrito 2  


  - Distrito 1 → Distrito 11  



  - Distrito 1 → Distrito 12


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


**Resultados:**

- Ping desde fuera → "administratively prohibited"


- Ping desde dentro → timeout (por denegación al retorno)


---

> Los indigentes se comunican con los pobres, pero los demás distritos no quieren saber nada de ellos.

Se crea una **ACL extendida** en R4 para denegar tráfico hacia los distritos 1 y 2.


Comprobamos ping desde el distrito 12.


---

> Los pobres y los pijos se alían y pueden comunicarse solo a través de R5.

Se modifica el enrutamiento de R2 y R4 para enviar tráfico por defecto a R5.  
No se necesita ACL nueva.



---

## Ejercicio 3: DHCP para los superpijos

Se monta un **servidor DHCP** en el router del distrito 1.  
Las máquinas deben recibir IP automáticamente (cinco primeras del rango), reservando la primera para el router.

### Pasos:

1. Excluir la IP del router.


2. Configurar parámetros del servidor DHCP.


3. Comprobar asignación automática de IPs.




---

## Ejercicio 4: ACL por relaciones personales

> Peeta establece alianza con Clove.  
> Katniss deja de hablarse con Rue.  
> Katniss y Cato se comunican.

Como el tráfico del distrito 12 estaba bloqueado, se reescribe la **ACL extendida**:



- Katniss ↔ Peeta, Cato, Thresh  
- Peeta ↔ Katniss, Clove, Distrito 11  

**Comprobaciones:**  
Ping en ambos sentidos, con timeout cuando está denegado.



Si intentamos hacer un ping denegado en sentido contrario volveremos a encontrarnos con el mensaje de timeout anteriormente explicado.


> Cato y Thresh se pelean.

Se deniega comunicación con una ACL extendida (puede estar en R2, R3 o R5).




---

## Ejercicio 5: Servidor web del distrito 13

Se monta un **servidor Apache** accesible solo desde los distritos 11 y 12 (puerto 80).

### Pasos:

1. Sustituir VPCS por Debian con Apache2.


2. Asignar IP estática.



Si hacemos ping desde las distintas máquinas veremos que tenemos acceso desde los Distritos 2 y 11.


En primer lugar modificaremos la ACL de R4 para permitirle el acceso al distrito 12.

3. Modificar ACLs:

   - En **R4** permitir acceso del distrito 12 antes del `deny ip any any`.



El '45' colocará la regla justo antes del deny any. - Comprobación:


Ahora denegamos el paso al distrito 2 desde R3 de igual forma modificando la ACL ya establecida.

   - En **R3** denegar acceso del distrito 2.


Comprobación:


Ahora que solo tienen acceso los Distritos 11 y 12 cortaremos este a únicamente el puerto 80 mediante una ACL en R5.

   - En **R5** permitir solo puerto 80.



### Comprobaciones:

- Ping bloqueado (ICMP ≠ puerto 80).


- Acceso web permitido desde distritos 11 y 12 (navegador Firefox en TinyCore).

Para comprobar que el servidor web es accesible desde los distritos 11 y 12 vamos a añadir 1 tinycore con firefox al switch de dichos distritos.


Será necesario configurar la IP de ambas máquinas en rango. Una vez hecho podremos acceder al servidor web.


---

**Fin del documento**
