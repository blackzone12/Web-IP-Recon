import os
import socket
import requests
import re
import threading
import sys
import dns.resolver
import tldextract
from bs4 import BeautifulSoup
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

# Initialize DNS Resolver
resolver = dns.resolver.Resolver()
resolver.timeout = 3
resolver.lifetime = 3

# Force UTF-8 for Windows Terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
RESULT_BASE_DIR = "results"
WORDLIST_FILE = "subdomain_wordlist.txt"
TIMEOUT = 15 # Increased to handle slow servers
THREADS = 30
MAX_RETRIES = 2

# Asset Extensions - Exhaustive Search
IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.bmp', '.tiff', '.raw', '.psd', '.ai', '.eps', '.indd']
DOC_EXTS = ['.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.pptx', '.ppt', '.odt', '.rtf', '.tex', '.wpd', '.pages']
ARCHIVE_EXTS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.dmg', '.pkg', '.deb', '.rpm', '.exe', '.msi']
MEDIA_EXTS = ['.mp4', '.mov', '.avi', '.wmv', '.mkv', '.webm', '.mp3', '.wav', '.flac', '.m4a', '.ogg']
DATA_EXTS = ['.csv', '.json', '.xml', '.sql', '.sqlite', '.db', '.yaml', '.yml']
CONFIG_EXTS = ['.env', '.bak', '.old', '.conf', '.config', '.ini', '.log', '.git', '.htaccess', '.htpasswd']

# Premium Banner
BANNER = f"""
\033[94m
 ██╗    ██╗███████╗██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
 ██║    ██║██╔════╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
 ██║ █╗ ██║█████╗  ██████╔╝██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
 ██║███╗██║██╔══╝  ██╔══██╗██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
 ╚███╔███╔╝███████╗██████╔╝██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
  ╚══╝╚══╝ ╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
\033[0m
\033[93m        Advanced Web Reconnaissance Tool - v1.2.0\033[0m
\033[93m        Enhanced Reliability & Deep Asset Harvesting\033[0m
"""

class WebRecon:
    def __init__(self, target):
        # Normalize target domain using tldextract
        ext = tldextract.extract(target)
        self.target_domain = f"{ext.domain}.{ext.suffix}"
        if not self.target_domain or self.target_domain == ".": 
            self.target_domain = target
            
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.project_dir = os.path.join(RESULT_BASE_DIR, f"{self.target_domain}_{self.timestamp}")
        self.log_file = os.path.join(self.project_dir, "recon_log.txt")
        self.target_ip = None
        self.my_ip = None
        self.session = requests.Session()
        # Random User Agent for stealth
        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        self.session.headers.update({'User-Agent': ua_list[int(time.time()) % 3]})
        
        self.subdomains = []
        self.scanned_urls = set()
        self.discovered_assets = {
            "images": set(),
            "documents": set(),
            "archives": set(),
            "media": set(),
            "data": set(),
            "configs": set(),
            "other": set()
        }

        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)

    def log(self, message, print_it=True):
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        if print_it: print(entry)
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(entry + "\n")
        except: pass

    def get_public_ips(self):
        self.log(f"[*] Retrieving IP information...")
        try:
            self.target_ip = socket.gethostbyname(self.target_domain)
            self.log(f"[+] Target IP ({self.target_domain}): {self.target_ip}")
        except: self.log(f"[!] Could not resolve target IP.")
        try:
            res = self.session.get("https://api.ipify.org", timeout=10)
            self.my_ip = res.text
            self.log(f"[+] Your External IP: {self.my_ip}")
        except: self.log(f"[!] Could not retrieve your external IP.")

    def detect_wildcard(self):
        self.log("[*] Checking for DNS wildcard...")
        random_sub = f"wildcard-test-{int(time.time())}.{self.target_domain}"
        try:
            answers = resolver.resolve(random_sub, 'A')
            ip = str(answers[0])
            self.log(f"[!] Wildcard detected! {random_sub} resolved to {ip}.")
            return ip
        except:
            self.log("[+] No wildcard DNS detected.")
            return None

    def passive_discovery(self):
        potential_subs = set()
        self.log(f"[*] Querying OSINT sources (crt.sh, OTX, Wayback, HackerTarget)...")
        # crt.sh
        try:
            res = self.session.get(f"https://crt.sh/?q=%.{self.target_domain}&output=json", timeout=30)
            if res.status_code == 200:
                for entry in res.json():
                    for name in entry['name_value'].split('\n'):
                        name = name.strip().lower()
                        if name.endswith(self.target_domain) and "*" not in name: potential_subs.add(name)
        except: pass
        # OTX
        try:
            res = self.session.get(f"https://otx.alienvault.com/api/v1/indicators/domain/{self.target_domain}/passive_dns", timeout=20)
            if res.status_code == 200:
                for entry in res.json().get('passive_dns', []):
                    host = entry.get('hostname', '').lower()
                    if host.endswith(self.target_domain): potential_subs.add(host)
        except: pass
        # Wayback
        try:
            res = self.session.get(f"http://web.archive.org/cdx/search/cdx?url=*.{self.target_domain}/*&output=json&collapse=urlkey", timeout=30)
            if res.status_code == 200:
                data = res.json()
                for i in range(1, len(data)):
                    host = urlparse(f"http://{data[i][2]}").netloc.split(':')[0].lower()
                    if host.endswith(self.target_domain): potential_subs.add(host)
        except: pass
        # HackerTarget
        try:
            res = self.session.get(f"https://api.hackertarget.com/hostsearch/?q={self.target_domain}", timeout=15)
            if res.status_code == 200:
                for line in res.text.split('\n'):
                    if ',' in line: potential_subs.add(line.split(',')[0].strip().lower())
        except: pass
        self.log(f"[+] Passive discovery found {len(potential_subs)} candidates.")
        return list(potential_subs)

    def recursive_check(self, domains):
        self.log(f"[*] Probing nested tiers on {len(domains)} top targets...")
        common = ['dev', 'api', 'stg', 'test', 'prod', 'internal', 'vpn', 'admin', 'auth']
        extra = set()
        for d in domains:
            if d == self.target_domain: continue
            for t in common: extra.add(f"{t}.{d}")
        def quick_dns(domain):
            try:
                resolver.resolve(domain, 'A')
                return domain
            except: return None
        with ThreadPoolExecutor(max_workers=THREADS * 2) as executor:
            verified = [d for d in executor.map(quick_dns, list(extra)) if d]
        if verified: self.log(f"   [+] Recursive scan found {len(verified)} nested subdomains.")
        return verified

    def enumerate_subdomains(self):
        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", self.target_domain):
            self.log("[*] Target is an IP address. Skipping subdomain enumeration.")
            return

        wildcard_ip = self.detect_wildcard()
        candidates = set(self.passive_discovery())
        
        if os.path.exists(WORDLIST_FILE):
            self.log(f"[*] Adding wordlist candidates...")
            with open(WORDLIST_FILE, 'r') as f:
                for word in f:
                    word = word.strip().lower()
                    if word: candidates.add(f"{word}.{self.target_domain}")
        
        self.log(f"[*] Verifying {len(candidates)} candidates via DNS...")
        def verify_dns(domain):
            try:
                answers = resolver.resolve(domain, 'A')
                ip = str(answers[0])
                if wildcard_ip and ip == wildcard_ip and domain != self.target_domain: return None
                return domain
            except: return None

        with ThreadPoolExecutor(max_workers=THREADS * 2) as executor:
            dns_results = [d for d in executor.map(verify_dns, list(candidates)) if d]
            
        if dns_results:
            nested = self.recursive_check(dns_results[:100]) 
            dns_results = list(set(dns_results + nested))

        self.log(f"[+] {len(dns_results)} total domains passed DNS verification.")
        
        # Save All Resolved
        all_resolved_path = os.path.join(self.project_dir, "all_resolved_hosts.txt")
        with open(all_resolved_path, "w") as f:
            for d in sorted(dns_results): f.write(d + "\n")
        self.log(f"[*] Saved resolved hosts to all_resolved_hosts.txt")

        self.log(f"[*] Performing HTTP life-check...")
        def probe(domain):
            for p in ["https", "http"]:
                try:
                    res = self.session.head(f"{p}://{domain}", timeout=5, allow_redirects=True)
                    if res.status_code < 400: return f"{p}://{domain}"
                except: continue
            return None
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            self.subdomains = [u for u in executor.map(probe, dns_results) if u]
        self.log(f"[*] Total Active Web Services: {len(self.subdomains)}")
        with open(os.path.join(self.project_dir, "active_subdomains.txt"), "w") as f:
            for s in sorted(self.subdomains): f.write(s + "\n")

    def extract_assets(self, url):
        if url in self.scanned_urls: return
        self.scanned_urls.add(url)
        self.log(f"[*] Extracting assets from: {url}")
        
        try:
            res = self.session.get(url, timeout=TIMEOUT)
            if res.status_code != 200: return
            
            soup = BeautifulSoup(res.text, 'html.parser')
            tags = {'a': 'href', 'img': 'src', 'link': 'href', 'script': 'src', 'iframe': 'src', 'video': 'src', 'audio': 'src', 'source': 'src', 'embed': 'src'}
            
            found = []
            for tag, attr in tags.items():
                for el in soup.find_all(tag, **{attr: True}): found.append(el[attr])
            for el in soup.find_all(style=True):
                for match in re.findall(r'url\((["\']?)(.*?)\1\)', el['style']): found.append(match[1])

            for link in found:
                full = urljoin(url, link)
                path = urlparse(full).path.lower()
                ext = "." + path.split('.')[-1] if '.' in path else ""
                
                if ext in IMAGE_EXTS: self.discovered_assets["images"].add(full)
                elif ext in DOC_EXTS: self.discovered_assets["documents"].add(full)
                elif ext in ARCHIVE_EXTS: self.discovered_assets["archives"].add(full)
                elif ext in MEDIA_EXTS: self.discovered_assets["media"].add(full)
                elif ext in DATA_EXTS: self.discovered_assets["data"].add(full)
                elif ext in CONFIG_EXTS: self.discovered_assets["configs"].add(full)
                elif ext in ['.js', '.css', '.json', '.xml', '.ico']: self.discovered_assets["other"].add(full)
                    
        except Exception as e:
            self.log(f"[!] Error crawling {url}: {e}")

    def save_assets(self):
        self.log(f"[*] Compiling discovery results...")
        for category, assets in self.discovered_assets.items():
            if not assets: continue
            with open(os.path.join(self.project_dir, f"{category}.txt"), "w", encoding='utf-8') as f:
                for a in sorted(list(assets)): f.write(a + "\n")
        
        summary = f"\n--- RECON SUMMARY ---\nDomain: {self.target_domain}\nSubdomains: {len(self.subdomains)}\n----------------------\n"
        for k, v in self.discovered_assets.items(): summary += f"{k.capitalize():<10}: {len(v)}\n"
        summary += "----------------------\n"
        print(f"\033[92m{summary}\033[0m")
        self.log(summary, print_it=False)

    def run(self):
        try:
            print(BANNER)
            self.log(f"--- Recon Session: {self.target_domain} ---")
            self.get_public_ips()
            self.enumerate_subdomains()
            
            crawl_list = list(set([
                f"http://{self.target_domain}", 
                f"https://{self.target_domain}"
            ] + self.subdomains))
            
            self.log(f"[*] Extracting assets from {len(crawl_list)} active URLs...")
            with ThreadPoolExecutor(max_workers=THREADS) as crawler:
                crawler.map(self.extract_assets, crawl_list)

            self.save_assets()
            self.log(f"Done. Storage: {os.path.abspath(self.project_dir)}")
            
        except KeyboardInterrupt:
            self.log(f"\n[!] Session stopped. Finalizing logs...")
            self.save_assets()
        except Exception as e:
            self.log(f"[!] Critical Error: {e}")

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Web Recon Engine")
    parser.add_argument("-d", "--domain", help="Target Domain (e.g. example.com)")
    parser.add_argument("-i", "--ip", help="Target IP Address")
    args = parser.parse_args()

    try:
        target = ""
        if args.ip:
            ip_addr = args.ip
            try:
                print(f"[*] Performing Reverse DNS lookup for {ip_addr}...")
                target = socket.gethostbyaddr(ip_addr)[0]
                print(f"[+] Found Domain: {target}")
            except:
                print(f"[!] Reverse DNS failed. Using IP as target.")
                target = ip_addr
        elif args.domain:
            target = args.domain
        else:
            print("\033[92m[?] Web Recon Engine Ready.\033[0m")
            print("1. Domain Recon (e.g., example.com)")
            print("2. IP-Based Recon (e.g., 1.1.1.1)")
            choice = input("\nSelect Mode [1/2]: ").strip()
            
            if choice == "2":
                ip_addr = input("Enter IP Address: ").strip()
                try:
                    print(f"[*] Performing Reverse DNS lookup for {ip_addr}...")
                    target = socket.gethostbyaddr(ip_addr)[0]
                    print(f"[+] Found Domain: {target}")
                except:
                    print(f"[!] Reverse DNS failed. Using IP as target.")
                    target = ip_addr
            else:
                target = input("Enter Target Domain: ").strip()
        
        if not target: sys.exit(0)
        
        # Clean target (remove protocol, CIDR slashes, etc)
        if "://" in target: 
            from urllib.parse import urlparse
            target = urlparse(target).netloc
        if "/" in target:
            target = target.split("/")[0] # Fix for CIDR or paths
            
        WebRecon(target).run()
    except KeyboardInterrupt:
        sys.exit(0)
