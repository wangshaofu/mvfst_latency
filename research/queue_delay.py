import re
import matplotlib.pyplot as plt

def parse_log_file(log_file):
    added_entries = []
    written_entries = []
    added_pattern = re.compile(r'\[Queueing Delay\]Added data to buffer at (\d+), data identifier: (\d+)')
    written_pattern = re.compile(r'\[Queueing Delay\]Written data to builder at (\d+), data identifier: (\d+)')
    
    with open(log_file, 'r') as f:
        for line in f:
            # Check for "Added data to buffer" lines
            added_match = added_pattern.search(line)
            if added_match:
                timestamp = int(added_match.group(1))
                data_id = int(added_match.group(2))
                added_entries.append({'data_id': data_id, 'timestamp': timestamp})
                continue
            # Check for "Written data to builder" lines
            written_match = written_pattern.search(line)
            if written_match:
                timestamp = int(written_match.group(1))
                data_id = int(written_match.group(2))
                written_entries.append({'data_id': data_id, 'timestamp': timestamp})
    # Sort added entries by data_id to ensure correct order
    added_entries.sort(key=lambda x: x['data_id'])
    return added_entries, written_entries

def calculate_queueing_delays(added_entries, written_entries):
    written_dict = {entry['data_id']: entry['timestamp'] for entry in written_entries}
    delays = []
    packet_ids = []
    
    # Iterate through pairs of consecutive added entries
    for i in range(len(added_entries) - 1):
        current = added_entries[i]
        next_entry = added_entries[i + 1]
        end_seq = next_entry['data_id'] - 1
        
        if end_seq in written_dict:
            added_time = current['timestamp']
            written_time = written_dict[end_seq]
            delay_ns = written_time - added_time
            delay_ms = delay_ns / 1e6
            delays.append(delay_ms)
            packet_ids.append(current['data_id'])
        else:
            print(f"No written entry found for end sequence {end_seq} (packet start: {current['data_id']})")
    
    return packet_ids, delays

def plot_delays(packet_ids, delays, output_file=None):
    plt.figure(figsize=(10, 6))
    plt.plot(packet_ids, delays, marker='o', linestyle='-', color='b')
    plt.xlabel('Packet Start Sequence Number')
    plt.ylabel('Queueing Delay (ms)')
    plt.title('Queueing Delay per Packet')
    plt.grid(True)
    plt.tight_layout()
    if output_file:
        plt.savefig(output_file)
    plt.show()

def print_delays(packet_ids, delays):
    print("Queueing Delay per Packet:")
    for packet_id, delay in zip(packet_ids, delays):
        print(f"Packet Start: {packet_id}, Delay: {delay:.3f} ms")

if __name__ == "__main__":
    log_file = '../_build/build/quic/samples/temp'  # Replace with your log file path
    added_entries, written_entries = parse_log_file(log_file)
    packet_ids, delays = calculate_queueing_delays(added_entries, written_entries)
    
    if packet_ids and delays:
        print_delays(packet_ids, delays)
        plot_delays(packet_ids, delays)
    else:
        print("No queueing delay data found.")