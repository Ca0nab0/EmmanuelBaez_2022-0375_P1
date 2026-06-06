[README.md](https://github.com/user-attachments/files/28658645/README.md)
# CDPDOSSegRed-P1# Ataque DoS mediante el protocolo CDP

> **Nombre:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/iwnL7N4eYz4
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk
> **Repo Link:"** https://github.com/Ca0nab0/CDPDOSSegRed-P1

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque de Denegación de Servicio (DoS) contra un switch Cisco abusando del protocolo CDP (Cisco Discovery Protocol), evidenciar su impacto sobre la tabla de vecinos y la CPU del equipo, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Inundar al switch con anuncios CDP de dispositivos vecinos falsos. Cada paquete usa una dirección MAC de origen aleatoria y un Device-ID único, por lo que el switch registra cada uno como un vecino nuevo. Esto satura la tabla de vecinos CDP y consume CPU y memoria del equipo, degradando su funcionamiento.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./cdp_dos.py -i eth1 -n 100 -p 500

- `-i eth1` : interfaz de red del atacante (interfaz hacia el switch).
- `-n 100`  : número de dispositivos falsos por ráfaga.
- `-p 500`  : relleno del campo SoftwareVersion (amplifica el tamaño del paquete).
- `-d`      : retardo entre paquetes en segundos (opcional, por defecto 0).
- `-c`      : número de ráfagas (opcional, 0 = infinito).

Elementos internos del script:
- `load_contrib("cdp")` : carga el soporte de CDP en Scapy.
- `RandMAC()` : genera una MAC de origen aleatoria por cada paquete.
- Encapsulado `Ether / LLC / SNAP (OUI 0x00000c, code 0x2000) / CDPv2_HDR` : estructura correcta de una trama CDP.
- `CDPMsgDeviceID` : nombre de vecino falso único (SRV-VULN-...).
- `CDPMsgPlatform` : plataforma simulada (Cisco Nexus 9000).
- `Ether(raw(pkt))` : fuerza el recálculo de checksums antes de enviar.

# Requisitos para utilizar la herramienta.
- Python3
- Scapy (`sudo apt install python3-scapy`)
- Permisos root (los ataques de capa 2 requieren raw sockets).
- Estar conectado al switch víctima por LAN (puerto de acceso).

# Documentación del funcionamiento del script.
El script construye tramas CDP a mano usando el contrib oficial de Scapy. En un bucle infinito de ráfagas, por cada iteración genera `n` paquetes; cada uno lleva una MAC de origen aleatoria (`RandMAC()`) y un Device-ID único con el formato `SRV-VULN-<ráfaga>-<índice>`. Los paquetes se envían al destino multicast de CDP (`01:00:0c:cc:cc:cc`) encapsulados en LLC/SNAP. Como cada trama parece provenir de un dispositivo distinto, el switch las registra como vecinos nuevos, llenando su tabla de vecinos CDP y elevando el uso de CPU. El ataque corre hasta detenerse con Ctrl+C.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Cliente / víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

Mapa de puertos en SW1:
- Gi0/0 -> R1
- Gi0/1 -> PC1
- Gi0/2 -> Kali (atacante)

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)



<img width="516" height="305" alt="image" src="https://github.com/user-attachments/assets/aa28611a-8d5e-4605-ad6a-06bc7fcaa4cb" />


- Ejecución del script en Kali


<img width="770" height="407" alt="cdp_ejecucion" src="https://github.com/user-attachments/assets/371e09ec-a564-4395-a1e0-e71b0de3c7cd" />


- Tabla CDP del switch saturada (cientos de vecinos falsos SRV-VULN)



<img width="683" height="327" alt="cdp_neighbors_358" src="https://github.com/user-attachments/assets/25051e75-bd07-4bbe-8dc3-5e95f6aa511e" />


<img width="737" height="408" alt="cdp_wireshark" src="https://github.com/user-attachments/assets/33284be3-67f0-4e7c-9abb-6e0ec3c83cc6" />



- Impacto en la CPU del switch

<img width="667" height="161" alt="cdp_cpu_861" src="https://github.com/user-attachments/assets/1eb8a04e-60da-4d38-88b5-8ad19cfcbe04" />

# Documentación de contra-medidas.
La mitigación es deshabilitar CDP donde no se necesita. CDP no debe estar activo en puertos de acceso hacia usuarios.

Deshabilitar CDP globalmente:

    SW1# configure terminal
    SW1(config)# no cdp run

O deshabilitarlo solo en el puerto del atacante:

    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# no cdp enable

Verificación:

    SW1# show cdp
    SW1# show cdp neighbors

Con CDP deshabilitado, el switch deja de procesar estos paquetes: la tabla de vecinos no crece y la CPU se mantiene estable. Al relanzar el ataque ya no aparecen vecinos falsos.

Otras buenas prácticas:
- Mantener CDP solo en enlaces de infraestructura entre equipos de confianza.
- Monitorear el uso de CPU y el tamaño de la tabla de vecinos CDP.


# Ataque DHCP Starvation

> **Estudiante:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/uSBldC9d_8k
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk
> **Repo Link:"** https://github.com/Ca0nab0/DHCPStarvationSegRed-P1

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque DHCP Starvation contra el servidor DHCP de la red, agotando por completo su pool de direcciones para impedir que los clientes legítimos obtengan IP, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Agotar el pool de direcciones del servidor DHCP (R1) enviando una gran cantidad de mensajes DISCOVER, cada uno con una dirección MAC de origen falsa y aleatoria. El servidor interpreta cada DISCOVER como un cliente nuevo y le reserva una dirección, hasta que se queda sin direcciones disponibles. A partir de ese momento, ningún cliente legítimo puede obtener IP: es una Denegación de Servicio sobre el DHCP.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./dhcp_starvation.py -i eth1 -d 0.05

- `-i eth1` : interfaz de red del atacante.
- `-d 0.05` : retardo entre cada DISCOVER en segundos.
- `-c`      : número de DISCOVER a enviar (opcional, 0 = infinito).

Elementos internos del script:
- Generación de una MAC de origen aleatoria por cada paquete.
- Encapsulado `Ether / IP / UDP / BOOTP / DHCP` con `message-type = discover`.
- `xid` aleatorio por petición.
- `flags = 0x8000` (broadcast) para forzar la respuesta del servidor.

# Requisitos para utilizar la herramienta.
- Python3
- Scapy
- Permisos root
- Estar en la misma red por medio de LAN
- Un servidor DHCP activo en la red (R1) con un pool que agotar.

# Documentación del funcionamiento del script.
En un bucle, el script genera por cada iteración una dirección MAC aleatoria y construye un mensaje DHCP DISCOVER con esa MAC como origen y como identificador de cliente (`chaddr`). Los DISCOVER se envían en broadcast al servidor. Como cada uno aparenta provenir de un cliente distinto, el servidor reserva una dirección IP para cada MAC falsa, consumiendo su pool. El retardo (`-d`) controla la velocidad del ataque. El script imprime cada DISCOVER enviado con su MAC falsa, y corre hasta detenerse con Ctrl+C.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.132 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.130 | Víctima |
| Rocky Linux (auxiliar) | ens160 -> Cloud1 (VMnet1) -> Gi1/0 | 130 | 10.3.75.131 (DHCP) | Máquina auxiliar (cliente legítimo de prueba) |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

El pool DHCP de R1 reparte el rango 10.3.75.130 - 10.3.75.254.

> **Nota:** la máquina auxiliar Rocky Linux se conecta a la topología a través de un nodo Cloud1 (adaptador VMware VMnet1) enlazado a Gi1/0 del switch. Se utiliza como cliente legítimo para evidenciar el impacto del ataque: al agotarse el pool, no logra obtener dirección IP.

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)


<img width="457" height="360" alt="starv_topologia" src="https://github.com/user-attachments/assets/b99bb98f-0dba-4d42-900f-994f68968f3b" />

- Ejecución del ataque (DISCOVER con MACs falsas)



<img width="572" height="217" alt="starv_ejecucion" src="https://github.com/user-attachments/assets/86ecbfc8-3584-47b0-8c74-123379097f78" />

- Inundación de DISCOVER capturada en Wireshark


<img width="1218" height="360" alt="starv_wireshark" src="https://github.com/user-attachments/assets/77799780-59f6-4c60-8f8d-762e6fdae0a8" />)

- Impacto: un cliente legítimo (Rocky) no puede obtener IP por pool agotado



<img width="761" height="60" alt="starv_impacto_rocky" src="https://github.com/user-attachments/assets/34faf8cf-29d5-496a-9135-4ab0555dc57a" />



<img width="527" height="167" alt="starv_r1_locked" src="https://github.com/user-attachments/assets/dc5e7c14-cefb-4df1-a719-5ab9873f3c8b" />

# Documentación de contra-medidas.
La mitigación es Port Security, que limita cuántas direcciones MAC puede aprender el puerto del atacante. Como cada DISCOVER usa una MAC distinta, el switch detecta el exceso y bloquea el puerto. Se complementa con el rate-limit de DHCP Snooping.

    SW1# configure terminal
    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# switchport port-security
    SW1(config-if)# switchport port-security maximum 2
    SW1(config-if)# switchport port-security violation shutdown
    SW1(config-if)# exit

Opcional, límite de tasa con DHCP Snooping:

    SW1(config)# ip dhcp snooping
    SW1(config)# ip dhcp snooping vlan 130
    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# ip dhcp snooping limit rate 5

Verificación:

    SW1# show port-security interface GigabitEthernet0/2
    SW1# show interfaces status

Al intentar inundar con miles de MACs distintas, el puerto Gi0/2 entra en estado err-disabled (secure-shutdown): el atacante queda aislado y el pool del servidor permanece disponible para los clientes legítimos.

Otras buenas prácticas:
- DHCP Snooping para validar el origen de los mensajes DHCP.
- Monitoreo de la ocupación del pool del servidor DHCP.

# Ataque MAC Flooding

> **Nombre:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/_l7GSrS0wds
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk
> **Repo Link:"** https://github.com/Ca0nab0/MACFloodingSegRed-P1.git
---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque MAC Flooding contra un switch Cisco, saturando su tabla de direcciones MAC (tabla CAM) para forzar un comportamiento inseguro, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Inundar la tabla CAM del switch con miles de tramas, cada una con una dirección MAC de origen aleatoria y distinta. El switch aprende cada MAC y la almacena, hasta agotar el espacio de la tabla. Cuando la tabla se llena, algunos switches entran en modo "fail-open" y comienzan a difundir el tráfico por todos los puertos como un hub, lo que permitiría interceptar comunicaciones de otros equipos.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./mac_flooding.py -i eth1 -n 1000

- `-i eth1` : interfaz de red del atacante.
- `-n 1000` : número de tramas por ráfaga.
- `-d`      : retardo entre tramas en segundos (opcional, por defecto 0).
- `-c`      : número de ráfagas (opcional, 0 = infinito).

Elementos internos del script:
- `RandMAC()` : dirección MAC de origen aleatoria por cada trama.
- `RandIP()` : direcciones IP de origen/destino aleatorias.
- Encapsulado `Ether / IP / UDP` con puertos 1234 -> 80.
- Envío masivo por ráfagas mediante `sendp()`.

# Requisitos para utilizar la herramienta.
- Python3
- Scapy
- Permisos root
- Estar conectado al switch víctima por LAN (puerto de acceso).

# Documentación del funcionamiento del script.
El script genera tramas Ethernet en ráfagas. Por cada trama crea una dirección MAC de origen aleatoria (`RandMAC()`) y direcciones IP aleatorias, encapsuladas en UDP. Cada trama se envía por la interfaz del atacante. El switch, al recibir tramas con MACs de origen siempre distintas, las va aprendiendo y almacenando en su tabla CAM, asociadas al puerto del atacante. Como las MACs nunca se repiten, la tabla crece sin límite hasta saturarse. El script imprime el progreso por ráfagas y corre hasta detenerse con Ctrl+C.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.137 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.130 | Cliente / víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)



<img width="426" height="278" alt="mac_topologia" src="https://github.com/user-attachments/assets/d84ed783-89a2-44c8-9eb8-943531bd2c44" />

- Ejecución del script en Kali

<img width="388" height="157" alt="mac_ejecucion" src="https://github.com/user-attachments/assets/6495294b-2322-479a-80cb-532076ef78b6" />

- Tabla MAC del switch antes del ataque (pocas entradas)

<img width="396" height="228" alt="mac_tabla_977" src="https://github.com/user-attachments/assets/481875ec-7ff8-40e4-8963-e6e82c08e94a" />

- Tabla MAC saturándose durante el ataque (progresión 977 -> 2445 -> 2943 entradas)

<img width="395" height="192" alt="mac_tabla_2445" src="https://github.com/user-attachments/assets/40578c4c-8b7c-43e1-9586-e985cea53be5" />

<img width="282" height="190" alt="mac_tabla_2943" src="https://github.com/user-attachments/assets/6c7d40f3-f5b9-4a7b-a131-0078d443b181" />

- Avalancha de tramas con MACs aleatorias capturada en Wireshark

<img width="633" height="481" alt="mac_wireshark" src="https://github.com/user-attachments/assets/77107f27-a402-4a35-8e9b-4ff497c0c760" />

# Documentación de contra-medidas.
La mitigación es Port Security, que limita cuántas direcciones MAC puede aprender el puerto del atacante. Al superar el límite, el switch detecta la violación y bloquea el puerto.

    SW1# configure terminal
    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# switchport port-security
    SW1(config-if)# switchport port-security maximum 2
    SW1(config-if)# switchport port-security mac-address sticky
    SW1(config-if)# switchport port-security violation shutdown
    SW1(config-if)# exit

Verificación:

    SW1# show port-security interface GigabitEthernet0/2
    SW1# show mac address-table count
    SW1# show interfaces status

Con Port Security activo, al intentar inyectar más de 2 MACs el puerto Gi0/2 entra en estado err-disabled (secure-shutdown): el atacante queda aislado y la tabla CAM ya no se satura.

Otras buenas prácticas:
- Configurar Port Security en todos los puertos de acceso.
- Usar direcciones MAC sticky para registrar las MAC legítimas.
- Monitorear el tamaño de la tabla de direcciones MAC.

# Ataque MitM mediante ARP

> **Estudiante:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/GlReQ8H1rlI
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque Man-in-the-Middle (MitM) mediante envenenamiento de la tabla ARP, situando al atacante en medio del tráfico entre la víctima y el gateway, evidenciar la captura del tráfico, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Suplantar al router (gateway) y al dispositivo final, sirviendo como intermediario para capturar el tráfico entre ambos. El script envenena las cachés ARP de la víctima y del gateway para que cada uno asocie la IP del otro con la MAC del atacante; de esta forma todo el tráfico entre ellos pasa por el atacante, que lo analiza en la misma terminal. Activa el reenvío de paquetes (IP forwarding) para que el MitM sea transparente y restaura las tablas ARP al detenerse.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./arp_mitm.py -i eth1 -t 10.3.75.131 -g 10.3.75.129

- `-i eth1` : interfaz de red del atacante.
- `-t 10.3.75.131` : IP de la víctima (PC1).
- `-g 10.3.75.129` : IP del gateway (R1).

Elementos internos del script:
- `ARP(op=2)` : respuesta ARP falsa (is-at) enviada al router y al objetivo con la MAC del atacante.
- `packet_log()` : función de análisis del tráfico interceptado (ICMP, DNS, HTTP).
- `Raw.load` : lectura de contenido de paquetes HTTP (GET/POST).
- Activación de IP forwarding y restauración de tablas ARP al salir.

# Requisitos para utilizar la herramienta.
- Habilitar IP forwarding para que la máquina objetivo NO pierda su conexión (MitM transparente). El script lo activa automáticamente:

      echo 1 > /proc/sys/net/ipv4/ip_forward

- Python3
- Scapy
- Permisos root
- Estar en la misma red por medio de LAN

# Documentación del funcionamiento del script.
El script resuelve las direcciones MAC reales de la víctima y del gateway. Luego, en un bucle, envía respuestas ARP falsas (`ARP op=2`) a ambos: a la víctima le dice que la IP del gateway está en la MAC del atacante, y al gateway le dice que la IP de la víctima está en la MAC del atacante. Con el IP forwarding activo, el tráfico que pasa por el atacante se reenvía hacia su destino real, manteniendo la conexión y haciendo el ataque transparente. La función `packet_log()` inspecciona cada paquete que atraviesa al atacante e imprime origen, destino y protocolo (ICMP, DNS, HTTP). Al detener con Ctrl+C, el script reenvía ARP correctos para restaurar las tablas y desactiva el forwarding.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)



<img width="426" height="278" alt="arp_topologia" src="https://github.com/user-attachments/assets/439b58cc-33ae-4d38-aea3-bec80aed436c" />


- Ejecución del ataque (forwarding activado y MACs resueltas)



<img width="661" height="237" alt="arp_ejecucion" src="https://github.com/user-attachments/assets/858b7956-250b-48eb-8213-53bb6e5cee5b" />


- Tráfico interceptado en la terminal del atacante

 

<img width="715" height="288" alt="arp_trafico" src="https://github.com/user-attachments/assets/ed6e9ff1-293f-4854-8984-5bfa5564ca50" />

- ARP falsos (is-at) capturados en Wireshark


<img width="930" height="171" alt="arp_wireshark" src="https://github.com/user-attachments/assets/691cd061-3b07-4ab1-87b2-1402c2bd1282" />



# Documentación de contra-medidas.
La mitigación principal es Dynamic ARP Inspection (DAI), que valida los paquetes ARP contra la base de datos de DHCP Snooping y descarta los falsos. Requiere DHCP Snooping activo.

    SW1# configure terminal
    SW1(config)# ip dhcp snooping
    SW1(config)# ip dhcp snooping vlan 130
    SW1(config)# ip arp inspection vlan 130
    SW1(config)# interface GigabitEthernet0/0
    SW1(config-if)# ip dhcp snooping trust
    SW1(config-if)# ip arp inspection trust

Verificación:

    SW1# show ip arp inspection
    SW1# show ip arp inspection statistics

Con DAI activo, los ARP maliciosos del atacante (puerto no confiable) se descartan y la víctima vuelve a ver la MAC real del gateway.

Otras contramedidas:
- Tabla ARP estática en el router para las entradas críticas:

      R1(config)# arp 10.3.75.131 0050.7966.6800 arpa FastEthernet0/0

- Uso de VPN.
- Uso de HTTPS/TLS para cifrar el tráfico aunque sea interceptado.

# Ataque MitM mediante ARP

> **Estudiante:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/GlReQ8H1rlI
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk
> **Repo Link:"** https://github.com/Ca0nab0/ARPMitMSegRed-P1.git

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque Man-in-the-Middle (MitM) mediante envenenamiento de la tabla ARP, situando al atacante en medio del tráfico entre la víctima y el gateway, evidenciar la captura del tráfico, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Suplantar al router (gateway) y al dispositivo final, sirviendo como intermediario para capturar el tráfico entre ambos. El script envenena las cachés ARP de la víctima y del gateway para que cada uno asocie la IP del otro con la MAC del atacante; de esta forma todo el tráfico entre ellos pasa por el atacante, que lo analiza en la misma terminal. Activa el reenvío de paquetes (IP forwarding) para que el MitM sea transparente y restaura las tablas ARP al detenerse.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./arp_mitm.py -i eth1 -t 10.3.75.131 -g 10.3.75.129

- `-i eth1` : interfaz de red del atacante.
- `-t 10.3.75.131` : IP de la víctima (PC1).
- `-g 10.3.75.129` : IP del gateway (R1).

Elementos internos del script:
- `ARP(op=2)` : respuesta ARP falsa (is-at) enviada al router y al objetivo con la MAC del atacante.
- `packet_log()` : función de análisis del tráfico interceptado (ICMP, DNS, HTTP).
- `Raw.load` : lectura de contenido de paquetes HTTP (GET/POST).
- Activación de IP forwarding y restauración de tablas ARP al salir.

# Requisitos para utilizar la herramienta.
- Habilitar IP forwarding para que la máquina objetivo NO pierda su conexión (MitM transparente). El script lo activa automáticamente:

      echo 1 > /proc/sys/net/ipv4/ip_forward

- Python3
- Scapy
- Permisos root
- Estar en la misma red por medio de LAN

# Documentación del funcionamiento del script.
El script resuelve las direcciones MAC reales de la víctima y del gateway. Luego, en un bucle, envía respuestas ARP falsas (`ARP op=2`) a ambos: a la víctima le dice que la IP del gateway está en la MAC del atacante, y al gateway le dice que la IP de la víctima está en la MAC del atacante. Con el IP forwarding activo, el tráfico que pasa por el atacante se reenvía hacia su destino real, manteniendo la conexión y haciendo el ataque transparente. La función `packet_log()` inspecciona cada paquete que atraviesa al atacante e imprime origen, destino y protocolo (ICMP, DNS, HTTP). Al detener con Ctrl+C, el script reenvía ARP correctos para restaurar las tablas y desactiva el forwarding.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)



<img width="426" height="278" alt="arp_topologia" src="https://github.com/user-attachments/assets/439b58cc-33ae-4d38-aea3-bec80aed436c" />


- Ejecución del ataque (forwarding activado y MACs resueltas)



<img width="661" height="237" alt="arp_ejecucion" src="https://github.com/user-attachments/assets/858b7956-250b-48eb-8213-53bb6e5cee5b" />


- Tráfico interceptado en la terminal del atacante

 

<img width="715" height="288" alt="arp_trafico" src="https://github.com/user-attachments/assets/ed6e9ff1-293f-4854-8984-5bfa5564ca50" />

- ARP falsos (is-at) capturados en Wireshark


<img width="930" height="171" alt="arp_wireshark" src="https://github.com/user-attachments/assets/691cd061-3b07-4ab1-87b2-1402c2bd1282" />



# Documentación de contra-medidas.
La mitigación principal es Dynamic ARP Inspection (DAI), que valida los paquetes ARP contra la base de datos de DHCP Snooping y descarta los falsos. Requiere DHCP Snooping activo.

    SW1# configure terminal
    SW1(config)# ip dhcp snooping
    SW1(config)# ip dhcp snooping vlan 130
    SW1(config)# ip arp inspection vlan 130
    SW1(config)# interface GigabitEthernet0/0
    SW1(config-if)# ip dhcp snooping trust
    SW1(config-if)# ip arp inspection trust

Verificación:

    SW1# show ip arp inspection
    SW1# show ip arp inspection statistics

Con DAI activo, los ARP maliciosos del atacante (puerto no confiable) se descartan y la víctima vuelve a ver la MAC real del gateway.

Otras contramedidas:
- Tabla ARP estática en el router para las entradas críticas:

      R1(config)# arp 10.3.75.131 0050.7966.6800 arpa FastEthernet0/0

- Uso de VPN.
- Uso de HTTPS/TLS para cifrar el tráfico aunque sea interceptado.

# Ataque STP Root Claim (Root Bridge Hijack)

> **Estudiante:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/jWbHWWDFrkk
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque STP Root Claim, en el que el atacante se proclama Root Bridge del árbol de Spanning-Tree para alterar la topología lógica de la red y forzar que el tráfico pase por él, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Inyectar BPDUs (Bridge Protocol Data Units) de configuración con una prioridad de bridge muy baja (0) para ganar la elección de Root Bridge. Spanning-Tree elige como raíz al switch con la prioridad más baja; al anunciar prioridad 0 con la MAC del atacante, la red recalcula la topología tomando a Kali como raíz, otorgando al atacante control sobre las rutas del árbol.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./stp_root.py -i eth1 -p 0

- `-i eth1` : interfaz de red del atacante.
- `-p 0`    : prioridad del bridge (0 = la más baja posible, gana la elección).
- `-d`      : intervalo de envío en segundos (opcional, por defecto 2s = hello time).
- `-c`      : número de BPDUs a enviar (opcional, 0 = infinito).

Elementos internos del script:
- Encapsulado `Dot3 / LLC / STP` con destino multicast STP `01:80:c2:00:00:00`.
- `rootid = 0` y `bridgeid = 0` con la MAC de la interfaz como `rootmac`/`bridgemac`.
- Envío periódico cada hello time (2s) para mantener el rol de raíz.

# Requisitos para utilizar la herramienta.
- Python3
- Scapy
- Permisos root
- Estar conectado al switch víctima por LAN, en un puerto que acepte BPDUs (sin BPDU Guard activo).

# Documentación del funcionamiento del script.
El script construye BPDUs de configuración con la prioridad indicada (0) y la dirección MAC de la propia interfaz como identificador de raíz y de bridge. Las BPDUs se envían al destino multicast de STP cada hello time (2 segundos). Como la prioridad 0 es inferior a la de cualquier switch legítimo de la red, el algoritmo de Spanning-Tree elige al atacante como nuevo Root Bridge y recalcula la topología en consecuencia. El script imprime cada BPDU enviada y corre hasta detenerse con Ctrl+C.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Cliente / víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

Datos del árbol STP observados:
- Antes del ataque: Root Bridge = SW1, prioridad 32898, MAC 0cca.0c59.0000 ("This bridge is the root").
- Durante el ataque: Root Bridge = atacante, prioridad 0, MAC 000c.2946.84fa; Gi0/2 pasa a Root Port.

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)

<img width="426" height="278" alt="stp_topologia" src="https://github.com/user-attachments/assets/0436355c-0492-4dd7-b039-7750cf1d3a37" />

- Ejecución del script en Kali (BPDUs con prioridad 0)

<img width="428" height="236" alt="stp_ejecucion" src="https://github.com/user-attachments/assets/3f014ad9-c180-4794-9ec9-38c3d90f609a" />

- STP antes del ataque (SW1 es la raíz)

<img width="536" height="235" alt="stp_antes_sw1_root" src="https://github.com/user-attachments/assets/71abf04f-176f-4b03-8e1f-f1758603dd68" />

- STP durante el ataque (raíz = MAC de Kali, prioridad 0, Gi0/2 como Root Port)

<img width="727" height="313" alt="stp_durante_kali_root" src="https://github.com/user-attachments/assets/1695acbf-38ec-4bf2-9bf0-3f4c32193149" />

- BPDUs falsas y Topology Change capturadas en Wireshark

<img width="1433" height="440" alt="stp_wireshark" src="https://github.com/user-attachments/assets/078f6040-70b1-4533-8f73-3e8d9bf4cdec" />

# Documentación de contra-medidas.
La mitigación es BPDU Guard, que deshabilita automáticamente cualquier puerto de acceso donde se reciban BPDUs. Los puertos hacia clientes nunca deberían enviar BPDUs, por lo que recibir una indica un ataque o una conexión indebida.

    SW1# configure terminal
    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# spanning-tree portfast
    SW1(config-if)# spanning-tree bpduguard enable
    SW1(config-if)# exit

Opcionalmente, BPDU Guard global para todos los puertos PortFast:

    SW1(config)# spanning-tree portfast bpduguard default

Y Root Guard en puertos hacia switches donde no debe aparecer una raíz nueva:

    SW1(config-if)# spanning-tree guard root

Verificación:

    SW1# show spanning-tree summary
    SW1# show spanning-tree inconsistentports
    SW1# show interfaces status

Con BPDU Guard activo, al recibir la primera BPDU falsa el puerto Gi0/2 entra en estado err-disabled: el atacante queda aislado y SW1 vuelve a ser la raíz legítima.

Otras buenas prácticas:
- Activar BPDU Guard en todos los puertos de acceso.
- Usar Root Guard en enlaces hacia otros switches.
- Definir manualmente la prioridad del Root Bridge legítimo (por ejemplo, prioridad 0 o 4096 en el switch core).

# Ataque STP Root Claim (Root Bridge Hijack)

> **Estudiante:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Video ilustrativo:** https://youtu.be/jWbHWWDFrkk
> **Playlist (Práctica 1):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk
> **Repo Link:"** https://github.com/Ca0nab0/STPRootSegRed-P1

---

# Objetivo del laboratorio.
Demostrar de forma controlada un ataque STP Root Claim, en el que el atacante se proclama Root Bridge del árbol de Spanning-Tree para alterar la topología lógica de la red y forzar que el tráfico pase por él, e implementar y verificar la contramedida que lo mitiga.

# Objetivo del script.
Inyectar BPDUs (Bridge Protocol Data Units) de configuración con una prioridad de bridge muy baja (0) para ganar la elección de Root Bridge. Spanning-Tree elige como raíz al switch con la prioridad más baja; al anunciar prioridad 0 con la MAC del atacante, la red recalcula la topología tomando a Kali como raíz, otorgando al atacante control sobre las rutas del árbol.

# Parámetros usados.
Comando de ejecución:

    sudo python3 ./stp_root.py -i eth1 -p 0

- `-i eth1` : interfaz de red del atacante.
- `-p 0`    : prioridad del bridge (0 = la más baja posible, gana la elección).
- `-d`      : intervalo de envío en segundos (opcional, por defecto 2s = hello time).
- `-c`      : número de BPDUs a enviar (opcional, 0 = infinito).

Elementos internos del script:
- Encapsulado `Dot3 / LLC / STP` con destino multicast STP `01:80:c2:00:00:00`.
- `rootid = 0` y `bridgeid = 0` con la MAC de la interfaz como `rootmac`/`bridgemac`.
- Envío periódico cada hello time (2s) para mantener el rol de raíz.

# Requisitos para utilizar la herramienta.
- Python3
- Scapy
- Permisos root
- Estar conectado al switch víctima por LAN, en un puerto que acepte BPDUs (sin BPDU Guard activo).

# Documentación del funcionamiento del script.
El script construye BPDUs de configuración con la prioridad indicada (0) y la dirección MAC de la propia interfaz como identificador de raíz y de bridge. Las BPDUs se envían al destino multicast de STP cada hello time (2 segundos). Como la prioridad 0 es inferior a la de cualquier switch legítimo de la red, el algoritmo de Spanning-Tree elige al atacante como nuevo Root Bridge y recalcula la topología en consecuencia. El script imprime cada BPDU enviada y corre hasta detenerse con Ctrl+C.

# Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Cliente / víctima |

Imágenes usadas:
- `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (switch SW1)
- `c3725-adventerprisek9-mz.124-15.T14` (router R1)

Datos del árbol STP observados:
- Antes del ataque: Root Bridge = SW1, prioridad 32898, MAC 0cca.0c59.0000 ("This bridge is the root").
- Durante el ataque: Root Bridge = atacante, prioridad 0, MAC 000c.2946.84fa; Gi0/2 pasa a Root Port.

# Capturas de pantalla.
- Topología (Emmanuel Baez 20220375)

<img width="426" height="278" alt="stp_topologia" src="https://github.com/user-attachments/assets/0436355c-0492-4dd7-b039-7750cf1d3a37" />

- Ejecución del script en Kali (BPDUs con prioridad 0)

<img width="428" height="236" alt="stp_ejecucion" src="https://github.com/user-attachments/assets/3f014ad9-c180-4794-9ec9-38c3d90f609a" />

- STP antes del ataque (SW1 es la raíz)

<img width="536" height="235" alt="stp_antes_sw1_root" src="https://github.com/user-attachments/assets/71abf04f-176f-4b03-8e1f-f1758603dd68" />

- STP durante el ataque (raíz = MAC de Kali, prioridad 0, Gi0/2 como Root Port)

<img width="727" height="313" alt="stp_durante_kali_root" src="https://github.com/user-attachments/assets/1695acbf-38ec-4bf2-9bf0-3f4c32193149" />

- BPDUs falsas y Topology Change capturadas en Wireshark

<img width="1433" height="440" alt="stp_wireshark" src="https://github.com/user-attachments/assets/078f6040-70b1-4533-8f73-3e8d9bf4cdec" />

# Documentación de contra-medidas.
La mitigación es BPDU Guard, que deshabilita automáticamente cualquier puerto de acceso donde se reciban BPDUs. Los puertos hacia clientes nunca deberían enviar BPDUs, por lo que recibir una indica un ataque o una conexión indebida.

    SW1# configure terminal
    SW1(config)# interface GigabitEthernet0/2
    SW1(config-if)# spanning-tree portfast
    SW1(config-if)# spanning-tree bpduguard enable
    SW1(config-if)# exit

Opcionalmente, BPDU Guard global para todos los puertos PortFast:

    SW1(config)# spanning-tree portfast bpduguard default

Y Root Guard en puertos hacia switches donde no debe aparecer una raíz nueva:

    SW1(config-if)# spanning-tree guard root

Verificación:

    SW1# show spanning-tree summary
    SW1# show spanning-tree inconsistentports
    SW1# show interfaces status

Con BPDU Guard activo, al recibir la primera BPDU falsa el puerto Gi0/2 entra en estado err-disabled: el atacante queda aislado y SW1 vuelve a ser la raíz legítima.

Otras buenas prácticas:
- Activar BPDU Guard en todos los puertos de acceso.
- Usar Root Guard en enlaces hacia otros switches.
- Definir manualmente la prioridad del Root Bridge legítimo (por ejemplo, prioridad 0 o 4096 en el switch core).
