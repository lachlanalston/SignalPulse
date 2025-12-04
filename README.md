# SignalPulse

SignalPulse is a **LTE-focused network testing tool** designed to help MSPs and network engineers monitor cellular performance. It measures **download/upload speeds, latency, jitter, packet loss, and LTE signal metrics** (RSRP, RSRQ, SINR), generating a **one-page PDF report with traffic-light summaries and charts**.  

---

## Features

- Automated ping tests to multiple targets
- Speedtest CLI integration for real download/upload metrics
- LTE signal metrics support (RSRP, RSRQ, SINR)
- VoIP metrics: jitter and packet loss
- Live JSON logging of results
- Generates a PDF report with charts and traffic-light indicators

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YourUsername/SignalPulse.git
cd SignalPulse
```

### 2. Install Python dependencies
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt

### 3. Install system tools
sudo apt update
sudo apt install -y speedtest-cli

### 4. (Optional) Run full setup script if included
chmod +x setup.sh
./setup.sh

### 5. Run SignalPulse
python3 main.py
