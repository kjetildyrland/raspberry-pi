from LoRaRF import SX126x
import time

LoRa = SX126x()

# set to use SPI with bus id 0 and cs id 1 and speed 7.8 Mhz
LoRa.setSpi(0, 0, 7800000)

if not LoRa.begin():
    raise Exception("Something wrong, can't begin LoRa radio")

# Set frequency to 868 MHz (for EU/UK PixMob bracelets)
# Use 915 MHz for US bracelets: LoRa.setFrequency(915000000)
LoRa.setFrequency(868000000)

# Configure for OOK modulation instead of LoRa
# PixMob bracelets use OOK (On-Off Keying), not LoRa modulation
try:
    # Try to set OOK mode - this depends on your LoRaRF library version
    LoRa.setOOK(True)
except AttributeError:
    print("Warning: OOK mode not directly supported by this library")
    print("You may need to use a different library or radio configuration")

# Set transmit power
LoRa.setTxPower(2, LoRa.TX_POWER_SX1262)

# Enable direct transmission mode for OOK
try:
    LoRa.transmitDirect()
except AttributeError:
    print("Warning: Direct transmission mode not available")


def format_data_for_transmission(raw_data):
    """
    Convert PixMob raw timing data to binary stream for transmission

    Args:
        raw_data (str): Space-separated timing values (e.g., "510 -510 510 -1020 ...")

    Returns:
        list: Binary stream representing the timing data
    """
    binary_stream = []
    time_unit = 510  # Basic unit of time in microseconds

    # Split the raw data into individual durations
    durations = [int(x) for x in raw_data.split()]

    for duration in durations:
        # Positive values = signal ON (1), negative values = signal OFF (0)
        signal_state = 1 if duration > 0 else 0
        num_units = round(abs(duration) / time_unit)

        # Append the corresponding number of bits to the binary stream
        binary_stream.extend([signal_state] * num_units)

    return binary_stream


def transmit_pixmob_signal(binary_stream, bit_duration_us=510):
    """
    Transmit binary stream using direct OOK modulation

    Args:
        binary_stream (list): Binary data to transmit
        bit_duration_us (int): Duration of each bit in microseconds
    """
    try:
        for bit in binary_stream:
            if bit == 1:
                # Turn on transmission
                LoRa.transmitDirect()
            else:
                # Turn off transmission
                LoRa.standby()

            # Wait for bit duration
            time.sleep(bit_duration_us / 1000000.0)  # Convert to seconds

        # Ensure transmission is off at the end
        LoRa.standby()

    except Exception as e:
        print(f"Error during transmission: {e}")
        LoRa.standby()


def send_pixmob_command(command_data, repeat_count=5):
    """
    Send a PixMob command with repeats

    Args:
        command_data (str): Raw timing data string
        repeat_count (int): Number of times to repeat the command
    """
    binary_stream = format_data_for_transmission(command_data)

    print(f"Sending PixMob command (repeated {repeat_count} times)...")
    print(f"Binary stream length: {len(binary_stream)} bits")

    for i in range(repeat_count):
        print(f"Transmission {i+1}/{repeat_count}")
        transmit_pixmob_signal(binary_stream)
        time.sleep(0.1)  # Small delay between repeats


# Example PixMob commands (868 MHz versions)
PIXMOB_COMMANDS = {
    "nothing": "510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -1020 510 -510 510 -510 1020 -510 510 -510 510 -2040 510 -1530 1020 -2040 510 -510 1020 -2040 510 -510 510 -1530 1020 -1020 510 -1530 1020 -510 510 -510 510 -2040 510 -2040 510 -510 510 -1020 510",
    "gold_fade_in": "510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -1020 1020 -510 510 -1020 510 -2040 510 -1020 510 -2040 510 -1020 510 -510 1020 -510 510 -510 1020 -2040 510 -1020 510 -510 1020 -1020 510 -510 1020 -2040 510 -1530 1020 -1020 510 -510 510",
    "white_fastfade": "510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -1020 510 -510 1020 -1020 510 -510 510 -2040 510 -1020 510 -510 1020 -510 1020 -1530 510 -1020 510 -1020 510 -510 1020 -2040 510 -2040 510 -510 510 -1020 510 -510 1020 -1020 510 -510 1020",
    "wine_fade_in": "510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -510 510 -1020 1020 -510 1020 -510 510 -2040 510 -1020 510 -2040 510 -1020 510 -510 1020 -510 510 -510 1020 -2040 510 -1020 510 -510 1020 -1020 510 -510 1020 -2040 510 -1530 1020 -2040 510",
}

# Example usage - wake up bracelets first
if __name__ == "__main__":
    print("Waking up PixMob bracelets...")
    # Send "nothing" command repeatedly for 30 seconds to wake up sleeping bracelets
    wake_duration = 30  # seconds
    wake_start = time.time()

    while time.time() - wake_start < wake_duration:
        send_pixmob_command(PIXMOB_COMMANDS["nothing"], repeat_count=1)
        time.sleep(1)

    print("Bracelets should now be awake. Sending color commands...")

    # Send actual color commands
    send_pixmob_command(PIXMOB_COMMANDS["gold_fade_in"], repeat_count=10)
    time.sleep(2)
    send_pixmob_command(PIXMOB_COMMANDS["white_fastfade"], repeat_count=10)
    time.sleep(2)
    send_pixmob_command(PIXMOB_COMMANDS["wine_fade_in"], repeat_count=10)

    print("Transmission complete!")
