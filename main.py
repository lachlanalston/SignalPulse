#!/usr/bin/env python3
import time
import datetime
import subprocess
import json
import random
import matplotlib.pyplot as plt
from fpdf import FPDF

# =====================
# CONFIG
# =====================
SITE_NAME = "Test Site"
DURATION_SECONDS = 30  # set to 24*60*60 for full-day testing
PING_TARGETS = ["1.1.1.1", "8.8.8.8"]
OUTPUT_JSON = "results.json"
OUTPUT_PDF = "pre_sales_voip_report.pdf"
SLEEP_INTERVAL = 5  # seconds

# Thresholds for traffic light summary
DOWNLOAD_THRESHOLDS = {"green": 50, "yellow": 20}  # Mbps
UPLOAD_THRESHOLDS = {"green": 20, "yellow": 10}    # Mbps
LATENCY_THRESHOLDS = {"green": 50, "yellow": 100}  # ms
RSRP_THRESHOLDS = {"green": -85, "yellow": -100}   # dBm
RSRQ_THRESHOLDS = {"green": -10, "yellow": -15}    # dB
SINR_THRESHOLDS = {"green": 15, "yellow": 10}      # dB
JITTER_THRESHOLDS = {"green": 10, "yellow": 30}    # ms
PACKET_LOSS_THRESHOLDS = {"green": 1, "yellow": 3} # %

# =====================
# HELPER FUNCTIONS
# =====================
def run_ping(target="1.1.1.1", count=3):
    try:
        result = subprocess.run(["ping", "-c", str(count), target],
                                capture_output=True, text=True, timeout=10)
        output = result.stdout
        avg_latency = jitter = packet_loss = None
        for line in output.splitlines():
            if "packet loss" in line:
                try:
                    packet_loss = float(line.split(",")[2].strip().split()[0].replace("%", ""))
                except:
                    packet_loss = None
            if "rtt min/avg/max/mdev" in line:
                stats = line.split('=')[1].split('/')
                avg_latency = float(stats[1].replace(' ms','').strip())
                jitter = float(stats[3].replace(' ms','').strip())
        return {"avg_latency": avg_latency, "jitter": jitter, "packet_loss": packet_loss}
    except Exception as e:
        print(f"Ping error ({target}): {e}")
        return {"avg_latency": None, "jitter": None, "packet_loss": None}

def run_speedtest():
    try:
        result = subprocess.run(["speedtest", "--json"], capture_output=True, text=True, timeout=30)
        if not result.stdout:
            return {"download": None, "upload": None}
        data = json.loads(result.stdout)
        download = data.get('download', 0) / 1e6
        upload = data.get('upload', 0) / 1e6
        return {"download": download, "upload": upload}
    except subprocess.TimeoutExpired:
        print("Speedtest timed out")
        return {"download": None, "upload": None}
    except Exception as e:
        print(f"Speedtest error: {e}")
        return {"download": None, "upload": None}

def get_fake_teltonika_metrics():
    return {
        "RSRP": -90 + random.randint(-5,5),
        "RSRQ": -12 + random.randint(-2,2),
        "SINR": 12 + random.randint(-2,3)
    }

def save_json_live(data, filename=OUTPUT_JSON):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def traffic_light_color(value, thresholds):
    if value is None:
        return (128,128,128)  # Gray
    if value >= thresholds["green"]:
        return (0,200,0)      # Green
    elif value >= thresholds["yellow"]:
        return (255,200,0)    # Yellow
    else:
        return (200,0,0)      # Red

# =====================
# CHARTS
# =====================
def generate_charts(data):
    timestamps = [d['timestamp'] for d in data]
    download = [d['speedtest']['download'] or 0 for d in data]
    upload = [d['speedtest']['upload'] or 0 for d in data]
    rsrp = [d['teltonika']['RSRP'] or 0 for d in data]
    rsrq = [d['teltonika']['RSRQ'] or 0 for d in data]
    sinr = [d['teltonika']['SINR'] or 0 for d in data]
    jitter = [d['ping'][PING_TARGETS[0]]['jitter'] or 0 for d in data]
    packet_loss = [d['ping'][PING_TARGETS[0]]['packet_loss'] or 0 for d in data]

    plt.style.use('ggplot')

    # Speed chart
    plt.figure(figsize=(9,3))
    plt.plot(timestamps, download, marker='o', label='Download Mbps', linewidth=2)
    plt.plot(timestamps, upload, marker='s', label='Upload Mbps', linewidth=2)
    plt.xticks(rotation=45)
    plt.ylabel("Mbps")
    plt.xlabel("Time")
    plt.tight_layout()
    plt.savefig("speed_chart.png", dpi=120)
    plt.close()

    # Signal chart
    plt.figure(figsize=(9,3))
    plt.plot(timestamps, rsrp, marker='o', label='RSRP dBm', linewidth=2)
    plt.plot(timestamps, rsrq, marker='s', label='RSRQ dB', linewidth=2)
    plt.plot(timestamps, sinr, marker='^', label='SINR dB', linewidth=2)
    plt.xticks(rotation=45)
    plt.ylabel("Signal")
    plt.xlabel("Time")
    plt.tight_layout()
    plt.savefig("signal_chart.png", dpi=120)
    plt.close()

    # VoIP quality chart
    plt.figure(figsize=(9,3))
    plt.plot(timestamps, jitter, marker='o', label='Jitter ms', linewidth=2)
    plt.plot(timestamps, packet_loss, marker='s', label='Packet Loss %', linewidth=2)
    plt.xticks(rotation=45)
    plt.ylabel("VoIP Metrics")
    plt.xlabel("Time")
    plt.tight_layout()
    plt.savefig("voip_chart.png", dpi=120)
    plt.close()

# =====================
# PDF GENERATION
# =====================
def generate_pdf(data, filename=OUTPUT_PDF):
    # Compute averages
    speed_downloads = [d['speedtest']['download'] for d in data if d['speedtest']['download'] is not None]
    speed_uploads = [d['speedtest']['upload'] for d in data if d['speedtest']['upload'] is not None]
    pings = [d['ping'][PING_TARGETS[0]]['avg_latency'] for d in data if d['ping'][PING_TARGETS[0]]['avg_latency'] is not None]
    jitters = [d['ping'][PING_TARGETS[0]]['jitter'] for d in data if d['ping'][PING_TARGETS[0]]['jitter'] is not None]
    packet_losses = [d['ping'][PING_TARGETS[0]]['packet_loss'] for d in data if d['ping'][PING_TARGETS[0]]['packet_loss'] is not None]
    rsrps = [d['teltonika']['RSRP'] for d in data if d['teltonika']['RSRP'] is not None]
    rsrqs = [d['teltonika']['RSRQ'] for d in data if d['teltonika']['RSRQ'] is not None]
    sinrs = [d['teltonika']['SINR'] for d in data if d['teltonika']['SINR'] is not None]

    avg_download = sum(speed_downloads)/len(speed_downloads) if speed_downloads else None
    avg_upload = sum(speed_uploads)/len(speed_uploads) if speed_uploads else None
    avg_latency = sum(pings)/len(pings) if pings else None
    avg_jitter = sum(jitters)/len(jitters) if jitters else None
    avg_packet_loss = sum(packet_losses)/len(packet_losses) if packet_losses else None
    avg_rsrp = sum(rsrps)/len(rsrps) if rsrps else None
    avg_rsrq = sum(rsrqs)/len(rsrqs) if rsrqs else None
    avg_sinr = sum(sinrs)/len(sinrs) if sinrs else None

    # Generate charts
    generate_charts(data)

    # PDF creation
    pdf = FPDF('P','mm','A4')
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 8, f"{SITE_NAME} - Pre-Sales VoIP & LTE Report", ln=True, align="C")
    pdf.ln(4)

    # Traffic light summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Traffic Light Summary", ln=True)
    pdf.ln(1)
    pdf.set_font("Arial", "", 10)
    metrics = [
        ("Download Mbps", avg_download, DOWNLOAD_THRESHOLDS),
        ("Upload Mbps", avg_upload, UPLOAD_THRESHOLDS),
        ("Latency ms", avg_latency, LATENCY_THRESHOLDS),
        ("Jitter ms", avg_jitter, JITTER_THRESHOLDS),
        ("Packet Loss %", avg_packet_loss, PACKET_LOSS_THRESHOLDS),
        ("RSRP dBm", avg_rsrp, RSRP_THRESHOLDS),
        ("RSRQ dB", avg_rsrq, RSRQ_THRESHOLDS),
        ("SINR dB", avg_sinr, SINR_THRESHOLDS)
    ]
    for label, value, thresholds in metrics:
        color = traffic_light_color(value, thresholds)
        pdf.set_fill_color(*color)
        pdf.cell(6, 6, "", ln=0, fill=True)
        pdf.cell(45, 6, f" {label}: {value:.2f}" if value is not None else f" {label}: N/A", ln=1)
    pdf.ln(2)

    # Metric explanations
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Metric Explanations", ln=True)
    pdf.set_font("Arial", "", 9)
    explanations = {
        "Download Mbps": "Speed at which data is received. Higher = smoother downloads & streaming.",
        "Upload Mbps": "Speed at which data is sent. Higher = faster uploads & cloud backup and VoIP upstream.",
        "Latency ms": "Time for signal round-trip. Lower = better for VoIP & real-time apps.",
        "Jitter ms": "Variability in latency. Lower = smoother VoIP calls.",
        "Packet Loss %": "Percentage of lost packets. Lower = fewer dropped VoIP calls.",
        "RSRP dBm": "Strength of 4G LTE signal. Higher (less negative) = stronger connection.",
        "RSRQ dB": "Quality of LTE signal relative to noise/interference. Higher (less negative) = more stable.",
        "SINR dB": "Signal-to-Interference+Noise ratio. Higher = more stable LTE performance."
    }
    for label, text in explanations.items():
        pdf.multi_cell(0, 5, f"{label}: {text}")
    pdf.ln(2)

    # Executive summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Executive Summary", ln=True)
    pdf.set_font("Arial", "", 9)
    narrative = f"""
During this test period, the 4G/LTE performance at {SITE_NAME} showed:
- Average download: {avg_download:.2f} Mbps
- Average upload: {avg_upload:.2f} Mbps
- Average latency: {avg_latency:.2f} ms
- Average jitter: {avg_jitter:.2f} ms
- Average packet loss: {avg_packet_loss:.2f} %
- Average RSRP: {avg_rsrp:.2f} dBm
- Average RSRQ: {avg_rsrq:.2f} dB
- Average SINR: {avg_sinr:.2f} dB

Traffic lights above indicate network quality. Charts below show trends over time.
"""
    pdf.multi_cell(0, 5, narrative)
    pdf.ln(2)

    # Charts
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Performance Charts", ln=True)
    pdf.image("speed_chart.png", w=170)
    pdf.ln(2)
    pdf.image("signal_chart.png", w=170)
    pdf.ln(2)
    pdf.image("voip_chart.png", w=170)

    pdf.output(filename)
    print(f"One-page VoIP-ready LTE PDF generated: {filename}")

# =====================
# MAIN SCRIPT
# =====================
data = []
start_time = time.time()
end_time = start_time + DURATION_SECONDS

while time.time() < end_time:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ping_results = {t: run_ping(t) for t in PING_TARGETS}
    speed_results = run_speedtest()
    teltonika_metrics = get_fake_teltonika_metrics()

    entry = {
        "timestamp": timestamp,
        "ping": ping_results,
        "speedtest": speed_results,
        "teltonika": teltonika_metrics
    }
    data.append(entry)
    save_json_live(data)
    print(f"{timestamp} - Entry collected and saved to JSON")
    time.sleep(SLEEP_INTERVAL)

generate_pdf(data)
