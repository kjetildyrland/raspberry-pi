#!/usr/bin/env python3
"""
Simple LoRa SX126X test script
Tests basic LoRa functionality with minimal code
"""

from LoRaRF import SX126x
import time


def simple_lora_test():
    """Simple LoRa test function"""
    print("=== Simple LoRa SX126X Test ===")

    try:
        # Initialize LoRa
        print("Initializing LoRa module...")
        lora = SX126x()

        # Begin LoRa
        if not lora.begin():
            print("❌ ERROR: Failed to initialize LoRa module!")
            print("Check connections:")
            print("- SPI wiring (MOSI, MISO, SCK)")
            print("- CS/NSS pin connection")
            print("- Reset pin connection")
            print("- Power supply (3.3V)")
            return False

        print("✅ LoRa module initialized successfully!")

        # Configure basic settings
        print("Configuring LoRa settings...")
        lora.setSPI(0, 0, 7800000)  # SPI bus 0, chip select 0
        lora.setFrequency(868000000)  # 868 MHz
        lora.setModulationParams(SF=7, BW=125, CR=5)
        lora.setPacketParams(
            PreambleLength=8, HeaderType=1, PayloadLength=255, CRCType=1
        )
        lora.setTxPower(14)  # 14 dBm

        print("✅ LoRa configured successfully!")

        # Send test messages
        test_messages = ["Hello World!", "LoRa Test 123", "SX126X Working!"]

        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test {i}/3 ---")
            print(f"Sending: '{message}'")

            # Convert to bytes and send
            message_bytes = message.encode("utf-8")
            result = lora.sendPacket(message_bytes)

            if result:
                print(f"✅ Message {i} sent successfully!")
            else:
                print(f"❌ Message {i} failed to send!")

            # Wait between messages
            time.sleep(2)

        print("\n=== Test Complete ===")
        print("If you see checkmarks above, your LoRa module is working!")
        print("Use a LoRa receiver or another LoRa device to verify transmission.")

        return True

    except ImportError:
        print("❌ ERROR: LoRaRF library not found!")
        print("Install with: pip install LoRaRF")
        return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check all wiring connections")
        print("2. Verify SPI is enabled: sudo raspi-config -> Interface Options -> SPI")
        print("3. Check power supply (3.3V for SX126X)")
        print("4. Verify GPIO pin numbers in LoRaRF library configuration")
        return False


if __name__ == "__main__":
    simple_lora_test()
