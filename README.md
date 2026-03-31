<p align="center">
  <img src="preview.png" width="600">
</p>
## 🔬 Context

This tool is part of a broader exploration into network identity manipulation and behavioral signal variability.

It focuses on how low-level identifiers (like MAC addresses) can be controlled, rotated, and analyzed in controlled environments.

---

## 🧠 What this actually enables

* Simulating device identity changes
* Testing correlation mechanisms
* Exploring detection boundaries
* Understanding how systems rely on persistent identifiers

---

## ⚡ Bigger direction

This is a minimal implementation of a larger idea:

Building modular tools for identity-layer manipulation and behavior simulation across networked systems.

# MAC Address Auto Rotator (CLI)

Lightweight CLI tool for rotating MAC addresses on Linux interfaces in real time.

---

## Why I built this

During work on network behavior simulation and privacy testing in isolated lab environments, I needed a simple and reliable way to:

* Randomize MAC addresses safely
* Avoid vendor conflicts (LAA compliance)
* Run in headless environments (SSH / VM)
* Control behavior dynamically without restarting

This tool was built to solve that.

---

## Features

* Locally Administered MAC generation (safe, non-conflicting)
* Threaded background rotation engine
* Interactive CLI control
* Dry-run mode for safe testing
* File logging (audit trail)

---

## Usage

```bash
sudo python3 mac_rotator.py
```

Optional:

```bash
sudo python3 mac_rotator.py --interface eth0 --interval 10
```

---

## Controls

* s → start rotation
* p → stop
* c → change immediately
* q → quit

---

## Environment

* Debian / Linux
* Headless / SSH
* Local VM / lab usage

---

## Notes

* Requires root privileges
* Designed for controlled environments only

---

## Author

Mikel
Cybersecurity Researcher | Offensive Security | Network Behavior Analysis
