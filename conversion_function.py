from LoRaRF import SX126x
import time

print("Creating SX126x instance...")
LoRa = SX126x()

print("Available methods in SX126x:")
methods = [method for method in dir(LoRa) if not method.startswith("_")]
for method in methods:
    print(f"  - {method}")

print("\nTrying basic initialization...")

# First, just try to begin without any configuration
try:
    print("Attempting LoRa.begin()...")
    result = LoRa.begin()
    print(f"LoRa.begin() result: {result}")
    if result:
        print("✓ Success! Module initialized")

        # Try to get some basic info
        try:
            # Try different methods that might exist
            if hasattr(LoRa, "getChipVersion"):
                print(f"Chip version: {LoRa.getChipVersion()}")
            if hasattr(LoRa, "getMode"):
                print(f"Current mode: {LoRa.getMode()}")
        except Exception as e:
            print(f"Error getting module info: {e}")

    else:
        print("✗ Failed to initialize")

except Exception as e:
    print(f"Error during begin(): {e}")

# Now try to configure SPI if the module supports it
print("\nTrying SPI configuration...")
spi_methods = ["setSPI", "setSpi", "configureSPI", "spiConfig"]
spi_configured = False

for method_name in spi_methods:
    if hasattr(LoRa, method_name):
        try:
            method = getattr(LoRa, method_name)
            print(f"Found SPI method: {method_name}")
            # Try common parameter combinations
            try:
                method(0, 0, 1000000)  # bus, cs, speed
                print(f"✓ SPI configured with {method_name}")
                spi_configured = True
                break
            except Exception as e:
                print(f"Error with {method_name}(0, 0, 1000000): {e}")
                try:
                    method(0, 0)  # bus, cs only
                    print(f"✓ SPI configured with {method_name}(bus, cs)")
                    spi_configured = True
                    break
                except Exception as e2:
                    print(f"Error with {method_name}(0, 0): {e2}")
        except Exception as e:
            print(f"Error accessing {method_name}: {e}")

if not spi_configured:
    print("No SPI configuration method found or working")

# Try to set frequency
print("\nTrying frequency configuration...")
freq_methods = ["setFrequency", "setFreq", "frequency"]
for method_name in freq_methods:
    if hasattr(LoRa, method_name):
        try:
            method = getattr(LoRa, method_name)
            method(868000000)  # 868 MHz
            print(f"✓ Frequency set using {method_name}")
            break
        except Exception as e:
            print(f"Error with {method_name}: {e}")

print("\nNow attempting full initialization...")
try:
    if LoRa.begin():
        print("✓ Final initialization successful!")

        # Try basic packet transmission test
        print("Testing basic packet transmission...")
        try:
            # Look for transmission methods
            tx_methods = ["transmit", "send", "sendPacket", "write"]
            for method_name in tx_methods:
                if hasattr(LoRa, method_name):
                    print(f"Found transmission method: {method_name}")
        except Exception as e:
            print(f"Error checking transmission methods: {e}")

    else:
        print("✗ Final initialization failed")
        print("\nThis could be due to:")
        print("1. Incorrect wiring")
        print("2. Wrong GPIO pin configuration")
        print("3. SPI not enabled")
        print("4. Module power issues")

except Exception as e:
    print(f"Final initialization error: {e}")

print("\nDiagnostic complete.")
