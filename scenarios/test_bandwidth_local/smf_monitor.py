import socket
import threading
import subprocess
import time, os
from prometheus_client import start_http_server, Gauge


smf_ips=[
   os.getenv('SMF_IP'),
   os.getenv('SMF2_IP'),
   os.getenv('SMF3_IP'),
   os.getenv('SMF4_IP'),
]

SMF_IP = subprocess.check_output("ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'", shell=True).decode().strip()

LOG_FILE = f"/mnt/test_folder/logs/smf{smf_ips.index(SMF_IP)+1}.csv"
MONITOR_INTERVAL = 1  # seconds
monitoring = False
monitor_thread = None
running = True
PORT = 9999
PROMETHEUS_PORT = 9093

cpu_metric = Gauge("smf_cpu_percent", "CPU usage percentage of UPF process")
mem_metric = Gauge("smf_memory_mb", "Memory usage of UPF process in MB")
mem_percent_metric = Gauge("smf_memory_percent", "Memory usage as percent of system")


def get_upf_stats():
    process_name = "open5gs-smfd"

    # Get memory in MB using ps
    try:
        ps_cmd = f"ps -C {process_name} -o rss= | awk '{{sum+=$1}} END {{print sum/1024}}'"
        mem_output = subprocess.check_output(ps_cmd, shell=True).decode().strip()
        memory_mb = float(mem_output)
    except Exception as e:
        memory_mb = -1
        print(f"[Error] Getting memory: {e}")
        
    try:
        pid = subprocess.check_output(["pidof", process_name], text=True).strip()
        top_output = subprocess.check_output(["top", "-b", "-n1", "-p", pid], text=True)

        # Find the line that starts with the PID
        for line in top_output.splitlines():
            if line.strip().startswith(pid):
                parts = line.split()
                cpu_usage = float(parts[8])      # 9th column: %CPU
                memory_percent = float(parts[9]) # 10th column: %MEM
                break
        else:
            cpu_usage = -1
            memory_percent = -1
            print("[Error] Process line not found in top output")
    except Exception as e:
        cpu_usage = -1
        memory_percent = -1
        print(f"[Error] Getting CPU: {e}")

    return cpu_usage, memory_mb, memory_percent

#write csv log
#TODO push to prometheus for real time graph?
def monitor():
    with open(LOG_FILE, "w") as f:
        f.write(f"time,cpu_percent,mem_mb,mem_percent\n")
        f.flush()
        while True:
            cpu, mem, mem_p = get_upf_stats()
            # Update Prometheus metrics
            cpu_metric.set(cpu)
            mem_metric.set(mem)
            mem_percent_metric.set(mem_p)            
            if monitoring:
                f.write(f"{time.time()},{cpu},{mem},{mem_p}\n")
                f.flush()
            time.sleep(MONITOR_INTERVAL)
        


def handle_client(conn):
    global monitoring, monitor_thread
    with conn:
        cmd = conn.recv(1024).decode().strip().lower()
        if cmd == "start":
            if not monitoring:
                monitoring = True
                conn.sendall(b"Monitoring started\n")
            else:
                conn.sendall(b"Already monitoring\n")
        elif cmd == "stop":
            if monitoring:
                monitoring = False
                conn.sendall(b"Monitoring stopped\n")
            else:
                conn.sendall(b"Not monitoring\n")
        else:
            conn.sendall(b"Unknown command\n")


def main():
    global running
    
    monitor_thread = threading.Thread(target=monitor)
    monitor_thread.start()
    
    start_http_server(PROMETHEUS_PORT)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))  # bind to all interfaces, port 9999
    server.listen(1)
    print("SMF monitor server listening on port 9999...")

    while running:
        conn, _ = server.accept()
        handle_client(conn)


if __name__ == "__main__":
    main()
