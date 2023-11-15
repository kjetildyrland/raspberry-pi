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
