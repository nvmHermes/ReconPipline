# Recon Pipeline v2.0

> Automated Reconnaissance Framework for Bug Bounty Hunting, CTFs, and Penetration Testing
> 
## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Overview

Recon Pipeline v2.0 is an automated reconnaissance framework that combines multiple security tools into a single workflow.

The goal is to reduce repetitive enumeration tasks by automatically:

* Scanning ports
* Enumerating services
* Discovering directories
* Finding virtual hosts
* Enumerating subdomains
* Fingerprinting web technologies
* Capturing screenshots
* Generating structured reports

The tool also supports automatic installation of missing dependencies.

---

## Features

### Network Reconnaissance

* Full TCP port scanning with Nmap
* Service and version detection
* XML parsing and JSON conversion

### Web Enumeration

* Directory brute forcing with Gobuster
* Virtual host discovery
* FFUF endpoint fuzzing

### Subdomain Discovery

* Subfinder integration
* Sublist3r integration

### Web Technology Detection

* WhatWeb fingerprinting
* Technology stack identification

### Visual Reconnaissance

* Automated screenshots using GoWitness

### Reporting

* Summary report generation
* JSON export
* Organized output structure

### Auto Installation

Automatically installs missing tools:

* Nmap
* Gobuster
* FFUF
* Subfinder
* Sublist3r
* WhatWeb
* GoWitness

---

## Supported Tools

| Tool      | Purpose                         |
| --------- | ------------------------------- |
| Nmap      | Port and service discovery      |
| Gobuster  | Directory and vHost enumeration |
| FFUF      | Endpoint fuzzing                |
| Subfinder | Subdomain discovery             |
| Sublist3r | Subdomain enumeration           |
| WhatWeb   | Technology fingerprinting       |
| GoWitness | Website screenshots             |

---

## Installation

Clone the repository:

```bash
git clone https://github.com/nvmHermes/recon-pipeline.git

cd recon-pipeline
```

Install Python dependencies:

```bash
pip3 install colorama
```

Run with automatic tool installation:

```bash
python3 recon.py -t target.com --auto-install
```

---

## Usage

### Run Everything

```bash
python3 recon.py -t target.com
```

### Run Specific Tools

```bash
python3 recon.py -t target.com --tools nmap,gobuster
```

### Custom Output Directory

```bash
python3 recon.py -t target.com -o engagement1
```

### Custom Wordlist

```bash
python3 recon.py -t target.com \
--wordlist ~/wordlists/common.txt
```

### Verbose Mode

```bash
python3 recon.py -t target.com -v
```

### Auto Install Missing Tools

```bash
python3 recon.py -t target.com --auto-install
```

---

## Output Structure

```text
recon_target.com_2026-06-18_15-30-00/

├── nmap/
│   ├── ports.txt
│   ├── nmap_scan.txt
│   └── nmap_scan.xml
│
├── gobuster/
│   ├── dirs.txt
│   └── vhosts.txt
│
├── ffuf/
│   ├── admin.csv
│   ├── api.csv
│   └── ...
│
├── subdomains/
│   ├── subfinder.txt
│   └── sublist3r.txt
│
├── screenshots/
│   ├── urls.txt
│   ├── screenshots/
│   └── whatweb.txt
│
├── parsed/
│   └── nmap_parsed.json
│
├── logs/
│
├── summary.txt
└── results.json
```

---

## Example

```bash
python3 recon.py \
-t devhub.htb \
--tools nmap,gobuster,whatweb \
--auto-install \
-v
```

Output:

```text
[INFO] Starting Nmap scans
[SUCCESS] Found 3 open ports

[INFO] Starting Gobuster scans
[SUCCESS] Directory scan completed

[INFO] Starting WhatWeb
[SUCCESS] Technology detection completed
```

---

## Why I Built This

During Hack The Box and TryHackMe engagements, I repeatedly found myself running the same commands:

```bash
nmap
gobuster
ffuf
whatweb
subfinder
```

This project was created to automate that workflow and keep all results organized in a single location.

---

## Future Improvements

* Masscan integration
* Nuclei integration
* Amass integration
* HTTPX integration
* Automatic HTML reporting
* Screenshot gallery dashboard
* Multi-target scanning
* AI-assisted findings summary

---

## Disclaimer

This tool is intended for:

* Authorized penetration testing
* Capture The Flag competitions
* Hack The Box
* TryHackMe
* Security research

Only use against systems you own or have permission to test.

---

## Author

**Hermes**

GitHub: https://github.com/nvmHermes

If you find this project useful, consider starring the repository.

