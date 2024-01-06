from LoRaRF import SX126x

# Initialize the LoRa module
LoRa = SX126x()

# Begin the LoRa module
if not LoRa.begin():
    raise Exception("Something wrong, can't begin LoRa radio")

# Set the SPI, frequency, modulation parameters, and packet parameters
LoRa.setSPI(0, 0, 7800000)
LoRa.setFrequency(868000000)
LoRa.setModulationParams(SF=7, BW=125, CR=5)
LoRa.setPacketParams(PreambleLength=16, HeaderType=1, PayloadLength=255, CRCType=1)

# Read the signal you want to send from a file
with open('rf/edited_rf_captures/868Mhz/withrepeats/rand_color_blinks.sub', 'r') as file:
    lines = file.readlines()

# Extract the raw signal data
raw_data_lines = [line for line in lines if line.startswith('RAW_Data:')]
raw_data = ' '.join(line.split(':', 1)[1].strip() for line in raw_data_lines)


print(raw_data)
# Convert the signal to bytes
signal_bytes = bytes(raw_data, 'utf-8')

# Send the signal
LoRa.sendPacket(signal_bytes)