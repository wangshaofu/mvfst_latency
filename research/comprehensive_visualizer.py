import re
import statistics
import matplotlib.pyplot as plt

def read_timestamps(file_name):
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

def calculate_latencies(sent_file, received_file):
    sent_timestamps = read_timestamps(sent_file)
    received_timestamps = read_timestamps(received_file)
    
    latencies_ms = []
    file_ids = []
    
    common_file_ids = set(sent_timestamps.keys()) & set(received_timestamps.keys())
    
    for file_id in sorted(common_file_ids):
        sent_time = sent_timestamps[file_id]
        received_time = received_timestamps[file_id]
        latency_ms = (received_time - sent_time) / 1e6  # Convert ns to ms
        latencies_ms.append(latency_ms)
        file_ids.append(file_id)
    
    return file_ids, latencies_ms, sent_timestamps, received_timestamps

def print_latencies(file_ids, latencies_ms):
    print("Latency Results:")
    for file_id, latency in zip(file_ids, latencies_ms):
        print(f"FileID: {file_id}, Latency: {latency:.3f} ms")

def output_time_differences(sent_timestamps, received_timestamps, output_file='log_timeline.txt'):
    with open(output_file, 'w') as file:
        file.write("Time Differences Between Send and Receive Times:\n")
        common_file_ids = set(sent_timestamps.keys()) & set(received_timestamps.keys())
        for file_id in sorted(common_file_ids):
            sent_time = sent_timestamps[file_id]
            received_time = received_timestamps[file_id]
            time_diff_ns = received_time - sent_time  # Calculate difference in ns
            time_diff_ms = time_diff_ns / 1e6  # Convert ns to ms
            file.write(f"FileID {file_id}: SendTime {sent_time} ns, ReceiveTime {received_time} ns, Difference: {time_diff_ns} ns ({time_diff_ms:.3f} ms)\n")
    print(f"Time differences have been written to {output_file}")

def calculate_throughput_and_srtt(filename):
    timestamps = []
    throughputs = []
    srtts = []
    
    # Read file and extract timestamps, throughput, and SRTT values
    with open(filename, 'r') as file:
        for line in file:
            # Use regex to find timestamp, throughput, and SRTT values
            timestamp_match = re.search(r'At time (\d+)ns:', line)
            throughput_match = re.search(r'Throughput: (\d+)', line)
            srtt_match = re.search(r'SRTT: (\d+)', line)
            
            if timestamp_match and throughput_match and srtt_match:
                timestamp = int(timestamp_match.group(1))
                throughput = int(throughput_match.group(1)) / 1_000_000  # Convert bps to Mbps
                srtt = int(srtt_match.group(1)) / 1000
                
                timestamps.append(timestamp)
                throughputs.append(throughput)
                srtts.append(srtt)
    
    if not timestamps or not throughputs or not srtts:
        return None, None, [], [], []  # Return None if no data found
    
    # Calculate average and median
    average_throughput = sum(throughputs) / len(throughputs)
    median_throughput = statistics.median(throughputs)
    
    return average_throughput, median_throughput, timestamps, throughputs, srtts

def plot_all_data(file_ids, latencies_ms, throughput_timestamps, throughputs, srtts):
    plt.figure(figsize=(18, 5))
    
    # Plot latency
    plt.subplot(1, 3, 1)
    plt.plot(file_ids, latencies_ms, marker='o', linestyle='-')
    plt.xlabel('FileID')
    plt.ylabel('Latency (ms)')
    plt.title('Latency per FileID')
    plt.grid(True)
    
    # Plot throughput
    plt.subplot(1, 3, 2)
    plt.plot(throughput_timestamps, throughputs, marker='o')
    plt.title('Throughput Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('Throughput (Mbps)')
    plt.grid(True)
    
    # Plot SRTT
    plt.subplot(1, 3, 3)
    plt.plot(throughput_timestamps, srtts, marker='x', color='r')
    plt.title('SRTT Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('SRTT (ms)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Latency calculations
    sent_file = 'log_sent_timestamp.txt'
    received_file = 'log_received_timestamp.txt'
    file_ids, latencies_ms, sent_timestamps, received_timestamps = calculate_latencies(sent_file, received_file)
    print_latencies(file_ids, latencies_ms)
    output_time_differences(sent_timestamps, received_timestamps)
    
    # Throughput and SRTT calculations
    network_log_file = 'log_network_condition.txt'  # Ensure this file is in the same directory
    average_throughput, median_throughput, throughput_timestamps, throughputs, srtts = calculate_throughput_and_srtt(network_log_file)
    
    if average_throughput is not None:
        print(f"\nAverage throughput: {average_throughput:.2f} Mbps")
        print(f"Median throughput: {median_throughput:.2f} Mbps")

        # Plot all data
        plot_all_data(file_ids, latencies_ms, throughput_timestamps, throughputs, srtts)
    else:
        print("No throughput or SRTT data found in the file.")

