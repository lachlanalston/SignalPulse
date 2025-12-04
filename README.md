# SignalPulse

SignalPulse is a **LTE-focused network testing tool** designed to **measure cellular performance and VoIP quality**. It monitors download/upload speeds, latency, jitter, packet loss, and LTE signal metrics (RSRP, RSRQ, SINR), and generates a **PDF report with charts and traffic-light summaries**.  

> **Note:** This is currently a **proof-of-concept** script. Later, it is intended to run on a **Raspberry Pi with the Teltonika Calyx HAT** for real LTE metrics.  

---

## Features

- Automated **ping tests** to multiple targets  
- **Speedtest CLI** for download/upload measurements  
- LTE signal metrics support (RSRP, RSRQ, SINR)  
- VoIP metrics: **jitter** and **packet loss**  
- Live JSON logging of results  
- Generates a **modern PDF report** with traffic-light summary and charts  
- Designed to be **Raspberry Pi / Teltonika Calyx HAT-ready**  

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
