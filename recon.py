#!/usr/bin/env python3
"""
Advanced Recon Pipeline – Complete Version with Auto-Install
Created by: Hermes (github.com/nvmHermes)
Usage: python3 recon.py -t example.com --tools nmap,gobuster --wordlist mylist.txt
"""

import os
import sys
import re
import json
import subprocess
import argparse
from datetime import datetime

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS = True
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
    class Style:
        RESET_ALL = ''
        BRIGHT = ''
    COLORS = False

class ReconPipeline:
    def __init__(self, args):
        """Initialize with parsed arguments."""
        self.target = args.target
        self.tools = args.tools.split(',') if args.tools else ['all']
        self.output_dir = args.output or f"recon_{self.target}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        self.wordlist = args.wordlist
        self.vhost_wordlist = args.vhost_wordlist
        self.ffuf_wordlist = args.ffuf_wordlist
        self.threads = args.threads or 50
        self.verbose = args.verbose
        self.auto_install = args.auto_install
        self.results = {}
        self.failed_phases = []
        self.installed_tools = []
        
        # Define available tools with their install info
        self.tool_map = {
            'nmap': {
                'func': self.nmap_scan,
                'install': self.install_nmap,
                'check': self.check_nmap
            },
            'gobuster': {
                'func': self.gobuster_scan,
                'install': self.install_gobuster,
                'check': self.check_gobuster
            },
            'ffuf': {
                'func': self.ffuf_scan,
                'install': self.install_ffuf,
                'check': self.check_ffuf
            },
            'subfinder': {
                'func': self.subfinder_scan,
                'install': self.install_subfinder,
                'check': self.check_subfinder
            },
            'sublist3r': {
                'func': self.sublist3r_scan,
                'install': self.install_sublist3r,
                'check': self.check_sublist3r
            },
            'whatweb': {
                'func': self.whatweb_scan,
                'install': self.install_whatweb,
                'check': self.check_whatweb
            },
            'screenshots': {
                'func': self.gowitness_scan,
                'install': self.install_gowitness,
                'check': self.check_gowitness
            },
            'all': {
                'func': self.run_all_tools,
                'install': None,
                'check': None
            }
        }
        
        self.create_dirs()
        self.print_banner()
        self.check_and_install_tools()

    # ============================================================
    # INSTALLATION CHECKER
    # ============================================================
    
    def check_and_install_tools(self):
        """Check if required tools are installed, install if missing."""
        self.log("Checking required tools...", "INFO")
        
        tools_to_check = []
        if 'all' in self.tools:
            tools_to_check = list(self.tool_map.keys())
            tools_to_check.remove('all')
        else:
            tools_to_check = self.tools
        
        for tool_name in tools_to_check:
            if tool_name not in self.tool_map:
                continue
            tool_info = self.tool_map[tool_name]
            if tool_info['check'] is None:
                continue
            
            if not tool_info['check']():
                self.log(f"{tool_name} is not installed.", "WARNING")
                if self.auto_install:
                    self.log(f"Attempting to install {tool_name}...", "INFO")
                    if tool_info['install']():
                        self.log(f"{tool_name} installed successfully.", "SUCCESS")
                        self.installed_tools.append(tool_name)
                    else:
                        self.log(f"Failed to install {tool_name}.", "ERROR")
                else:
                    self.log(f"Run with --auto-install to install {tool_name} automatically.", "WARNING")
            else:
                self.log(f"{tool_name} is installed.", "SUCCESS")

    # ============================================================
    # INSTALLATION FUNCTIONS
    # ============================================================
    
    def install_with_apt(self, package):
        """Install a package using apt."""
        try:
            cmd = f"sudo apt update && sudo apt install -y {package}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def install_with_go(self, package):
        """Install a Go package."""
        try:
            cmd = f"go install {package}@latest"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def install_with_pip(self, package):
        """Install a Python package with pip."""
        try:
            cmd = f"pip3 install {package}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def install_with_git(self, repo, dest):
        """Clone and install a git repository."""
        try:
            cmd = f"git clone {repo} /tmp/{dest} && cd /tmp/{dest} && sudo python3 setup.py install"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    # ----- Tool-specific install checks -----
    
    def check_nmap(self):
        return self.tool_installed("nmap")
    
    def install_nmap(self):
        return self.install_with_apt("nmap")
    
    def check_gobuster(self):
        return self.tool_installed("gobuster")
    
    def install_gobuster(self):
        return self.install_with_apt("gobuster")
    
    def check_ffuf(self):
        return self.tool_installed("ffuf")
    
    def install_ffuf(self):
        return self.install_with_apt("ffuf")
    
    def check_subfinder(self):
        return self.tool_installed("subfinder")
    
    def install_subfinder(self):
        return self.install_with_apt("subfinder")
    
    def check_sublist3r(self):
        return self.tool_installed("sublist3r")
    
    def install_sublist3r(self):
        return self.install_with_git("https://github.com/aboul3la/Sublist3r.git", "Sublist3r")
    
    def check_whatweb(self):
        return self.tool_installed("whatweb")
    
    def install_whatweb(self):
        return self.install_with_apt("whatweb")
    
    def check_gowitness(self):
        return self.tool_installed("gowitness")
    
    def install_gowitness(self):
        # Check if Go is installed first
        if not self.tool_installed("go"):
            self.log("Go is required for gowitness. Installing Go...", "INFO")
            if not self.install_with_apt("golang-go"):
                self.log("Failed to install Go. Skipping gowitness.", "ERROR")
                return False
        return self.install_with_go("github.com/sensepost/gowitness")

    # ============================================================
    # SETUP & UTILITY METHODS
    # ============================================================
    
    def print_banner(self):
        """Print a cool banner with creator credit."""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    RECON PIPELINE v2.0                          ║
║                  Automated Security Scanner                     ║
║                  Created by: Hermes (nvmHermes)                 ║
║                   with Auto-Install Support                     ║
╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
{Fore.GREEN}[+] Target: {self.target}
[+] Output: {self.output_dir}
[+] Tools: {', '.join(self.tools)}
[+] Threads: {self.threads}
[+] Auto-install: {'Yes' if self.auto_install else 'No'}
{Style.RESET_ALL}"""
        print(banner)

    def create_dirs(self):
        """Create output directory structure."""
        folders = [
            self.output_dir,
            f"{self.output_dir}/nmap",
            f"{self.output_dir}/gobuster",
            f"{self.output_dir}/ffuf",
            f"{self.output_dir}/subdomains",
            f"{self.output_dir}/screenshots",
            f"{self.output_dir}/parsed",
            f"{self.output_dir}/logs",
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
        print(f"{Fore.GREEN}[+] Created output directory: {self.output_dir}{Style.RESET_ALL}")

    def log(self, message, level="INFO"):
        """Print colored log messages."""
        colors = {
            "INFO": Fore.WHITE,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "DEBUG": Fore.CYAN
        }
        color = colors.get(level, Fore.WHITE)
        print(f"{color}[{level}] {message}{Style.RESET_ALL}")

    def run_command(self, command, description, timeout=600):
        """Execute a shell command and return output."""
        self.log(f"Running: {description}", "INFO")
        if self.verbose:
            self.log(f"Command: {command}", "DEBUG")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode != 0 and self.verbose:
                self.log(f"Command returned non-zero: {result.returncode}", "WARNING")
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            self.log(f"{description} timed out after {timeout}s", "ERROR")
            return ""
        except Exception as e:
            self.log(f"Error in {description}: {e}", "ERROR")
            return ""

    def get_wordlist(self, custom, default):
        """Return custom wordlist if valid, else default."""
        if custom and os.path.exists(custom):
            return custom
        if custom:
            self.log(f"Wordlist not found: {custom}", "WARNING")
        if os.path.exists(default):
            return default
        self.log(f"Default wordlist not found: {default}", "WARNING")
        return None

    def tool_installed(self, tool_name):
        """Check if a tool is installed."""
        try:
            subprocess.run(f"which {tool_name}", shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    # ============================================================
    # TOOL 1: NMAP
    # ============================================================
    
    def nmap_scan(self):
        """Run comprehensive Nmap scans."""
        self.log("Starting Nmap scans", "INFO")
        
        if not self.tool_installed("nmap"):
            self.log("Nmap not installed. Skipping.", "ERROR")
            return
        
        # Quick port scan
        ports_file = f"{self.output_dir}/nmap/ports.txt"
        cmd = f"nmap -p- --min-rate 1000 -oN {ports_file} {self.target}"
        self.run_command(cmd, "Nmap full port scan")
        self.results["nmap_quick"] = ports_file
        
        # Detailed scan
        detailed_file = f"{self.output_dir}/nmap/nmap_scan.txt"
        xml_file = f"{self.output_dir}/nmap/nmap_scan.xml"
        
        ports = ""
        if os.path.exists(ports_file):
            with open(ports_file, 'r') as f:
                content = f.read()
                found_ports = re.findall(r'(\d+)/open', content)
                if found_ports:
                    ports = ",".join(found_ports[:50])
                    self.log(f"Found {len(found_ports)} open ports", "SUCCESS")
        
        if ports:
            cmd = f"nmap -sC -sV -p {ports} -oN {detailed_file} -oX {xml_file} {self.target}"
        else:
            cmd = f"nmap -sC -sV -oN {detailed_file} -oX {xml_file} {self.target}"
        
        self.run_command(cmd, "Nmap service scan")
        self.results["nmap_detailed"] = detailed_file
        self.results["nmap_xml"] = xml_file
        
        # Parse XML
        self.parse_nmap_xml(xml_file)
        self.log("Nmap scans completed", "SUCCESS")

    def parse_nmap_xml(self, xml_file):
        """Parse nmap XML output to JSON."""
        if not os.path.exists(xml_file):
            return
        
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            parsed = {"hosts": [], "ports": []}
            for host in root.findall('host'):
                addr = host.find('address')
                if addr is not None:
                    parsed["hosts"].append(addr.get('addr', 'unknown'))
                
                for port in host.findall('ports/port'):
                    port_id = port.get('portid')
                    protocol = port.get('protocol')
                    service = port.find('service')
                    state = port.find('state')
                    parsed["ports"].append({
                        "port": port_id,
                        "protocol": protocol,
                        "service": service.get('name') if service is not None else "unknown",
                        "state": state.get('state') if state is not None else "unknown"
                    })
            
            json_file = f"{self.output_dir}/parsed/nmap_parsed.json"
            with open(json_file, 'w') as f:
                json.dump(parsed, f, indent=2)
            self.results["nmap_parsed"] = json_file
            self.log(f"Parsed {len(parsed['ports'])} ports to JSON", "SUCCESS")
        except Exception as e:
            self.log(f"Failed to parse nmap XML: {e}", "WARNING")

    # ============================================================
    # TOOL 2: GOBUSTER
    # ============================================================
    
    def gobuster_scan(self):
        """Run directory and vhost brute-force."""
        self.log("Starting Gobuster scans", "INFO")
        
        if not self.tool_installed("gobuster"):
            self.log("Gobuster not installed. Skipping.", "ERROR")
            return
        
        # Directory scan
        dir_output = f"{self.output_dir}/gobuster/dirs.txt"
        wordlist = self.get_wordlist(self.wordlist, "/usr/share/wordlists/dirb/common.txt")
        
        if wordlist:
            cmd = f"gobuster dir -u http://{self.target} -w {wordlist} -o {dir_output} -t {self.threads} -q"
            self.run_command(cmd, "Gobuster directory scan")
            self.results["gobuster_dir"] = dir_output
        else:
            self.log("No wordlist for directory scan", "WARNING")
        
        # Vhost scan
        vhost_output = f"{self.output_dir}/gobuster/vhosts.txt"
        vhost_wordlist = self.get_wordlist(
            self.vhost_wordlist,
            "/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt"
        )
        
        if vhost_wordlist:
            cmd = f"gobuster vhost -u http://{self.target} -w {vhost_wordlist} -o {vhost_output} -t {self.threads} -q"
            self.run_command(cmd, "Gobuster vhost scan")
            self.results["gobuster_vhost"] = vhost_output
        else:
            self.log("No wordlist for vhost scan", "WARNING")
        
        self.log("Gobuster scans completed", "SUCCESS")

    # ============================================================
    # TOOL 3: FFUF
    # ============================================================
    
    def ffuf_scan(self):
        """Fuzz common paths with ffuf."""
        self.log("Starting FFUF scans", "INFO")
        
        if not self.tool_installed("ffuf"):
            self.log("FFUF not installed. Skipping.", "ERROR")
            return
        
        wordlist = self.get_wordlist(
            self.ffuf_wordlist or self.wordlist,
            "/usr/share/wordlists/dirb/common.txt"
        )
        
        if not wordlist:
            self.log("No wordlist for ffuf", "WARNING")
            return
        
        ffuf_dir = f"{self.output_dir}/ffuf"
        paths = ['admin', 'api', 'backup', 'config', 'logs', 'debug', 'test', 'dev']
        
        for path in paths:
            output = f"{ffuf_dir}/{path}.csv"
            cmd = f"ffuf -u http://{self.target}/{path}/FUZZ -w {wordlist} -o {output} -of csv -t {self.threads} -ac -s"
            self.run_command(cmd, f"FFUF {path} fuzzing", timeout=300)
        
        self.results["ffuf"] = ffuf_dir
        self.log("FFUF scans completed", "SUCCESS")

    # ============================================================
    # TOOL 4: SUBFINDER
    # ============================================================
    
    def subfinder_scan(self):
        """Discover subdomains with subfinder."""
        self.log("Starting Subfinder", "INFO")
        
        if not self.tool_installed("subfinder"):
            self.log("Subfinder not installed. Skipping.", "ERROR")
            return
        
        output = f"{self.output_dir}/subdomains/subfinder.txt"
        cmd = f"subfinder -d {self.target} -o {output}"
        self.run_command(cmd, "Subfinder scan")
        self.results["subfinder"] = output
        self.log("Subfinder completed", "SUCCESS")

    # ============================================================
    # TOOL 5: SUBLIST3R
    # ============================================================
    
    def sublist3r_scan(self):
        """Discover subdomains with sublist3r."""
        self.log("Starting Sublist3r", "INFO")
        
        if not self.tool_installed("sublist3r"):
            self.log("Sublist3r not installed. Skipping.", "WARNING")
            return
        
        output = f"{self.output_dir}/subdomains/sublist3r.txt"
        cmd = f"sublist3r -d {self.target} -o {output}"
        self.run_command(cmd, "Sublist3r scan")
        self.results["sublist3r"] = output
        self.log("Sublist3r completed", "SUCCESS")

    # ============================================================
    # TOOL 6: WHATWEB
    # ============================================================
    
    def whatweb_scan(self):
        """Detect web technologies."""
        self.log("Starting WhatWeb", "INFO")
        
        if not self.tool_installed("whatweb"):
            self.log("WhatWeb not installed. Skipping.", "WARNING")
            return
        
        output = f"{self.output_dir}/screenshots/whatweb.txt"
        cmd = f"whatweb http://{self.target} > {output}"
        self.run_command(cmd, "WhatWeb scan")
        self.results["whatweb"] = output
        self.log("WhatWeb completed", "SUCCESS")

    # ============================================================
    # TOOL 7: GOWITNESS (SCREENSHOTS)
    # ============================================================
    
    def gowitness_scan(self):
        """Capture screenshots of web services."""
        self.log("Starting Gowitness screenshots", "INFO")
        
        if not self.tool_installed("gowitness"):
            self.log("Gowitness not installed. Skipping.", "WARNING")
            return
        
        ports_file = f"{self.output_dir}/nmap/ports.txt"
        if not os.path.exists(ports_file):
            self.log("No ports file found. Run nmap first.", "WARNING")
            return
        
        with open(ports_file, 'r') as f:
            content = f.read()
            ports = re.findall(r'(\d+)/open.*http', content, re.IGNORECASE)
            
            if not ports:
                self.log("No web ports found. Skipping screenshots.", "WARNING")
                return
            
            urls = [f"http://{self.target}:{p}" for p in ports] + [f"https://{self.target}:{p}" for p in ports]
            url_file = f"{self.output_dir}/screenshots/urls.txt"
            
            with open(url_file, 'w') as uf:
                uf.write('\n'.join(urls))
            
            cmd = f"gowitness file -f {url_file} -P {self.output_dir}/screenshots"
            self.run_command(cmd, "Gowitness screenshot capture", timeout=300)
            self.results["gowitness"] = f"{self.output_dir}/screenshots"
            self.log("Screenshots completed", "SUCCESS")

    # ============================================================
    # RUN ALL TOOLS
    # ============================================================
    
    def run_all_tools(self):
        """Execute all tools in sequence."""
        self.log("Running ALL tools", "INFO")
        for name, tool_info in self.tool_map.items():
            if name != 'all':
                try:
                    tool_info['func']()
                except Exception as e:
                    self.log(f"Tool {name} failed: {e}", "ERROR")
                    self.failed_phases.append(name)

    # ============================================================
    # SUMMARY & REPORTING
    # ============================================================
    
    def save_summary(self):
        """Generate summary report."""
        self.log("Generating summary", "INFO")
        summary_file = f"{self.output_dir}/summary.txt"
        
        with open(summary_file, 'w') as f:
            f.write(f"{'='*60}\n")
            f.write(f"RECON PIPELINE SUMMARY\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Created by: Hermes (nvmHermes)\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Auto-install: {'Yes' if self.auto_install else 'No'}\n\n")
            
            if self.installed_tools:
                f.write(f"Installed tools: {', '.join(self.installed_tools)}\n\n")
            
            f.write(f"{'-'*60}\n")
            f.write(f"RESULTS\n")
            f.write(f"{'-'*60}\n\n")
            
            for key, value in self.results.items():
                f.write(f"{key:20}: {value}\n")
            
            if self.failed_phases:
                f.write(f"\n{'-'*60}\n")
                f.write(f"FAILED PHASES\n")
                f.write(f"{'-'*60}\n")
                for phase in self.failed_phases:
                    f.write(f"- {phase}\n")
        
        self.log(f"Summary saved to: {summary_file}", "SUCCESS")

    def save_json(self):
        """Save structured JSON output."""
        self.log("Saving JSON output", "INFO")
        json_file = f"{self.output_dir}/results.json"
        
        output = {
            "creator": "Hermes (nvmHermes)",
            "target": self.target,
            "timestamp": datetime.now().isoformat(),
            "tools_used": self.tools,
            "auto_install": self.auto_install,
            "installed_tools": self.installed_tools,
            "results": self.results,
            "failed_phases": self.failed_phases
        }
        
        with open(json_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        self.log(f"JSON saved to: {json_file}", "SUCCESS")

    # ============================================================
    # MAIN EXECUTION
    # ============================================================
    
    def run(self):
        """Execute the pipeline based on selected tools."""
        if 'all' in self.tools:
            self.run_all_tools()
        else:
            for tool in self.tools:
                if tool in self.tool_map:
                    try:
                        self.tool_map[tool]['func']()
                    except Exception as e:
                        self.log(f"Tool {tool} failed: {e}", "ERROR")
                        self.failed_phases.append(tool)
                else:
                    self.log(f"Unknown tool: {tool}", "ERROR")
        
        self.save_summary()
        self.save_json()
        
        self.log(f"\n{'='*60}", "SUCCESS")
        self.log(f"RECON COMPLETE!", "SUCCESS")
        self.log(f"Created by: Hermes (nvmHermes)", "SUCCESS")
        self.log(f"Output directory: {self.output_dir}", "SUCCESS")
        if self.installed_tools:
            self.log(f"Tools installed: {', '.join(self.installed_tools)}", "INFO")
        if self.failed_phases:
            self.log(f"Failed phases: {', '.join(self.failed_phases)}", "WARNING")
        self.log(f"{'='*60}", "SUCCESS")


# ============================================================
# COMMAND LINE ARGUMENTS
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Recon Pipeline v2.0 - Created by Hermes (nvmHermes)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 recon.py -t example.com
  python3 recon.py -t example.com --tools nmap,gobuster
  python3 recon.py -t example.com --wordlist ~/my_wordlist.txt
  python3 recon.py -t example.com --tools ffuf --ffuf-wordlist ~/fuzz.txt
  python3 recon.py -t example.com --auto-install  # Automatically install missing tools
        """
    )
    
    parser.add_argument("-t", "--target", required=True, help="Target domain or IP address")
    parser.add_argument("-o", "--output", help="Custom output directory name")
    parser.add_argument("--tools", default="all", help="Comma-separated tools to run (default: all)")
    parser.add_argument("--wordlist", help="Custom wordlist for directory scanning")
    parser.add_argument("--vhost-wordlist", help="Custom wordlist for vhost scanning")
    parser.add_argument("--ffuf-wordlist", help="Custom wordlist for ffuf")
    parser.add_argument("--threads", type=int, default=50, help="Number of threads (default: 50)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--auto-install", action="store_true", help="Automatically install missing tools")
    
    args = parser.parse_args()
    
    # Convert target to lowercase
    args.target = args.target.lower()
    
    # Run the pipeline
    pipeline = ReconPipeline(args)
    pipeline.run()


if __name__ == "__main__":
    main()