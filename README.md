# Práctica 1 — Ataques de Capa 2 y sus Contramedidas

> **Estudiante:** Emmanuel Báez Ramírez
> **Matrícula:** 2022-0375
> **Playlist (todos los videos):** https://www.youtube.com/playlist?list=PLp7pfUFf22-zekAmQ7hncCvmJHZe7lLHk

Documentación técnica completa de la Práctica 1. Reúne los cinco ataques de capa 2 ejecutados sobre una topología de laboratorio en GNS3, mostrando en cada caso el ataque y su contramedida. Cada ataque cuenta además con su propio repositorio independiente.

## Repositorios y videos

| # | Ataque | Repositorio | Video |
|---|--------|-------------|-------|
| 1 | DoS por CDP | https://github.com/Ca0nab0/CDPDOSSegRed-P1 | https://youtu.be/iwnL7N4eYz4 |
| 2 | MitM por ARP | https://github.com/Ca0nab0/ARPMitMSegRed-P1 | https://youtu.be/GlReQ8H1rlI |
| 3 | DHCP Starvation | https://github.com/Ca0nab0/DHCPStarvationSegRed-P1 | https://youtu.be/uSBldC9d_8k |
| 4 | MAC Flooding | https://github.com/Ca0nab0/MACFloodingSegRed-P1 | https://youtu.be/_l7GSrS0wds |
| 5 | STP Root Claim | https://github.com/Ca0nab0/STPRootSegRed-P1 | https://youtu.be/jWbHWWDFrkk |

> **Nota:** por motivos de tiempo no se incluyó el ataque de DHCP Spoofing; los cinco ataques restantes se entregan completos con script, documentación, capturas y video.

---

# 1 · Ataque DoS mediante el protocolo CDP

> **Video:** https://youtu.be/iwnL7N4eYz4 · **Repositorio:** https://github.com/Ca0nab0/CDPDOSSegRed-P1

## Objetivo del laboratorio.
Demostrar de forma controlada un ataque de Denegación de Servicio (DoS) contra un switch Cisco abusando del protocolo CDP (Cisco Discovery Protocol), evidenciar su impacto sobre la tabla de vecinos y la CPU del equipo, e implementar y verificar la contramedida que lo mitiga.

## Objetivo del script.
Inundar al switch con anuncios CDP de dispositivos vecinos falsos. Cada paquete usa una dirección MAC de origen aleatoria y un Device-ID único, por lo que el switch registra cada uno como un vecino nuevo. Esto satura la tabla de vecinos CDP y consume CPU y memoria del equipo, degradando su funcionamiento.

## Parámetros usados.
    sudo python3 ./cdp_dos.py -i eth1 -n 100 -p 500
- `-i eth1` : interfaz de red del atacante (interfaz hacia el switch).
- `-n 100`  : número de dispositivos falsos por ráfaga.
- `-p 500`  : relleno del campo SoftwareVersion (amplifica el tamaño del paquete).
- `-d`      : retardo entre paquetes en segundos (opcional, por defecto 0).
- `-c`      : número de ráfagas (opcional, 0 = infinito).

Elementos internos: `load_contrib("cdp")`, `RandMAC()`, encapsulado `Ether / LLC / SNAP (OUI 0x00000c, code 0x2000) / CDPv2_HDR`, `CDPMsgDeviceID` (SRV-VULN-...), `CDPMsgPlatform`, y `Ether(raw(pkt))` para recalcular checksums.

## Requisitos para utilizar la herramienta.
Python3, Scapy (`sudo apt install python3-scapy`), permisos root, conexión por LAN al switch víctima.

## Documentación del funcionamiento del script.
El script construye tramas CDP con el contrib de Scapy. Por cada ráfaga genera `n` paquetes con MAC aleatoria y Device-ID `SRV-VULN-<ráfaga>-<índice>`, enviados al multicast CDP `01:00:0c:cc:cc:cc` en LLC/SNAP. El switch los registra como vecinos nuevos, llenando la tabla y elevando la CPU. Corre hasta Ctrl+C.

## Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Cliente / víctima |

Imágenes: `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (SW1), `c3725-adventerprisek9-mz.124-15.T14` (R1). Mapa de puertos: Gi0/0 -> R1, Gi0/1 -> PC1, Gi0/2 -> Kali.

## Capturas de pantalla.
Topología (Emmanuel Báez 2022-0375):
<img width="516" alt="cdp_topologia" src="https://github.com/user-attachments/assets/aa28611a-8d5e-4605-ad6a-06bc7fcaa4cb" />

Ejecución en Kali:
<img width="770" alt="cdp_ejecucion" src="https://github.com/user-attachments/assets/371e09ec-a564-4395-a1e0-e71b0de3c7cd" />

Tabla CDP saturada:
<img width="683" alt="cdp_neighbors" src="https://github.com/user-attachments/assets/25051e75-bd07-4bbe-8dc3-5e95f6aa511e" />

Captura en Wireshark:
<img width="737" alt="cdp_wireshark" src="https://github.com/user-attachments/assets/33284be3-67f0-4e7c-9abb-6e0ec3c83cc6" />

Impacto en la CPU:
<img width="667" alt="cdp_cpu" src="https://github.com/user-attachments/assets/1eb8a04e-60da-4d38-88b5-8ad19cfcbe04" />

## Documentación de contra-medidas.
Deshabilitar CDP donde no se necesita.

    SW1(config)# no cdp run
    ! o por puerto:
    SW1(config-if)# no cdp enable

Verificación: `show cdp`, `show cdp neighbors`. Con CDP deshabilitado la tabla deja de crecer y la CPU se estabiliza.

---

# 2 · Ataque MitM mediante ARP

> **Video:** https://youtu.be/GlReQ8H1rlI · **Repositorio:** https://github.com/Ca0nab0/ARPMitMSegRed-P1

## Objetivo del laboratorio.
Demostrar de forma controlada un ataque Man-in-the-Middle (MitM) mediante envenenamiento de la tabla ARP, situando al atacante en medio del tráfico entre la víctima y el gateway, evidenciar la captura del tráfico, e implementar y verificar la contramedida que lo mitiga.

## Objetivo del script.
Suplantar al router (gateway) y al dispositivo final como intermediario para capturar el tráfico. Envenena las cachés ARP de víctima y gateway para que cada uno asocie la IP del otro con la MAC del atacante; activa IP forwarding (MitM transparente) y restaura las tablas al detenerse.

## Parámetros usados.
    sudo python3 ./arp_mitm.py -i eth1 -t 10.3.75.131 -g 10.3.75.129
- `-i eth1` : interfaz del atacante.
- `-t 10.3.75.131` : IP de la víctima (PC1).
- `-g 10.3.75.129` : IP del gateway (R1).

Elementos internos: `ARP(op=2)` (is-at falso), `packet_log()` (ICMP/DNS/HTTP), `Raw.load`, activación de forwarding y restauración al salir.

## Requisitos para utilizar la herramienta.
El script activa el forwarding automáticamente (`echo 1 > /proc/sys/net/ipv4/ip_forward`) para que la víctima NO pierda conexión. Python3, Scapy, permisos root, conexión por LAN.

## Documentación del funcionamiento del script.
Resuelve las MAC reales y envía respuestas ARP falsas (`op=2`) a ambos extremos. Con el forwarding activo reenvía el tráfico a su destino real (MitM transparente). `packet_log()` inspecciona ICMP, DNS y HTTP. Al detener (Ctrl+C) restaura las tablas y desactiva el forwarding.

## Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Víctima |

Imágenes: `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (SW1), `c3725-adventerprisek9-mz.124-15.T14` (R1).

## Capturas de pantalla.
Topología (Emmanuel Báez 2022-0375):
<img width="426" alt="arp_topologia" src="https://github.com/user-attachments/assets/439b58cc-33ae-4d38-aea3-bec80aed436c" />

Ejecución (forwarding y MACs resueltas):
<img width="661" alt="arp_ejecucion" src="https://github.com/user-attachments/assets/858b7956-250b-48eb-8213-53bb6e5cee5b" />

Tráfico interceptado:
<img width="715" alt="arp_trafico" src="https://github.com/user-attachments/assets/ed6e9ff1-293f-4854-8984-5bfa5564ca50" />

ARP falsos en Wireshark:
<img width="930" alt="arp_wireshark" src="https://github.com/user-attachments/assets/691cd061-3b07-4ab1-87b2-1402c2bd1282" />

## Documentación de contra-medidas.
Dynamic ARP Inspection (DAI), requiere DHCP Snooping:

    SW1(config)# ip dhcp snooping
    SW1(config)# ip dhcp snooping vlan 130
    SW1(config)# ip arp inspection vlan 130
    SW1(config)# interface Gi0/0
    SW1(config-if)# ip dhcp snooping trust
    SW1(config-if)# ip arp inspection trust

Verificación: `show ip arp inspection statistics`. Otras: ARP estático en R1, VPN, HTTPS/TLS.

---

# 3 · Ataque DHCP Starvation

> **Video:** https://youtu.be/uSBldC9d_8k · **Repositorio:** https://github.com/Ca0nab0/DHCPStarvationSegRed-P1

## Objetivo del laboratorio.
Demostrar de forma controlada un ataque DHCP Starvation contra el servidor DHCP de la red, agotando su pool de direcciones para impedir que los clientes legítimos obtengan IP, e implementar y verificar la contramedida que lo mitiga.

## Objetivo del script.
Agotar el pool del servidor DHCP (R1) enviando DISCOVER con MACs falsas aleatorias. El servidor reserva una dirección por cada MAC, hasta agotar el pool; a partir de ahí ningún cliente legítimo obtiene IP.

## Parámetros usados.
    sudo python3 ./dhcp_starvation.py -i eth1 -d 0.05
- `-i eth1` : interfaz del atacante.
- `-d 0.05` : retardo entre DISCOVER.
- `-c`      : número de DISCOVER (opcional, 0 = infinito).

Elementos internos: MAC aleatoria por paquete, encapsulado `Ether / IP / UDP / BOOTP / DHCP` con `message-type = discover`, `xid` aleatorio, `flags = 0x8000` (broadcast).

## Requisitos para utilizar la herramienta.
Python3, Scapy, permisos root, conexión por LAN, servidor DHCP activo (R1) con pool que agotar.

## Documentación del funcionamiento del script.
Por cada iteración genera una MAC aleatoria y construye un DISCOVER con esa MAC como `chaddr`, enviado en broadcast. El servidor reserva una IP por cada MAC falsa, consumiendo el pool. La máquina auxiliar Rocky (vía Cloud1/VMnet1 -> Gi1/0) evidencia el impacto: con el pool agotado no obtiene IP.

## Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.132 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.130 | Víctima |
| Rocky Linux (auxiliar) | ens160 -> Cloud1 (VMnet1) -> Gi1/0 | 130 | 10.3.75.131 | Cliente auxiliar de prueba |

El pool DHCP de R1 reparte el rango 10.3.75.130 - 10.3.75.254.

> **Nota:** la máquina auxiliar Rocky Linux se conecta a través de un nodo Cloud1 (adaptador VMware VMnet1) enlazado a Gi1/0 del switch, como cliente legítimo para evidenciar el impacto del ataque.

## Capturas de pantalla.
Topología (Emmanuel Báez 2022-0375):
<img width="457" alt="starv_topologia" src="https://github.com/user-attachments/assets/b99bb98f-0dba-4d42-900f-994f68968f3b" />

Ejecución (DISCOVER con MACs falsas):
<img width="572" alt="starv_ejecucion" src="https://github.com/user-attachments/assets/86ecbfc8-3584-47b0-8c74-123379097f78" />

Inundación en Wireshark:
<img width="1218" alt="starv_wireshark" src="https://github.com/user-attachments/assets/77799780-59f6-4c60-8f8d-762e6fdae0a8" />

Impacto: Rocky no obtiene IP (pool agotado):
<img width="761" alt="starv_impacto" src="https://github.com/user-attachments/assets/34faf8cf-29d5-496a-9135-4ab0555dc57a" />

<img width="527" alt="starv_r1" src="https://github.com/user-attachments/assets/dc5e7c14-cefb-4df1-a719-5ab9873f3c8b" />

## Documentación de contra-medidas.
Port Security (limita MACs por puerto) + rate-limit de DHCP Snooping:

    SW1(config)# interface Gi0/2
    SW1(config-if)# switchport port-security
    SW1(config-if)# switchport port-security maximum 2
    SW1(config-if)# switchport port-security violation shutdown

Verificación: `show port-security interface Gi0/2`. El puerto entra en err-disabled y el pool queda disponible.

---

# 4 · Ataque MAC Flooding

> **Video:** https://youtu.be/_l7GSrS0wds · **Repositorio:** https://github.com/Ca0nab0/MACFloodingSegRed-P1

## Objetivo del laboratorio.
Demostrar de forma controlada un ataque MAC Flooding contra un switch Cisco, saturando su tabla de direcciones MAC (tabla CAM) para forzar un comportamiento inseguro, e implementar y verificar la contramedida que lo mitiga.

## Objetivo del script.
Inundar la tabla CAM con miles de tramas de MAC origen aleatoria. Al saturarse, algunos switches difunden el tráfico por todos los puertos como un hub, permitiendo interceptar comunicaciones ajenas.

## Parámetros usados.
    sudo python3 ./mac_flooding.py -i eth1 -n 1000
- `-i eth1` : interfaz del atacante.
- `-n 1000` : tramas por ráfaga.
- `-d`      : retardo entre tramas (opcional, por defecto 0).
- `-c`      : número de ráfagas (opcional, 0 = infinito).

Elementos internos: `RandMAC()`, `RandIP()`, encapsulado `Ether / IP / UDP` (puertos 1234 -> 80), envío por ráfagas con `sendp()`.

## Requisitos para utilizar la herramienta.
Python3, Scapy, permisos root, conexión por LAN al switch víctima.

## Documentación del funcionamiento del script.
Genera tramas con MAC origen aleatoria (`RandMAC()`) por cada trama. El switch aprende cada MAC en el puerto del atacante; como nunca se repiten, la tabla CAM crece sin control (progresión observada: 977 -> 2445 -> 2943 entradas). Corre hasta Ctrl+C.

## Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.137 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.130 | Cliente / víctima |

Imágenes: `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (SW1), `c3725-adventerprisek9-mz.124-15.T14` (R1).

## Capturas de pantalla.
Topología (Emmanuel Báez 2022-0375):
<img width="426" alt="mac_topologia" src="https://github.com/user-attachments/assets/d84ed783-89a2-44c8-9eb8-943531bd2c44" />

Ejecución en Kali:
<img width="388" alt="mac_ejecucion" src="https://github.com/user-attachments/assets/6495294b-2322-479a-80cb-532076ef78b6" />

Tabla MAC inicial:
<img width="396" alt="mac_977" src="https://github.com/user-attachments/assets/481875ec-7ff8-40e4-8963-e6e82c08e94a" />

Tabla saturándose (2445 y 2943):
<img width="395" alt="mac_2445" src="https://github.com/user-attachments/assets/40578c4c-8b7c-43e1-9586-e985cea53be5" />

<img width="282" alt="mac_2943" src="https://github.com/user-attachments/assets/6c7d40f3-f5b9-4a7b-a131-0078d443b181" />

Avalancha en Wireshark:
<img width="633" alt="mac_wireshark" src="https://github.com/user-attachments/assets/77107f27-a402-4a35-8e9b-4ff497c0c760" />

## Documentación de contra-medidas.
Port Security:

    SW1(config)# interface Gi0/2
    SW1(config-if)# switchport port-security
    SW1(config-if)# switchport port-security maximum 2
    SW1(config-if)# switchport port-security mac-address sticky
    SW1(config-if)# switchport port-security violation shutdown

Verificación: `show port-security interface Gi0/2`, `show mac address-table count`. Al superar el límite, el puerto entra en err-disabled.

---

# 5 · Ataque STP Root Claim (Root Bridge Hijack)

> **Video:** https://youtu.be/jWbHWWDFrkk · **Repositorio:** https://github.com/Ca0nab0/STPRootSegRed-P1

## Objetivo del laboratorio.
Demostrar de forma controlada un ataque STP Root Claim, en el que el atacante se proclama Root Bridge del árbol de Spanning-Tree para alterar la topología lógica y forzar que el tráfico pase por él, e implementar y verificar la contramedida que lo mitiga.

## Objetivo del script.
Inyectar BPDUs de configuración con prioridad 0 para ganar la elección de Root Bridge. Al anunciar prioridad 0 con la MAC del atacante, la red recalcula la topología tomando a Kali como raíz.

## Parámetros usados.
    sudo python3 ./stp_root.py -i eth1 -p 0
- `-i eth1` : interfaz del atacante.
- `-p 0`    : prioridad del bridge (0 = la más baja, gana).
- `-d`      : intervalo de envío (opcional, por defecto 2s = hello time).
- `-c`      : número de BPDUs (opcional, 0 = infinito).

Elementos internos: encapsulado `Dot3 / LLC / STP` (multicast `01:80:c2:00:00:00`), `rootid = 0` y `bridgeid = 0` con la MAC de la interfaz, envío cada hello time.

## Requisitos para utilizar la herramienta.
Python3, Scapy, permisos root, conexión por LAN en un puerto que acepte BPDUs (sin BPDU Guard activo).

## Documentación del funcionamiento del script.
Construye BPDUs con prioridad 0 y la MAC de la interfaz como raíz, enviadas al multicast STP cada hello time (2s). Al ser la prioridad más baja, STP elige al atacante como raíz. Observado: la raíz cambia de SW1 (prioridad 32898) a Kali (prioridad 0, MAC 000c.2946.84fa); Gi0/2 pasa a Root Port. Corre hasta Ctrl+C.

## Documentación de la Red.
Topología en VLAN 130 / 10.3.75.128/25.

| Dispositivo | Interfaz | VLAN | Dirección IP | Rol |
|-------------|----------|------|--------------|-----|
| R1 (c3725) | Fa0/0 | 130 | 10.3.75.129 | Gateway / Servidor DHCP |
| SW1 (vIOS-L2) | — | 130 | — | Switch de acceso (víctima) |
| Kali (atacante) | eth1 -> Gi0/2 | 130 | 10.3.75.133 | Atacante |
| PC1 (VPCS) | -> Gi0/1 | 130 | 10.3.75.131 | Cliente / víctima |

Imágenes: `vios_l2-adventerprisek9-m.vmdk.SSA.152-4.0.55.E` (SW1), `c3725-adventerprisek9-mz.124-15.T14` (R1).

Datos del árbol STP observados: antes, Root = SW1 (prioridad 32898, MAC 0cca.0c59.0000); durante, Root = atacante (prioridad 0, MAC 000c.2946.84fa), Gi0/2 como Root Port.

## Capturas de pantalla.
Topología (Emmanuel Báez 2022-0375):
<img width="426" alt="stp_topologia" src="https://github.com/user-attachments/assets/0436355c-0492-4dd7-b039-7750cf1d3a37" />

Ejecución (BPDUs prioridad 0):
<img width="428" alt="stp_ejecucion" src="https://github.com/user-attachments/assets/3f014ad9-c180-4794-9ec9-38c3d90f609a" />

STP antes (SW1 es la raíz):
<img width="536" alt="stp_antes" src="https://github.com/user-attachments/assets/71abf04f-176f-4b03-8e1f-f1758603dd68" />

STP durante (raíz = Kali, prioridad 0):
<img width="727" alt="stp_durante" src="https://github.com/user-attachments/assets/1695acbf-38ec-4bf2-9bf0-3f4c32193149" />

BPDUs falsas en Wireshark:
<img width="1433" alt="stp_wireshark" src="https://github.com/user-attachments/assets/078f6040-70b1-4533-8f73-3e8d9bf4cdec" />

## Documentación de contra-medidas.
BPDU Guard (+ Root Guard):

    SW1(config)# interface Gi0/2
    SW1(config-if)# spanning-tree portfast
    SW1(config-if)# spanning-tree bpduguard enable
    ! Opcional global:
    SW1(config)# spanning-tree portfast bpduguard default
    ! Root Guard hacia otros switches:
    SW1(config-if)# spanning-tree guard root

Verificación: `show spanning-tree inconsistentports`, `show interfaces status`. Al recibir la primera BPDU falsa, Gi0/2 entra en err-disabled y SW1 vuelve a ser raíz.

---

*Documentación de la Práctica 1 — Seguridad en Redes. Emmanuel Báez Ramírez · 2022-0375.*
