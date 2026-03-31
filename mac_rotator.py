#!/usr/bin/env python3

"""
MAC Address Auto-Rotator (PRO)

Author: Mikel
Context: Network behavior simulation / privacy testing (isolated lab environments)

Features:
- LAA-safe MAC generation
- Threaded rotation engine
- CLI interactive control
- File logging (audit trail)
- Dry-run mode (safe testing)
"""

import subprocess
import random
import re
import time
import threading
import os
import sys
from datetime import datetime

# ===== CONFIG =====
DEFAULT_INTERFACE = "ens33"
DEFAULT_INTERVAL  = 30
LOG_FILE          = "mac_rotator.log"

# ===== ANSI =====
GRN = "\033[92m"
YLW = "\033[93m"
RED = "\033[91m"
CYN = "\033[96m"
GRY = "\033[90m"
BLD = "\033[1m"
RST = "\033[0m"

# ===== STATE =====
running = False
counter = 0
lock = threading.Lock()

# ===== UTIL =====

def _check_ip_tool():
    if not shutil.which("ip"):
        print(f"{RED}Missing 'ip' command (iproute2){RST}")
        sys.exit(1)

def _validate_interface(interface):
    try:
        subprocess.check_output(["ip", "link", "show", interface],
                                stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def _log_file(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} {msg}\n")

def _log(msg, color=GRN):
    ts = datetime.now().strftime("%H:%M:%S")
    with lock:
        print(f"{GRY}[{ts}]{RST} {color}{msg}{RST}")
    _log_file(msg)

# ===== MAC =====

def _gen_laa_mac():
    first = (random.randint(0x00, 0xff) & 0xfe) | 0x02
    rest  = [random.randint(0x00, 0xff) for _ in range(5)]
    return ":".join(f"{b:02x}" for b in [first] + rest)

def _get_current_mac(interface):
    try:
        out = subprocess.check_output(["ip", "link", "show", interface]).decode()
        match = re.search(r"link/ether\s+([0-9a-f:]{17})", out)
        return match.group(1) if match else "unknown"
    except:
        return "error"

def _set_mac(interface, new_mac, dry_run=False):
    if dry_run:
        _log(f"[DRY-RUN] {interface} -> {new_mac}", YLW)
        return

    cmds = [
        ["ip", "link", "set", interface, "down"],
        ["ip", "link", "set", interface, "address", new_mac],
        ["ip", "link", "set", interface, "up"],
    ]

    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode().strip())

# ===== CORE =====

def _change_mac(interface, dry_run):
    global counter
    try:
        new_mac = _gen_laa_mac()
        _set_mac(interface, new_mac, dry_run)
        actual = _get_current_mac(interface)
        counter += 1
        _log(f"#{counter:03d}  {actual}", GRN)
    except RuntimeError as e:
        _log(f"ERROR: {e}", RED)

def _worker(interface, interval, dry_run):
    global running
    while running:
        _change_mac(interface, dry_run)

        for _ in range(interval * 10):
            if not running:
                break
            time.sleep(0.1)

# ===== CLI =====

def _parse_args():
    interface = DEFAULT_INTERFACE
    interval  = DEFAULT_INTERVAL
    dry_run   = False

    args = sys.argv[1:]

    for i, arg in enumerate(args):
        if arg == "--interface" and i + 1 < len(args):
            interface = args[i + 1]

        elif arg == "--interval" and i + 1 < len(args):
            try:
                interval = int(args[i + 1])
            except:
                pass

        elif arg == "--dry-run":
            dry_run = True

    return interface, interval, dry_run

def _header(interface, interval, dry_run):
    os.system("clear")
    print(f"{BLD}{GRN}")
    print("  +======================================+")
    print("  |      MAC ROTATOR PRO (CLI TOOL)      |")
    print("  +======================================+")
    print(f"{RST}")

    print(f"  {GRY}Interface :{RST} {CYN}{interface}{RST}")
    print(f"  {GRY}Interval  :{RST} {CYN}{interval}s{RST}")
    print(f"  {GRY}Mode      :{RST} {YLW}{'DRY-RUN' if dry_run else 'LIVE'}{RST}")
    print(f"  {GRY}Current   :{RST} {GRN}{_get_current_mac(interface)}{RST}")
    print()

    print(f"  {YLW}s{RST} start   {YLW}p{RST} stop   {YLW}c{RST} change   {YLW}q{RST} quit")
    print()

# ===== MAIN =====

def main():
    global running

    if os.geteuid() != 0:
        print(f"{RED}Run with sudo{RST}")
        sys.exit(1)

    interface, interval, dry_run = _parse_args()

    if not _validate_interface(interface):
        print(f"{RED}Invalid interface: {interface}{RST}")
        sys.exit(1)

    _header(interface, interval, dry_run)
    _log(f"Ready. MAC: {_get_current_mac(interface)}", YLW)

    while True:
        try:
            cmd = input(f"\n{CYN}> {RST}").strip().lower()
        except (KeyboardInterrupt, EOFError):
            running = False
            break

        if cmd == "s":
            if not running:
                running = True
                threading.Thread(
                    target=_worker,
                    args=(interface, interval, dry_run),
                    daemon=True
                ).start()
                _log(f"Started ({interval}s)", GRN)
            else:
                _log("Already running", YLW)

        elif cmd == "p":
            running = False
            _log("Stopped", RED)

        elif cmd == "c":
            threading.Thread(
                target=_change_mac,
                args=(interface, dry_run),
                daemon=True
            ).start()

        elif cmd == "q":
            running = False
            break

        else:
            _log("s / p / c / q", YLW)

if __name__ == "__main__":
    import shutil
    main()
