import re
import statistics
import matplotlib.pyplot as plt

def read_timestamps(file_name):
    timestamps = {}
    with open(file_name, 'r') as file:
        for line in file:
            # Use regex to extract FileID and timestamp
            match = re.match(r'(?:FileID|ID):\s*(\d+)\s+.*Time:\s*(\d+)\s*ns', line)
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

def output_time_differences(timestamps_a, timestamps_b, label_a, label_b, output_file):
    with open(output_file, 'w') as file:
        file.write(f"Time Differences Between {label_a} and {label_b} Times:\n")
        common_file_ids = set(timestamps_a.keys()) & set(timestamps_b.keys())
        time_diffs_ms = []
        file_ids = []
        for file_id in sorted(common_file_ids):
            time_a = timestamps_a[file_id]
            time_b = timestamps_b[file_id]
            time_diff_ns = time_b - time_a  # Difference in ns
            time_diff_ms = time_diff_ns / 1e6  # Convert ns to ms
            time_diffs_ms.append(time_diff_ms)
            file_ids.append(file_id)
            file.write(f"FileID {file_id}: {label_a} {time_a} ns, {label_b} {time_b} ns, Difference: {time_diff_ns} ns ({time_diff_ms:.3f} ms)\n")
    print(f"Time differences have been written to {output_file}")
    return file_ids, time_diffs_ms

def calculate_throughput_srtt_buffer(filename):
    timestamps = []
    throughputs = []
    srtts = []
    buffer_sizes = []
    
    # Read file and extract timestamps, throughput, SRTT, and Buffer Size values
    with open(filename, 'r') as file:
        for line in file:
            # Use regex to find timestamp, throughput, SRTT, and Buffer Size values
            timestamp_match = re.search(r'At time (\d+)ns:', line)
            throughput_match = re.search(r'Throughput: (\d+)', line)
            srtt_match = re.search(r'SRTT: (\d+)', line)
            buffer_size_match = re.search(r'Buffer Size: (\d+)', line)
            
            if timestamp_match and throughput_match and srtt_match and buffer_size_match:
                timestamp = int(timestamp_match.group(1))
                throughput = int(throughput_match.group(1)) / 1_000_000  # Convert bps to Mbps
                srtt = int(srtt_match.group(1)) / 1000  # Convert us to ms
                buffer_size = int(buffer_size_match.group(1)) / 1024  # Convert bytes to KB
                
                timestamps.append(timestamp)
                throughputs.append(throughput)
                srtts.append(srtt)
                buffer_sizes.append(buffer_size)
    
    if not timestamps or not throughputs or not srtts or not buffer_sizes:
        return None, None, [], [], [], []  # Return None if no data found
    
    # Calculate average and median throughput
    average_throughput = sum(throughputs) / len(throughputs)
    median_throughput = statistics.median(throughputs)
    
    return average_throughput, median_throughput, timestamps, throughputs, srtts, buffer_sizes

def plot_all_data(file_ids, latencies_ms, builder_diffs_ms, throughput_timestamps, throughputs, srtts, buffer_sizes):
    plt.figure(figsize=(18, 12))
    
    # Plot latency
    plt.subplot(3, 2, 1)
    plt.plot(file_ids, latencies_ms, marker='o', linestyle='-')
    plt.xlabel('FileID')
    plt.ylabel('Latency (ms)')
    plt.title('Latency per FileID (Send to Receive)')
    plt.grid(True)
    
    # Plot builder time differences
    plt.subplot(3, 2, 2)
    plt.plot(file_ids, builder_diffs_ms, marker='s', linestyle='-', color='g')
    plt.xlabel('FileID')
    plt.ylabel('Time Difference (ms)')
    plt.title('Time Difference per FileID (Send to Builder)')
    plt.grid(True)
    
    # Plot throughput
    plt.subplot(3, 2, 3)
    plt.plot(throughput_timestamps, throughputs, marker='o')
    plt.title('Throughput Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('Throughput (Mbps)')
    plt.grid(True)
    
    # Plot SRTT
    plt.subplot(3, 2, 4)
    plt.plot(throughput_timestamps, srtts, marker='x', color='r')
    plt.title('SRTT Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('SRTT (ms)')
    plt.grid(True)
    
    # Plot Buffer Size
    plt.subplot(3, 2, 5)
    plt.plot(throughput_timestamps, buffer_sizes, marker='^', linestyle='-', color='m')
    plt.title('Buffer Size Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('Buffer Size (KB)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Latency calculations
    builder_file = 'log_builder_timestamp.txt'
    sent_file = 'log_sent_timestamp.txt'
    received_file = 'log_received_timestamp.txt'
    
    # Read timestamps
    builder_timestamps = read_timestamps(builder_file)
    sent_timestamps = read_timestamps(sent_file)
    received_timestamps = read_timestamps(received_file)
    
    # Calculate latencies
    file_ids, latencies_ms, _, _ = calculate_latencies(sent_file, received_file)
    print_latencies(file_ids, latencies_ms)
    
    # Output time differences for Send to Receive
    output_file_receive = 'log_receive_timeline.txt'
    _, _ = output_time_differences(sent_timestamps, received_timestamps, 'SendTime', 'ReceiveTime', output_file_receive)
    
    # Output time differences for Builder to Send
    output_file_builder = 'log_builder_timeline.txt'
    builder_file_ids, builder_diffs_ms = output_time_differences(sent_timestamps, builder_timestamps, 'SendTime', 'BuilderTime', output_file_builder)
    
    # Throughput, SRTT, and Buffer Size calculations
    network_log_file = 'log_network_condition.txt'  # Ensure this file is in the same directory
    average_throughput, median_throughput, throughput_timestamps, throughputs, srtts, buffer_sizes = calculate_throughput_srtt_buffer(network_log_file)
    
    if average_throughput is not None:
        print(f"\nAverage throughput: {average_throughput:.2f} Mbps")
        print(f"Median throughput: {median_throughput:.2f} Mbps")
    
        # Plot all data
        plot_all_data(file_ids, latencies_ms, builder_diffs_ms, throughput_timestamps, throughputs, srtts, buffer_sizes)
    else:
        print("No throughput, SRTT, or Buffer Size data found in the file.")
