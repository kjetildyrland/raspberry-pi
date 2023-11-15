import time
import serial

def read_sub_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("RAW_Data:"):
                return line.split(": ")[1].strip()
    return ""

def format_data_for_transmission(raw_data):
    # This function should convert the raw timing data into a format
    # suitable for transmission. This part depends on how your LoRa module
    # expects data and how it transmits it. You might need to convert
    # these timings into a byte sequence or some other format.
    # This is a placeholder function and needs to be implemented.
    return bytes(raw_data, 'utf-8')

# Set up the LoRa serial connection
lora = serial.Serial(port='/dev/ttyS0', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1)

# Read and parse the .sub file
sub_file_path = "rf/edited_rf_captures/868Mhz/white_fastfade.sub"  # Replace with your .sub file path
raw_data = read_sub_file(sub_file_path)

# Format the data for transmission
formatted_data = format_data_for_transmission(raw_data)

# Transmit the data
lora.write(formatted_data)
time.sleep(0.2)  # Optional delay

# Close the serial connection
lora.close()
