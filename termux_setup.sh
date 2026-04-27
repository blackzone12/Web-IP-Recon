#!/data/data/com.termux/files/usr/bin/bash
echo "[*] Initializing Web Recon Installation (Android/Termux)..."

# Termux packages
pkg update && pkg upgrade -y
pkg install python ndk-sysroot clang make libdns -y

echo "[*] Creating Virtual Environment..."
python -m venv venv
source venv/bin/activate

echo "[*] Installing Requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[PRO TIP] To run the tool: source venv/bin/activate && python web_recon.py --domain example.com"
echo "[SUCCESS] Termux Setup Complete."
