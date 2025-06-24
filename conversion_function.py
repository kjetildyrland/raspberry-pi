from LoRaRF import SX126x
import time

print("Creating SX126x instance...")
LoRa = SX126x()

print("Available methods in SX126x:")
methods = [method for method in dir(LoRa) if not method.startswith("_")]
for method in methods:
    print(f"  - {method}")

print("\nTrying basic initialization...")

# Configure SPI first
print("Configuring SPI...")
try:
    LoRa.setSPI(0, 0, 7800000)  # bus 0, CS 0, 7.8MHz
    print("[SUCCESS] SPI configured")
except Exception as e:
    print(f"SPI error: {e}")

# Try to configure GPIO pins before begin()
print("Trying to configure GPIO pins...")
gpio_methods = ["setPin", "setPins", "setResetPin", "setDio1Pin", "setBusyPin"]
for method_name in gpio_methods:
    if hasattr(LoRa, method_name):
        print(f"Found GPIO method: {method_name}")

# Try to set individual pins if methods exist
try:
    if hasattr(LoRa, "setResetPin"):
        LoRa.setResetPin(22)
        print("Reset pin set to GPIO 22")
    if hasattr(LoRa, "setDio1Pin"):
        LoRa.setDio1Pin(17)
        print("DIO1 pin set to GPIO 17")
    if hasattr(LoRa, "setBusyPin"):
        LoRa.setBusyPin(27)
        print("BUSY pin set to GPIO 27")
    if hasattr(LoRa, "setPin"):
        LoRa.setPin(reset=22, dio1=17, busy=27)
        print("All pins set using setPin method")
except Exception as e:
    print(f"GPIO pin configuration error: {e}")

# Set frequency before begin
print("Setting frequency...")
try:
    LoRa.setFrequency(868000000)  # 868 MHz
    print("[SUCCESS] Frequency set to 868 MHz")
except Exception as e:
    print(f"Frequency error: {e}")

# Now try to begin
print("\nAttempting LoRa.begin()...")
try:
    result = LoRa.begin()
    print(f"LoRa.begin() result: {result}")
    if result:
        print("[SUCCESS] Module initialized successfully!")

        # Try to get module info
        try:
            if hasattr(LoRa, "getChipVersion"):
                print(f"Chip version: {LoRa.getChipVersion()}")
        except Exception as e:
            print(f"Error getting chip info: {e}")

    else:
        print("[FAILED] Module initialization failed")

except Exception as e:
    print(f"Error during begin(): {e}")
    print(
        "This 'tuple index out of range' error suggests GPIO pin configuration issues"
    )

print("\nDiagnostic complete.")
print("\nRecommendation: Consider using the working C++ RadioLib version instead")
print("The C++ version in radiolib_raspberry/ is already configured and working")
