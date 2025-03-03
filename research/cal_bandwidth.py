import re
import statistics
import matplotlib.pyplot as plt

def calculate_bandwidth_stats(filename):
    bandwidths = []
    
    # Read file and extract bandwidth values
    with open(filename, 'r') as file:
        for line in file:
            # Use regex to find bandwidth values
            match = re.search(r'Current Bandwidth: (\d+)', line)
            if match:
                bandwidth = int(match.group(1))
                bandwidths.append(bandwidth)
    
    if not bandwidths:
        return None, None, []  # Return None if no bandwidths found
    
    # Calculate average and median
    average = sum(bandwidths) / len(bandwidths)
    median = statistics.median(bandwidths)
    
    return average, median, bandwidths

def plot_bandwidths(bandwidths):
    plt.figure(figsize=(10, 5))
    plt.plot(bandwidths, marker='o')
    plt.title('Bandwidth Over Time')
    plt.xlabel('Sample Index')
    plt.ylabel('Bandwidth (bytes/s)')
    plt.grid(True)
    plt.ylim(min(bandwidths) - 10, max(bandwidths) + 10)  # Ensure y-axis range fits the data
    plt.show()

# Example usage
filename = '_build/build/quic/samples/temp'  # Replace with your file path
average, median, bandwidths = calculate_bandwidth_stats(filename)

if average is not None:
    print(f"Average bandwidth: {average:.2f} bytes/s")
    print(f"Median bandwidth: {median} bytes/s")
    plot_bandwidths(bandwidths)
else:
    print("No bandwidth data found in the file.")
