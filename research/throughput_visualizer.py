import re
import statistics
import matplotlib.pyplot as plt

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
                srtt = int(srtt_match.group(1))
                
                timestamps.append(timestamp)
                throughputs.append(throughput)
                srtts.append(srtt)
    
    if not timestamps or not throughputs or not srtts:
        return None, None, [], [], []  # Return None if no data found
    
    # Calculate average and median
    average_throughput = sum(throughputs) / len(throughputs)
    median_throughput = statistics.median(throughputs)
    
    return average_throughput, median_throughput, timestamps, throughputs, srtts

def plot_data(timestamps, throughputs, srtts):
    plt.figure(figsize=(15, 5))
    
    # Plot throughput
    plt.subplot(1, 2, 1)
    plt.plot(timestamps, throughputs, marker='o')
    plt.title('Throughput Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('Throughput (Mbps)')
    plt.grid(True)
    
    # Plot SRTT
    plt.subplot(1, 2, 2)
    plt.plot(timestamps, srtts, marker='x', color='r')
    plt.title('SRTT Over Time')
    plt.xlabel('Timestamp (ns)')
    plt.ylabel('SRTT (us)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

# Example usage
filename = 'log_network_condition.txt'  # Replace with your file path
average_throughput, median_throughput, timestamps, throughputs, srtts = calculate_throughput_and_srtt(filename)

if average_throughput is not None:
    print(f"Average throughput: {average_throughput:.2f} Mbps")
    print(f"Median throughput: {median_throughput} Mbps")
    plot_data(timestamps, throughputs, srtts)
else:
    print("No throughput or SRTT data found in the file.")

