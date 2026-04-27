#!/bin/bash
echo "[*] Initializing Web Recon Installation (Linux)..."

if ! command -v python3 &> /dev/null
then
    echo "[!] Python3 could not be found. Please install it."
    exit
fi

echo "[*] Creating Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo "[*] Installing Requirements..."
pip install --upgrade pip
pip install -r requirements.txt

chmod +x web_recon.py
echo ""
echo "[PRO TIP] To run the tool: source venv/bin/activate && python3 web_recon.py --domain example.com"
echo "[SUCCESS] Installation Complete."
