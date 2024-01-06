# Read the signal you want to send from a file
with open('rf/edited_rf_captures/868Mhz/withrepeats/rand_color_blinks.sub', 'r') as file:
    lines = file.readlines()

# Extract the raw signal data
raw_data_lines = [line for line in lines if line.startswith('RAW_Data:')]
raw_data = ' '.join(line.split(':', 1)[1].strip() for line in raw_data_lines)


#print(raw_data)
# Convert the signal to bytes

signal_bytes = bytes(raw_data, 'utf-8')

print(signal_bytes)
