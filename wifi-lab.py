#!/usr/bin/env python3
"""
WiFi Lab Builder - Generador de Entornos Inalámbricos de Prácticas
Crea interfaces virtuales utilizando mac80211_hwsim para simular redes Wi-Fi en Linux.
"""

import os
import sys
import time
import subprocess
import argparse

TEMP_DIR = "/tmp/wifi_lab_configs"


def check_root():
    """Verifica que el script se ejecute con privilegios de superusuario."""
    if os.geteuid() != 0:
        print("[!] Este script requiere privilegios de root para gestionar módulos del kernel y servicios de red.")
        print("    Uso: sudo python3 wifi_lab.py [opciones]")
        sys.exit(1)


def setup_hwsim(num_radios=3):
    """Carga el módulo mac80211_hwsim y prepara las interfaces."""
    print(f"[*] Cargando módulo mac80211_hwsim con {num_radios} radios virtuales...")
    #Para NetworkManager para evitar problemas al iniciar script
    subprocess.run(["systemctl", "stop", "NetworkManager"], stderr=subprocess.DEVNULL)
    
    # Eliminar módulo previo si estaba cargado
    subprocess.run(["modprobe", "-r", "mac80211_hwsim"], stderr=subprocess.DEVNULL)
    result = subprocess.run(["modprobe", "mac80211_hwsim", f"radios={num_radios}"], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("[+] Interfaces inalámbricas virtuales creadas correctamente.")
        # Evitar interferencias de NetworkManager y activar interfaces al instante
        for i in range(num_radios):
            subprocess.run(["nmcli", "device", "set", f"wlan{i}", "managed", "no"], stderr=subprocess.DEVNULL)
            subprocess.run(["ip", "link", "set", f"wlan{i}", "up"], stderr=subprocess.DEVNULL)
    else:
        print(f"[!] Error cargando el módulo del kernel: {result.stderr}")
        sys.exit(1)


def teardown():
    """Limpia el entorno, detiene servicios y elimina el módulo virtual."""
    print("\n[*] Limpiando el laboratorio...")
    
    subprocess.run(["pkill", "-f", "hostapd"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "wpa_supplicant"], stderr=subprocess.DEVNULL)
    subprocess.run(["modprobe", "-r", "mac80211_hwsim"], stderr=subprocess.DEVNULL)
    
    if os.path.exists(TEMP_DIR):
        subprocess.run(["rm", "-rf", TEMP_DIR])
        
    print("[+] Entorno restaurado al estado original.")


def create_hostapd_config(iface="wlan0", ssid="Lab_WiFi_Test", channel=6, passphrase=None):
    """Genera el archivo de configuración para hostapd."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    config_path = os.path.join(TEMP_DIR, "hostapd.conf")
    
    config_content = f"""interface={iface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel={channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
    if passphrase:
        config_content += f"""wpa=2
wpa_passphrase={passphrase}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
    
    with open(config_path, "w") as f:
        f.write(config_content)
        
    return config_path


def start_ap(iface, ssid, channel, passphrase):
    """Inicia el punto de acceso con hostapd."""
    config_path = create_hostapd_config(iface, ssid, channel, passphrase)
    print(f"[*] Iniciando AP '{ssid}' en interfaz {iface} (Canal {channel})...")
    
    proc = subprocess.Popen(
        ["hostapd", config_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)
    
    if proc.poll() is None:
        print(f"[+] Punto de acceso activo (PID: {proc.pid}).")
        return proc
    else:
        print("[!] Error al iniciar hostapd. Verifica que hostapd esté instalado y que la interfaz esté libre.")
        return None


def start_virtual_client(client_iface="wlan1", ssid="Lab_WiFi_Test", passphrase="Laboratorio123!"):
    """Simula un cliente Wi-Fi conectándose automáticamente al AP."""
    os.makedirs(TEMP_DIR, exist_ok=True)
    supplicant_conf = os.path.join(TEMP_DIR, "wpa_supplicant.conf")
    
    content = f"""ctrl_interface=/var/run/wpa_supplicant
update_config=1

network={{
    ssid="{ssid}"
    psk="{passphrase}"
    key_mgmt=WPA-PSK
}}
"""
    with open(supplicant_conf, "w") as f:
        f.write(content)
        
    print(f"[*] Iniciando cliente virtual en {client_iface} intentando conectar a '{ssid}'...")
    
    proc = subprocess.Popen(
        ["wpa_supplicant", "-i", client_iface, "-c", supplicant_conf],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc


def main():
    parser = argparse.ArgumentParser(description="WiFi Lab Builder - Creador de laboratorios de pruebas Wi-Fi")
    parser.add_argument("--radios", type=int, default=3, help="Número de interfaces inalámbricas virtuales a crear")
    parser.add_argument("--ssid", type=str, default="Lab_WiFi_Test", help="Nombre del SSID para el AP virtual")
    parser.add_argument("--passphrase", type=str, default="Laboratorio123!", help="Contraseña WPA2 para la red virtual")
    parser.add_argument("--ap-iface", type=str, default="wlan0", help="Interfaz asignada al AP")
    parser.add_argument("--client-iface", type=str, default="wlan1", help="Interfaz asignada al cliente virtual")
    args = parser.parse_args()

    check_root()

    try:
        setup_hwsim(num_radios=args.radios)
        ap_proc = start_ap(args.ap_iface, args.ssid, 6, args.passphrase)
        
        if ap_proc:
            time.sleep(1)
            client_proc = start_virtual_client(args.client_iface, args.ssid, args.passphrase)
            
            print("\n" + "="*50)
            print("  LABORATORIO WI-FI ACTIVO")
            print("="*50)
            print(f"  - Punto de Acceso (AP): {args.ap_iface}")
            print(f"  - Cliente Virtual:      {args.client_iface}")
            print(f"  - SSID:                 {args.ssid}")
            print(f"  - Interfaz libre para pruebas: wlan2")
            print("\n  Presiona Ctrl+C para detener y limpiar el entorno.")
            print("="*50 + "\n")
            
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        teardown()


if __name__ == "__main__":
    main()