#!/usr/bin/env python3
"""
Proper LoRa SX126X transmission script for Raspberry Pi
This script correctly initializes and uses the LoRa module for transmission
"""

from LoRaRF import SX126x
import time
import sys


def initialize_lora():
    """Initialize the LoRa module with proper settings"""
    try:
        # Initialize the LoRa module
        LoRa = SX126x()

        # Begin the LoRa module
        if not LoRa.begin():
            raise Exception("Failed to initialize LoRa radio")

        # Configure SPI and basic settings
        LoRa.setSPI(0, 0, 7800000)  # SPI bus 0, CS 0, 7.8MHz

        # Set frequency to 868MHz (adjust based on your module)
        LoRa.setFrequency(868000000)

        # Set modulation parameters
        # SF=7: Spreading Factor (7-12, higher = longer range but slower)
        # BW=125: Bandwidth in kHz (125, 250, 500)
        # CR=5: Coding Rate (5-8, higher = more error correction)
        LoRa.setModulationParams(SF=7, BW=125, CR=5)

        # Set packet parameters
        # PreambleLength=8: Number of preamble symbols
        # HeaderType=1: Explicit header (0=implicit, 1=explicit)
        # PayloadLength=255: Maximum payload length
        # CRCType=1: CRC enabled (0=disabled, 1=enabled)
        LoRa.setPacketParams(
            PreambleLength=8, HeaderType=1, PayloadLength=255, CRCType=1
        )

        # Set transmission power (2-22 dBm)
        LoRa.setTxPower(14)

        print("LoRa module initialized successfully!")
        print(f"Frequency: 868 MHz")
        print(f"Spreading Factor: 7")
        print(f"Bandwidth: 125 kHz")
        print(f"Coding Rate: 4/5")
        print(f"TX Power: 14 dBm")

        return LoRa

    except Exception as e:
        print(f"Error initializing LoRa: {e}")
        return None


def send_test_message(lora, message="Hello LoRa World!"):
    """Send a test message via LoRa"""
    try:
        # Convert message to bytes
        message_bytes = message.encode("utf-8")

        print(f"Sending message: '{message}'")
        print(f"Message bytes: {message_bytes}")
        print(f"Message length: {len(message_bytes)} bytes")

        # Send the packet
        result = lora.sendPacket(message_bytes)

        if result:
            print("✓ Message transmitted successfully!")
        else:
            print("✗ Message transmission failed!")

        return result

    except Exception as e:
        print(f"Error sending message: {e}")
        return False


def send_pixmob_data(lora):
    """Send PIXMOB-style data (converted from your .sub files)"""
    try:
        # These are the converted hex values from your PIXMOB.py script
        # Each represents a different color/pattern command
        pixmob_commands = [
            # gold_fade_in
            bytes(
                [0xAA, 0xAA, 0x65, 0x21, 0x24, 0x6D, 0x61, 0x23, 0x11, 0x61, 0x2B, 0x40]
            ),
            # gold_fast_fade
            bytes(
                [0xAA, 0xAA, 0x5B, 0x61, 0x24, 0x6D, 0x61, 0x12, 0x51, 0x61, 0x22, 0x80]
            ),
            # white_fastfade
            bytes([0xAA, 0xAA, 0x56, 0xA1, 0x2D, 0x6D, 0x6D, 0x52, 0x51, 0x61, 0x0B]),
            # wine_fade_in
            bytes(
                [0xAA, 0xAA, 0x69, 0xA1, 0x21, 0x2D, 0x61, 0x23, 0x11, 0x61, 0x28, 0x40]
            ),
        ]

        command_names = [
            "gold_fade_in",
            "gold_fast_fade",
            "white_fastfade",
            "wine_fade_in",
        ]

        for i, (command, name) in enumerate(zip(pixmob_commands, command_names)):
            print(f"\nSending PIXMOB command {i+1}/4: {name}")
            print(f"Command bytes: {command.hex()}")

            result = lora.sendPacket(command)

            if result:
                print(f"✓ {name} command transmitted successfully!")
            else:
                print(f"✗ {name} command transmission failed!")

            # Wait between transmissions
            time.sleep(2)

    except Exception as e:
        print(f"Error sending PIXMOB data: {e}")


def main():
    """Main function"""
    print("=== LoRa SX126X Transmitter ===")
    print("Initializing LoRa module...")

    # Initialize LoRa
    lora = initialize_lora()
    if not lora:
        print("Failed to initialize LoRa module. Exiting.")
        sys.exit(1)

    try:
        while True:
            print("\n=== LoRa Transmission Menu ===")
            print("1. Send test message")
            print("2. Send custom message")
            print("3. Send PIXMOB commands")
            print("4. Exit")

            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                send_test_message(lora)

            elif choice == "2":
                message = input("Enter message to send: ").strip()
                if message:
                    send_test_message(lora, message)
                else:
                    print("No message entered.")

            elif choice == "3":
                print("Sending PIXMOB commands...")
                send_pixmob_data(lora)

            elif choice == "4":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please enter 1-4.")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("Program finished.")


if __name__ == "__main__":
    main()
