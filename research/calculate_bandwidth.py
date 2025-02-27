import re
import statistics

def calculate_bandwidth_stats(filename):
    bandwidths = []
    
    # Read file and extract bandwidth values
    with open(filename, 'r') as file:
        for line in file:
            # Use regex to find bandwidth values
            match = re.search(r'Estimated Bandwidth: (\d+) bytes/s', line)
            if match:
                bandwidth = int(match.group(1))
                bandwidths.append(bandwidth)
    
    if not bandwidths:
        return None, None  # Return None if no bandwidths found
    
    # Calculate average and median
    average = sum(bandwidths) / len(bandwidths)
    median = statistics.median(bandwidths)
    
    return average, median

# Example usage
filename = '_build/build/quic/samples/temp_log'  # Replace with your file path
average, median = calculate_bandwidth_stats(filename)

if average is not None:
    print(f"Average bandwidth: {average:.2f} bytes/s")
    print(f"Median bandwidth: {median} bytes/s")
else:
    print("No bandwidth data found in the file.")