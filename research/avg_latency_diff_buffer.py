import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np
import time
class latency_calculator:
    def __init__(self):
        self.sent_file = 'log_sent_timestamp.txt'
        self.received_file = 'log_received_timestamp.txt'
        self.median_latency = {}
    
    def read_timestamps(self, file_name):
        timestamps = {}
        with open(file_name, 'r') as file:
            for line in file:
                # Use regex to extract FileID and timestamp
                match = re.match(r'FileID:\s*(\d+)\s+.*Time:\s*(\d+)\s*ns', line)
                if match:
                    file_id = int(match.group(1))
                    timestamp_ns = int(match.group(2))
                    timestamps[file_id] = timestamp_ns
        return timestamps

    def calculate_latencies(self, sent_file, received_file):
        sent_timestamps = self.read_timestamps(sent_file)
        received_timestamps = self.read_timestamps(received_file)
        
        latencies_ms = []
        file_ids = []
        
        common_file_ids = set(sent_timestamps.keys()) & set(received_timestamps.keys())
        
        for file_id in sorted(common_file_ids):
            sent_time = sent_timestamps[file_id]
            received_time = received_timestamps[file_id]
            latency_ms = (received_time - sent_time) / 1e6  # Convert ns to ms
            latencies_ms.append(latency_ms)
            file_ids.append(file_id)
        
        return file_ids, latencies_ms
    
    def save_median_latency(self, buffer_size):
        file_ids, latencies_ms = self.calculate_latencies(self.sent_file, self.received_file)
        median = np.median(latencies_ms)
        self.median_latency[buffer_size] = median  # saving result
        print(f"Buffer size: {buffer_size}, median_latency:{median}")
        with open("log_median_latency", "a") as file:
            file.write(f"{buffer_size},{median}\n")  # save result to txt, for logging

def plot_graph(latency_data):
    """
    Plots buffer size vs median latency graph
    
    Args:
        latency_data (dict): Dictionary with buffer sizes as keys
                             and median latencies as values
    """
    # Sort the dictionary by buffer size
    sorted_data = sorted(latency_data.items(), key=lambda x: x[0])
    
    # Separate buffer sizes and latencies into individual lists
    buffer_sizes = [item[0] for item in sorted_data]
    median_latencies = [item[1] for item in sorted_data]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(buffer_sizes, median_latencies, 
             marker='o', linestyle='-', linewidth=2, markersize=8)
    
    # Customize the plot
    plt.title('Buffer Size vs Median Latency')
    plt.xlabel('Buffer Size (bytes)')
    plt.ylabel('Median Latency (ms)')
    plt.grid(True, which='both', linestyle='--', alpha=0.7)
    
    # Use logarithmic scale if buffer sizes span multiple orders of magnitude
    if max(buffer_sizes)/min(buffer_sizes) > 100:
        plt.xscale('log')
        plt.xticks(buffer_sizes, buffer_sizes)  # Show actual values on x-axis
    
    plt.tight_layout()
    plt.show()

buffer_sizes = [102400 + (51200 * i) for i in range(198)]  # Buffer sizes from 102400 to 10240000

calculator = latency_calculator()

directory = "../_build/build/quic/samples"

for buffer_size in buffer_sizes:
    print(f"Testing buffer size: {buffer_size}")
    # Start server and client processes
    server = subprocess.Popen(
        ['stdbuf', '-oL', './latency', '--mode=server'],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=directory
    )
    time.sleep(1)  # Allow server to start

    client = subprocess.Popen(
        ['./latency', '--mode=client', '--latency_buffer_size', str(buffer_size)],
        stdout=subprocess.DEVNULL, cwd=directory
    )

    log_found = False

    while True:
        if server.poll() is not None:
            print("Server exited unexpectedly")
            break

        line = server.stdout.readline()
        if line:
            if "Parsed FileID: 999" in line:
                log_found = True
                break  # Latency test complete

    # Terminate processes
    server.kill()
    client.kill()
    server.wait()
    client.wait()

    # Process results
    if log_found:
        calculator.save_median_latency(buffer_size)
    else:
        print(f"Timeout for buffer size: {buffer_size}")

# After all tests complete
plot_graph(calculator.median_latency)

