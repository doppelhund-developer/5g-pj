import socket
import threading
import psutil
import time

LOG_FILE = "/mnt/test_folder/logs/monitor_log.txt"
MONITOR_INTERVAL = 1  # seconds
monitoring = False
monitor_thread = None
running = True
PORT = 9999


def get_cpu_times():
    with open("/proc/stat", "r") as f:
        cpu_line = f.readline()
    fields = [float(column) for column in cpu_line.strip().split()[1:]]
    total = sum(fields)
    idle = fields[3]  # idle time is the 4th field
    return total, idle

def get_cpu_percent(interval=1.0):
    total1, idle1 = get_cpu_times()
    time.sleep(interval)
    total2, idle2 = get_cpu_times()

    total_delta = total2 - total1
    idle_delta = idle2 - idle1

    if total_delta == 0:
        return 0.0
    cpu_usage = (1.0 - idle_delta / total_delta) * 100.0
    return cpu_usage

def monitor():
    with open(LOG_FILE, "w") as f:
        while monitoring:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            f.write(f"{time.time()}, CPU: {cpu}%, MEM: {mem}%\n")
            f.flush()
            time.sleep(MONITOR_INTERVAL)


def handle_client(conn):
    global monitoring, monitor_thread
    with conn:
        cmd = conn.recv(1024).decode().strip().lower()
        if cmd == "start":
            if not monitoring:
                monitoring = True
                monitor_thread = threading.Thread(target=monitor)
                monitor_thread.start()
                conn.sendall(b"Monitoring started\n")
            else:
                conn.sendall(b"Already monitoring\n")
        elif cmd == "stop":
            if monitoring:
                monitoring = False
                monitor_thread.join()
                conn.sendall(b"Monitoring stopped\n")
            else:
                conn.sendall(b"Not monitoring\n")
        else:
            conn.sendall(b"Unknown command\n")


def main():
    global running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))  # bind to all interfaces, port 9999
    server.listen(1)
    print("UPF monitor server listening on port 9999...")

    while running:
        conn, _ = server.accept()
        handle_client(conn)


if __name__ == "__main__":
    main()
