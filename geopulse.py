#!/usr/bin/env python3
"""
GeoPulse CLI v2.5 — Advanced Network Geolocation, Latency Benchmarking & Intelligence Engine
Tailored for Quant Infrastructure & Low-Latency Systems Engineering.
Author: Vaibhav Agrawal (D. E. Shaw & Co. / NITK)
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
import concurrent.futures
from datetime import datetime

# ANSI Color Definitions
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
{RESET}{DIM} Quant-Grade Low-Latency Network Intelligence & Geolocation Engine v2.5{RESET}
"""

def print_banner():
    if sys.stdout.isatty():
        os.system("clear" if os.name != "nt" else "cls")
        print(BANNER)

def resolve_target(target):
    """Resolves hostname to IP address with reverse DNS pointer."""
    try:
        ip = socket.gethostbyname(target)
        try:
            ptr = socket.gethostbyaddr(ip)[0]
        except Exception:
            ptr = "N/A"
        return ip, ptr
    except socket.gaierror:
        return target, "Resolution Failed"

def measure_tcp_latency(ip, port=80, count=4):
    """Measures TCP handshake RTT latency with nanosecond precision & jitter."""
    rtts = []
    for _ in range(count):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        start = time.perf_counter_ns()
        try:
            s.connect((ip, port))
            end = time.perf_counter_ns()
            rtts.append((end - start) / 1e6) # ms
            s.close()
        except Exception:
            s.close()
            continue
        time.sleep(0.05)

    if not rtts:
        return None

    min_rtt = round(min(rtts), 3)
    avg_rtt = round(sum(rtts) / len(rtts), 3)
    max_rtt = round(max(rtts), 3)
    jitter = round(max_rtt - min_rtt, 3)
    return {
        "min_ms": min_rtt,
        "avg_ms": avg_rtt,
        "max_ms": max_rtt,
        "jitter_ms": jitter,
        "samples": len(rtts)
    }

def probe_common_ports(ip, ports=[22, 53, 80, 443, 8080]):
    """Fast concurrent TCP port reachability probe."""
    open_ports = []
    def check_port(p):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.8)
        try:
            res = s.connect_ex((ip, p))
            s.close()
            if res == 0:
                return p
        except Exception:
            s.close()
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ports)) as executor:
        results = executor.map(check_port, ports)
        for r in results:
            if r is not None:
                open_ports.append(r)
    return open_ports

def fetch_geolocation(ip_address=""):
    """Fetches geolocation payload using multi-provider failover pipeline."""
    start_ns = time.perf_counter_ns()

    # Primary Provider: ip-api.com
    url1 = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query,mobile,proxy,hosting"
    try:
        req = urllib.request.Request(url1, headers={'User-Agent': 'GeoPulse-Quant/2.5'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            exec_time = round((time.perf_counter_ns() - start_ns) / 1e6, 2)
            if data.get("status") == "success":
                data["_latency_ms"] = exec_time
                data["_provider"] = "ip-api (Primary)"
                return data
    except Exception:
        pass

    # Secondary Failover: ipapi.co
    url2 = f"https://ipapi.co/{ip_address}/json/" if ip_address else "https://ipapi.co/json/"
    try:
        req = urllib.request.Request(url2, headers={'User-Agent': 'GeoPulse-Quant/2.5'})
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            raw = json.loads(resp.read().decode('utf-8'))
            exec_time = round((time.perf_counter_ns() - start_ns) / 1e6, 2)
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
                "_latency_ms": exec_time,
                "_provider": "ipapi.co (Failover)"
            }
    except Exception:
        pass

    return {"status": "fail", "message": "Failed to query IP geolocation across all upstream endpoints."}

def display_quant_report(target_raw, ip, ptr, data, latency_stats, open_ports, as_json=False):
    if as_json:
        combined = {
            "query_target": target_raw,
            "resolved_ip": ip,
            "reverse_dns": ptr,
            "geolocation": data,
            "tcp_rtt_stats": latency_stats,
            "open_ports": open_ports
        }
        print(json.dumps(combined, indent=2))
        return

    if data.get("status") != "success":
        print(f"\n{RED}{BOLD}❌ Query Error:{RESET} {data.get('message', 'Unable to resolve target.')}\n")
        return

    lat = data.get("lat", 0)
    lon = data.get("lon", 0)
    exec_time = data.get("_latency_ms", 0)
    provider = data.get("_provider", "Primary")

    print(f"  {BOLD}{GREEN}✔ Geolocation & Network Diagnostics Complete{RESET} {DIM}({exec_time}ms via {provider}){RESET}")
    print(f"  {CYAN}{'='*64}{RESET}")

    items = [
        ("Target Host", f"{target_raw} -> {ip}"),
        ("Reverse DNS (PTR)", ptr),
        ("Location / Country", f"{data.get('city')}, {data.get('regionName')} | {data.get('country')} ({data.get('countryCode')})"),
        ("Coordinates", f"{lat}, {lon}"),
        ("Timezone", data.get("timezone")),
        ("Network Provider (ISP)", data.get("isp")),
        ("Organization", data.get("org")),
        ("BGP Autonomous System", data.get("as")),
        ("Active Ports Probed", ", ".join(map(str, open_ports)) if open_ports else "None detected (Filtered)")
    ]

    for label, val in items:
        print(f"  {BOLD}{YELLOW}{label:<24}{RESET} {GREEN}▶{RESET}  {val}")

    # Latency Stats Panel
    print(f"  {CYAN}{'-'*64}{RESET}")
    if latency_stats:
        print(f"  {BOLD}{MAGENTA}⚡ Low-Latency TCP Handshake Metrics (Port 80/443):{RESET}")
        print(f"     Min RTT: {BOLD}{GREEN}{latency_stats['min_ms']} ms{RESET} | Avg RTT: {BOLD}{CYAN}{latency_stats['avg_ms']} ms{RESET} | Max RTT: {YELLOW}{latency_stats['max_ms']} ms{RESET} | Jitter: {DIM}{latency_stats['jitter_ms']} ms{RESET}")
    else:
        print(f"  {BOLD}{MAGENTA}⚡ TCP Handshake Latency:{RESET} {DIM}ICMP/TCP Ping blocked by remote firewall{RESET}")

    print(f"  {CYAN}{'='*64}{RESET}")
    print(f"  {DIM}📍 Google Maps URL: https://maps.google.com/?q={lat},{lon}{RESET}\n")

def process_single_target(target, as_json=False):
    ip, ptr = resolve_target(target)
    geo_data = fetch_geolocation(ip)
    latency_stats = measure_tcp_latency(ip)
    open_ports = probe_common_ports(ip)
    display_quant_report(target, ip, ptr, geo_data, latency_stats, open_ports, as_json=as_json)

def process_batch(file_path, as_json=False):
    if not os.path.exists(file_path):
        print(f"{RED}Error: Batch target file '{file_path}' not found.{RESET}")
        return

    with open(file_path, 'r') as f:
        targets = [line.strip() for line in f if line.strip()]

    print(f"  {BOLD}{CYAN}🚀 Executing Parallel Quant Batch Lookup for {len(targets)} Targets...{RESET}\n")

    def run_worker(t):
        ip, ptr = resolve_target(t)
        geo = fetch_geolocation(ip)
        rtt = measure_tcp_latency(ip, count=2)
        ports = probe_common_ports(ip)
        return {"target": t, "ip": ip, "ptr": ptr, "geo": geo, "rtt": rtt, "ports": ports}

    results = []
    start_batch = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, len(targets))) as executor:
        future_map = {executor.submit(run_worker, t): t for t in targets}
        for future in concurrent.futures.as_completed(future_map):
            res = future.result()
            results.append(res)
            if not as_json:
                print(f"  {GREEN}✔ Processed:{RESET} {res['target']} ({res['ip']}) | {res['geo'].get('city', 'N/A')}, {res['geo'].get('countryCode', 'N/A')}")

    total_time = round(time.perf_counter() - start_batch, 2)
    print(f"\n  {BOLD}{GREEN}Batch complete in {total_time}s across {len(targets)} threads.{RESET}\n")

    if as_json:
        print(json.dumps(results, indent=2))

def interactive_menu():
    print_banner()
    while True:
        print(f"  {BOLD}{CYAN}[ 1 ]{RESET} Quant Target Trace (IP / Hostname + TCP Latency Benchmarking)")
        print(f"  {BOLD}{CYAN}[ 2 ]{RESET} Self Public Network Diagnostics (Your IP + Latency)")
        print(f"  {BOLD}{CYAN}[ 3 ]{RESET} High-Throughput Parallel Batch IP Trace")
        print(f"  {BOLD}{CYAN}[ 4 ]{RESET} About GeoPulse Quant Suite")
        print(f"  {BOLD}{RED}[ x ]{RESET} Exit System\n")

        choice = input(f"  {BOLD}{YELLOW}GeoPulse-Quant >> {RESET}").strip().lower()

        if choice in ["x", "exit", "q", "quit"]:
            print(f"\n  {GREEN}Shutting down GeoPulse Engine. Bye!{RESET}\n")
            sys.exit(0)
        elif choice == "1":
            target = input(f"  {BOLD}Enter Target IP or Hostname (e.g. 8.8.8.8, deshaw.com): {RESET}").strip()
            if target:
                process_single_target(target)
        elif choice == "2":
            process_single_target("")
        elif choice == "3":
            raw_input = input(f"  {BOLD}Enter space-separated targets or file path: {RESET}").strip()
            if os.path.exists(raw_input):
                process_batch(raw_input)
            elif raw_input:
                targets = raw_input.split()
                print(f"\n  {BOLD}{BLUE}--- Processing Batch ({len(targets)} items) ---{RESET}")
                for t in targets:
                    process_single_target(t)
        elif choice == "4":
            print_banner()
            print(f"  {BOLD}GeoPulse Quant Engine v2.5{RESET}")
            print(f"  Engineer: Vaibhav Agrawal (D. E. Shaw & Co. / NITK)")
            print(f"  Features: Microsecond RTT Benchmarking, Threaded Failover, Reverse DNS PTR, Port Scanning")
            print(f"  License: MIT\n")
        else:
            print(f"  {RED}Invalid Selection.{RESET}")

        input(f"\n  {DIM}Press Enter to return...{RESET}")
        print_banner()

def main():
    parser = argparse.ArgumentParser(description="GeoPulse CLI v2.5 — Quant Network Geolocation & Latency Engine")
    parser.add_argument("-t", "--target", help="IP address or hostname to trace")
    parser.add_argument("-m", "--my-ip", action="store_true", help="Diagnostics for local public IP")
    parser.add_argument("-j", "--json", action="store_true", help="Output complete raw payload as JSON")
    parser.add_argument("-b", "--batch", help="Path to text file containing target list")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        interactive_menu()
        return

    if args.my_ip:
        process_single_target("", as_json=args.json)
    elif args.target:
        process_single_target(args.target, as_json=args.json)
    elif args.batch:
        process_batch(args.batch, as_json=args.json)

if __name__ == "__main__":
    main()
