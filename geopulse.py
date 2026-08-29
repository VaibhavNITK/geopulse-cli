#!/usr/bin/env python3
"""
GeoPulse CLI — High-Performance Network Geolocation & Intelligence Engine
Author: Vaibhav Agrawal
License: MIT
"""

import sys
import os
import json
import urllib.request
import urllib.error
import socket
import time
import argparse
from datetime import datetime

# ANSI Color Tokens
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BLUE = "\033[34m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
   ______            ____  dWdzc2Ug
  / ____/__  ____   / __ \__  __/ ____/ / (_)
 / / __/ _ \/ __ \ / /_/ / / / / /   / / / /
/ /_/ /  __/ /_/ // ____/ / / / /___/ / / / 
\____/\___/\____//_/   /_/ /_/\____/_/_/_/  
{RESET}{DIM} High-Performance Network Geolocation & Intelligence Engine v2.0{RESET}
"""

def print_banner():
    if sys.stdout.isatty():
        os.system("clear" if os.name != "nt" else "cls")
        print(BANNER)

def resolve_domain(target):
    """Resolves domain name to IP address if needed."""
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        return target

def fetch_ip_info(ip_address=""):
    """Fetches geolocation data with multi-provider failover."""
    start_time = time.time()
    
    # Provider 1: ip-api.com
    url1 = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query,mobile,proxy,hosting"
    try:
        req = urllib.request.Request(url1, headers={'User-Agent': 'GeoPulse-CLI/2.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            latency = round((time.time() - start_time) * 1000, 2)
            if data.get("status") == "success":
                data["_latency_ms"] = latency
                data["_provider"] = "ip-api"
                return data
    except Exception:
        pass

    # Provider 2: ipapi.co fallback
    url2 = f"https://ipapi.co/{ip_address}/json/" if ip_address else "https://ipapi.co/json/"
    try:
        req = urllib.request.Request(url2, headers={'User-Agent': 'GeoPulse-CLI/2.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
            latency = round((time.time() - start_time) * 1000, 2)
            return {
                "status": "success",
                "query": raw.get("ip"),
                "country": raw.get("country_name"),
                "countryCode": raw.get("country_code"),
                "regionName": raw.get("region"),
                "city": raw.get("city"),
                "zip": raw.get("postal"),
                "lat": raw.get("latitude"),
                "lon": raw.get("longitude"),
                "timezone": raw.get("timezone"),
                "isp": raw.get("org"),
                "org": raw.get("org"),
                "as": raw.get("asn"),
                "_latency_ms": latency,
                "_provider": "ipapi.co"
            }
    except Exception:
        pass

    return {"status": "fail", "message": "Failed to resolve IP across all providers."}

def render_ascii_map(lat, lon):
    """Simple terminal map visualization."""
    grid = [
        "  +---------------------------------------------------+",
        "  |  N.America         |  Europe       |  Asia        |",
        "  |    [  *  ]         |     [   ]     |    [   ]     |",
        "  |--------------------+---------------+--------------|",
        "  |  S.America         |  Africa       |  Australia   |",
        "  |    [     ]         |     [   ]     |    [   ]     |",
        "  +---------------------------------------------------+"
    ]
    print(f"\n{BOLD}{YELLOW}📍 Coordinates:{RESET} {lat}, {lon}")
    print(f"{DIM}   Google Maps: https://maps.google.com/?q={lat},{lon}{RESET}\n")

def display_info(data, as_json=False):
    if as_json:
        print(json.dumps(data, indent=2))
        return

    if data.get("status") != "success":
        print(f"\n{RED}{BOLD}❌ Error:{RESET} {data.get('message', 'Unable to trace target.')}\n")
        return

    lat = data.get("lat", 0)
    lon = data.get("lon", 0)
    latency = data.get("_latency_ms", 0)
    provider = data.get("_provider", "Primary")

    print(f"  {BOLD}{GREEN}✔ Geolocation Query Successful{RESET} {DIM}({latency}ms via {provider}){RESET}")
    print(f"  {CYAN}{'='*56}{RESET}")

    items = [
        ("Target IP", data.get("query")),
        ("Country", f"{data.get('country')} ({data.get('countryCode')})"),
        ("Region / State", f"{data.get('regionName')} [{data.get('region', '')}]"),
        ("City / Postal", f"{data.get('city')}, {data.get('zip', 'N/A')}"),
        ("Latitude / Longitude", f"{lat}, {lon}"),
        ("Timezone", data.get("timezone")),
        ("Internet Service Provider", data.get("isp")),
        ("Organization", data.get("org")),
        ("Autonomous System (ASN)", data.get("as")),
        ("Security Features", f"Mobile: {data.get('mobile', False)} | Proxy/VPN: {data.get('proxy', False)} | Hosting: {data.get('hosting', False)}")
    ]

    for label, val in items:
        print(f"  {BOLD}{YELLOW}{label:<26}{RESET} {GREEN}▶{RESET}  {val}")

    print(f"  {CYAN}{'='*56}{RESET}")
    render_ascii_map(lat, lon)

def interactive_menu():
    print_banner()
    while True:
        print(f"  {BOLD}{CYAN}[ 1 ]{RESET} Trace Specific IP or Hostname")
        print(f"  {BOLD}{CYAN}[ 2 ]{RESET} Trace Your Own Public IP")
        print(f"  {BOLD}{CYAN}[ 3 ]{RESET} Interactive Batch Lookup")
        print(f"  {BOLD}{CYAN}[ 4 ]{RESET} About GeoPulse CLI")
        print(f"  {BOLD}{RED}[ x ]{RESET} Exit\n")
        
        choice = input(f"  {BOLD}{YELLOW}GeoPulse >> {RESET}").strip().lower()

        if choice in ["x", "exit", "q", "quit"]:
            print(f"\n  {GREEN}Thank you for using GeoPulse CLI! Bye.{RESET}\n")
            sys.exit(0)
        elif choice == "1":
            target = input(f"  {BOLD}Enter IP / Hostname: {RESET}").strip()
            if target:
                ip = resolve_domain(target)
                print(f"  {DIM}Resolving {target} -> {ip}...{RESET}")
                data = fetch_ip_info(ip)
                display_info(data)
        elif choice == "2":
            print(f"  {DIM}Tracing your public IP...{RESET}")
            data = fetch_ip_info("")
            display_info(data)
        elif choice == "3":
            raw_ips = input(f"  {BOLD}Enter space-separated IPs: {RESET}").strip().split()
            for item in raw_ips:
                ip = resolve_domain(item)
                print(f"\n  {BOLD}{BLUE}--- Results for {item} ({ip}) ---{RESET}")
                data = fetch_ip_info(ip)
                display_info(data)
        elif choice == "4":
            print_banner()
            print(f"  {BOLD}GeoPulse CLI v2.0{RESET}")
            print(f"  Author: Vaibhav Agrawal (D. E. Shaw & Co. / NITK)")
            print(f"  Architecture: Failover Multi-Provider REST Pipeline")
            print(f"  License: MIT\n")
        else:
            print(f"  {RED}Invalid selection.{RESET}")
        
        input(f"\n  {DIM}Press Enter to return to menu...{RESET}")
        print_banner()

def main():
    parser = argparse.ArgumentParser(description="GeoPulse CLI — High-Performance Network Geolocation Engine")
    parser.add_argument("-t", "--target", help="IP address or hostname to trace")
    parser.add_argument("-m", "--my-ip", action="store_true", help="Trace your own public IP address")
    parser.add_argument("-j", "--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("-b", "--batch", help="Path to text file containing target IPs")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        interactive_menu()
        return

    if args.my_ip:
        data = fetch_ip_info("")
        display_info(data, as_json=args.json)
    elif args.target:
        ip = resolve_domain(args.target)
        data = fetch_ip_info(ip)
        display_info(data, as_json=args.json)
    elif args.batch:
        if os.path.exists(args.batch):
            with open(args.batch, 'r') as f:
                ips = [line.strip() for line in f if line.strip()]
            results = []
            for item in ips:
                ip = resolve_domain(item)
                d = fetch_ip_info(ip)
                results.append(d)
                if not args.json:
                    print(f"\n--- {item} ---")
                    display_info(d)
            if args.json:
                print(json.dumps(results, indent=2))
        else:
            print(f"{RED}Error: File {args.batch} not found.{RESET}")

if __name__ == "__main__":
    main()
