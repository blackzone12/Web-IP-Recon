# 🦅 Web/IP-Recon Engine v3.5

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Android-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-orange?style=for-the-badge)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)

**An Elite, Multi-Source OSINT and Asset Harvesting Infrastructure.**

[Explore Features](#🚀-key-features) • [Quick Setup](#🛠️-installation) • [Usage Guide](#🖥️-usage) • [Legal](#🛡️-disclaimer)

</div>

---

## � Table of Contents
- [�🚀 Key Features](#🚀-key-features)
- [🛠️ Installation](#🛠️-installation)
- [🖥️ Usage](#🖥️-usage)
- [📂 Project Architecture](#📂-project-architecture)
- [🏗️ Quick Links](#🏗️-quick-links)
- [🛡️ Disclaimer](#🛡️-disclaimer)

---

## 🚀 Key Features

- **🛡️ Deep Passive Discovery**: Queries multiple industrial OSINT databases:
  - `crt.sh`: Certificate Transparency Logs.
  - `AlienVault OTX`: Passive DNS historical data.
  - `Wayback Machine`: Historical archive snapshots.
  - `HackerTarget`: Rapid hostname resolution indices.
- **⚡ DNS-First Logic**: Industrial-grade verification via `dnspython` for bypass-speed hostname validation.
- **🔄 Recursive Tier Scanning**: Automated discovery of nested infrastructure (e.g., `dev.vpn.cloud.example.com`).
- **🕷️ BeautifulSoup Intelligence**: Advanced HTML5/JS resource parsing for high-fidelity asset harvesting.
- **📱 Universal Compatibility**: Optimized for Desktop (Windows/Linux) and Mobile (Termux).

---

## 🛠️ Installation

| Step | Method | Command |
| :--- | :--- | :--- |
| **1** | Clone Repo | `git clone https://github.com/youruser/web-recon.git` |
| **2** | **Windows** | `install.bat` |
| **3** | **Linux** | `chmod +x install.sh && ./install.sh` |
| **4** | **Android** | `chmod +x termux_setup.sh && ./termux_setup.sh` |

---

## 🖥️ Usage

> **Note**: Always ensure your virtual environment is active before starting a session.

### 🏷️ Domain Reconnaissance
Execute a comprehensive scan against a top-level domain:
```bash
python web_recon.py --domain example.com
```

### 🌐 IP-Based Infrastructure Scan
Identify ownership and reverse-mapped domains:
```bash
python web_recon.py --ip 1.1.1.1
```

---

## 📂 Project Architecture

The tool follows a three-stage reconnaissance pipeline:
1.  **Seeding**: Passive OSINT & Wordlist aggregation.
2.  **Validation**: High-concurrency DNS A-Record verification & Wildcard filtering.
3.  **Harvesting**: Intelligent HTTP life-checks & BeautifulSoup asset extraction.

---

## 🏗️ Quick Links
- 🛡️ [License Agreement](LICENSE)
- 📋 [Dependencies](requirements.txt)
- 🪟 [Windows Installer](install.bat)
- 🐧 [Linux Installer](install.sh)
- 📱 [Termux Setup](termux_setup.sh)

---

## 🛡️ Disclaimer
This tool is for educational and authorized security testing purposes ONLY. The primary author (**Black Zone**) and contributors are not responsible for any misuse. **Ethical Use Only.**

---

## 🤝 Contributing
Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Feel free to fork and pull.

**Built with ❤️ by Black Zone**