# 📡 WiFi Lab Builder

A lightweight, automated Python tool designed to deploy isolated virtual 802.11 wireless laboratory environments on Linux systems using kernel-level virtualization. 

This project facilitates hands-on practice with Wi-Fi penetration testing techniques, frame analysis, and credential auditing without requiring physical wireless adapters or external router hardware.

---

## 📑 Table of Contents
- [Key Features](#-key-features)
- [Architecture & Mechanics](#-architecture--mechanics)
- [Prerequisites & Dependencies](#-prerequisites--dependencies)
- [Installation](#-installation)
- [Usage](#-usage)
- [Testing & Verification Guide](#-testing--verification-guide)
- [License](#-license)

---

## ⚡ Key Features

- **Software-Based Wireless Emulation:** Utilizes the Linux kernel module `mac80211_hwsim` to create functional virtual radio interfaces (`wlan0`, `wlan1`, `wlan2`, etc.) in system RAM.
- **Automated Access Point Deployment:** Spawns custom AP instances using `hostapd` configured with dynamic WPA2-PSK credentials.
- **Simulated Active Client:** Automatically attaches a virtual client using `wpa_supplicant` to generate realistic 802.11 traffic and handle re-authentication attempts upon deauthentication.
- **Service & Conflict Handling:** Programmatically disables `NetworkManager` during execution to prevent channel hopping and interface hijacking, restoring service automatically upon exit.
- **Graceful Teardown:** Ensures complete resource cleanup, killing background processes and removing kernel modules on exit (`Ctrl+C`).

---

## 🏗️ Architecture & Mechanics

The environment deploys three simulated radio interfaces by default over a virtual kernel bus:

```mermaid
graph TD
    subgraph Kernel ["Virtual Kernel Bus: mac80211_hwsim"]
        W0["wlan0<br/>(Access Point)"]
        W1["wlan1<br/>(Virtual Client)"]
        W2["wlan2<br/>(Monitor Mode)"]
    end

    H["hostapd<br/>(AP Daemon)"] --> W0
    S["wpa_supplicant<br/>(Client Daemon)"] --> W1
    A["airodump-ng / aireplay-ng<br/>(Auditing Tools)"] --> W2

    W0 <-->|WPA2 4-Way Handshake| W1
```

1. **`wlan0` (Access Point):** Governed by `hostapd`, broadcasting the target SSID.
2. **`wlan1` (Virtual Client):** Governed by `wpa_supplicant`, connected to `wlan0`.
3. **`wlan2` (Auditing Interface):** Left unmanaged for monitor mode configuration, frame injection (`aireplay-ng`), and packet capture (`airodump-ng` / Wireshark).

---

## 📋 Prerequisites & Dependencies

The tool relies on standard Linux networking and wireless utilities. Ensure your host system (e.g., Kali Linux, Debian, Ubuntu) has the required tools installed:

```bash
sudo apt update
sudo apt install -y hostapd wpa_supplicant iw wireless-tools net-tools NetworkManager
```

---

## 📥 Installation

Clone the repository to your local system:

```bash
git clone https://github.com/numial/wifi-lab-builder.git
cd wifi-lab-builder
```

---

## 🚀 Usage

Execute the script with root privileges (required for kernel module management and service handling):

```bash
sudo python3 wifi_lab.py
```

### Optional Command-Line Arguments

Customize the laboratory setup using CLI flags:

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--radios` | `int` | `3` | Number of virtual radio interfaces to generate |
| `--ssid` | `str` | `Lab_WiFi_Test` | Target Network SSID broadcasted by the AP |
| `--passphrase` | `str` | `Laboratorio123!` | WPA2-PSK passphrase for authentication |
| `--ap-iface` | `str` | `wlan0` | Virtual interface assigned to the Access Point |
| `--client-iface`| `str` | `wlan1` | Virtual interface assigned to the connected Client |
| `--random-mac`|  |  | Generate a random MAC address |


#### Example Custom Deployment:
```bash
sudo python3 wifi_lab.py --ssid "Corporate_Guest" --passphrase "SecureP@ssword2026" --radios 4
```

---

## 🧪 Testing & Verification Guide

Once the lab is running, you can test packet captures and deauthentication attacks from a secondary terminal:

### 1. Set the Unused Interface to Monitor Mode
```bash
sudo ip link set wlan2 down
sudo iw dev wlan2 set type monitor
sudo ip link set wlan2 up
```

### 2. Capture Traffic and Handshakes
```bash
sudo airodump-ng -c 6 wlan2
```

### 3. Inject Deauthentication Frames
In a third terminal, trigger a deauthentication attack against the virtual client (`wlan1`) to capture the 4-Way Handshake on reconnect:
```bash
sudo aireplay-ng -0 2 -a <AP_MAC_ADDRESS> -c <CLIENT_MAC_ADDRESS> wlan2
```

---
