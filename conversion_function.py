from LoRaRF import SX126x

LoRa = SX126x()


# set to use SPI with bus id 0 and cs id 1 and speed 7.8 Mhz
LoRa.setSPI(0, 0, 7800000)

if not LoRa.begin():
    raise Exception("Something wrong, can't begin LoRa radio")

# set transmit power to +2 dBm for SX1262
LoRa.setTxPower(2, LoRa.TX_POWER_SX1262)

# Set frequency to 868 Mhz
LoRa.setFrequency(868000000)

# Configure modulation parameter including spreading factor (SF), bandwidth (BW), and coding rate (CR)
# Receiver must have same SF and BW setting with transmitter to be able to receive LoRa packet
print(
    "Set modulation parameters:\n\tSpreading factor = 7\n\tBandwidth = 125 kHz\n\tCoding rate = 4/5"
)
sf = 7  # LoRa spreading factor: 7
bw = 125000  # Bandwidth: 125 kHz
cr = 5  # Coding rate: 4/5
LoRa.setLoRaModulation(sf, bw, cr)

# Configure packet parameter including header type, preamble length, payload length, and CRC type
# The explicit packet includes header contain CR, number of byte, and CRC type
# Receiver can receive packet with different CR and packet parameters in explicit header mode
print(
    "Set packet parameters:\n\tExplicit header type\n\tPreamble length = 12\n\tPayload Length = 15\n\tCRC on"
)
headerType = LoRa.HEADER_EXPLICIT  # Explicit header mode
preambleLength = 16  # Set preamble length to 12
payloadLength = 15  # Initialize payloadLength to 15
crcType = True  # Set CRC enable
LoRa.setLoRaPacket(headerType, preambleLength, payloadLength, crcType)

# Set syncronize word for public network (0x3444)
LoRa.setSyncWord(0x3444)


# message and counter to transmit
message = "HeLoRa World!\0"
messageList = list(message)
for i in range(len(messageList)):
    messageList[i] = ord(messageList[i])
counter = 0

LoRa.beginPacket()
LoRa.write(message, len(message))  # write multiple bytes
LoRa.write(counter)  # write single byte
LoRa.endPacket()
LoRa.wait()
counter += 1


def format_data_for_transmission(raw_data):
    binary_stream = []
    time_unit = 510  # Basic unit of time in microseconds

    # Splitting the raw data into individual durations
    durations = [int(x) for x in raw_data.split()]

    for duration in durations:
        signal_state = 1 if duration > 0 else 0
        num_units = round(abs(duration) / time_unit)

        # Appending the corresponding number of bits to the binary stream
        binary_stream.extend([signal_state] * num_units)

    # Convert the binary stream to bytes
    byte_data = convert_binary_to_bytes(binary_stream)
    return byte_data


def convert_binary_to_bytes(binary_stream):
    # Placeholder for conversion logic
    # Implement based on how you need to pack bits into bytes
    # and if there's additional encoding/CRC to consider
    return bytes(binary_stream)
