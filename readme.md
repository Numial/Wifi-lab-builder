# 📡 WiFi Lab Builder

Herramienta en Python para desplegar laboratorios virtuales de redes inalámbricas en entornos Linux. Permite auditar y analizar el comportamiento de tramas 802.11 sin necesidad de hardware físico adicional.

## 🚀 Características
* Creación dinámica de interfaces virtuales mediante `mac80211_hwsim`.
* Despliegue automático de puntos de acceso simulados usando `hostapd`.
* Limpieza integral del entorno al finalizar la ejecución.

## 🛠️ Uso
```bash
# Clonar repositorio
git clone [https://github.com/numial/wifi-lab-builder.git](https://github.com/numial/wifi-lab-builder.git)
cd wifi-lab-builder

#Antes de ejecutar nada
sudo apt update
sudo apt install -y hostapd dnsmasq iw wireless-tools

# Ejecutar laboratorio predeterminado
sudo python3 wifi_lab.py --ssid "MiRedVirtual" --passphrase "Password123!"
