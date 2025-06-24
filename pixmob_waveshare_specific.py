#!/usr/bin/env python3
"""
PIXMOB Controller for Waveshare SX1262 868M LoRa HAT
Uses the HAT's specific protocol format
"""

import sys
import time
import sx126x

def test_waveshare_protocol():
    """Test using Waveshare's documented protocol format"""
    print("=== Waveshare SX1262 HAT Specific Test ===")
    print("Using the HAT's documented protocol format")
    print("Reference: https://www.waveshare.com/wiki/SX1262_868M_LoRa_HAT")
    
    try:
        # Initialize with HAT-specific settings
        print("Initializing Waveshare SX1262 HAT...")
        lora = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,           # HAT is 868MHz specific
            addr=0,             # Our address
            power=22,           # Max power (10, 13, 17, 22dBm selectable)
            rssi=False,         # Disable for cleaner output
            air_speed=2400,     # Default air speed
            relay=False,
            buffer_size=240     # Max buffer size
        )
        
        print(f"HAT initialized: {lora.start_freq + lora.offset_freq} MHz")
        
        # Test 1: Raw PIXMOB data transmission
        print("\n=== Test 1: Raw PIXMOB Data ===")
        
        pixmob_commands = {
            'wake': bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40]),
            'gold': bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]),
        }
        
        # Extended wake sequence (as you suggested, 30+ seconds)
        print("Sending 45-second wake sequence...")
        wake_start = time.time()
        wake_count = 0
        
        while time.time() - wake_start < 45:
            lora.send(pixmob_commands['wake'])
            wake_count += 1
            time.sleep(0.2)  # 5 Hz transmission rate
            
            if wake_count % 25 == 0:  # Progress every 5 seconds
                elapsed = time.time() - wake_start
                print(f"  Wake progress: {elapsed:.0f}s, {wake_count} transmissions")
        
        print(f"Wake sequence complete: {wake_count} transmissions sent")
        
        # Test gold command
        print("\nSending GOLD command...")
        for i in range(20):
            lora.send(pixmob_commands['gold'])
            time.sleep(0.3)
            print(f"  Gold transmission {i+1}/20")
        
        response = input("\nAny PIXMOB response to raw data? (y/n): ").lower().strip()
        if response.startswith('y'):
            print("[SUCCESS] Raw data method works!")
            return True
        
        # Test 2: Waveshare protocol format
        print("\n=== Test 2: Waveshare Protocol Format ===")
        print("Using HAT's documented format: 'address,frequency,payload'")
        
        # According to docs: "node address,frequency,payload" like "20,868,Hello World"
        # Try broadcast to all addresses
        
        wake_msg = "0,868," + pixmob_commands['wake'].hex()
        gold_msg = "65535,868," + pixmob_commands['gold'].hex()  # Broadcast address
        
        print("Sending wake in protocol format...")
        for i in range(100):  # 20 seconds at 5Hz
            lora.send(wake_msg.encode())
            time.sleep(0.2)
            if i % 25 == 0:
                print(f"  Protocol wake: {i}/100")
        
        print("Sending gold in protocol format...")
        for i in range(10):
            lora.send(gold_msg.encode())
            time.sleep(0.5)
            print(f"  Protocol gold: {i+1}/10")
        
        response = input("\nAny PIXMOB response to protocol format? (y/n): ").lower().strip()
        if response.startswith('y'):
            print("[SUCCESS] Protocol format works!")
            return True
        
        # Test 3: Different air speeds
        print("\n=== Test 3: Different Air Speeds ===")
        print("HAT supports: 1200, 2400, 4800, 9600, 19200, 38400, 62500 bps")
        
        air_speeds = [1200, 2400, 4800, 9600]
        
        for speed in air_speeds:
            print(f"\nTesting air speed: {speed} bps")
            try:
                test_lora = sx126x.sx126x(
                    serial_num="/dev/ttyS0",
                    freq=868,
                    addr=0,
                    power=22,
                    rssi=False,
                    air_speed=speed,
                    relay=False
                )
                
                # Quick test
                for i in range(10):
                    test_lora.send(pixmob_commands['gold'])
                    time.sleep(0.2)
                
                response = input(f"Any response at {speed} bps? (y/n): ").lower().strip()
                if response.startswith('y'):
                    print(f"[SUCCESS] {speed} bps works!")
                    return True
                    
            except Exception as e:
                print(f"Error at {speed} bps: {e}")
        
        # Test 4: Different power levels
        print("\n=== Test 4: Different Power Levels ===")
        print("HAT supports: 10, 13, 17, 22 dBm")
        
        power_levels = [22, 17, 13, 10]  # Start with highest
        
        for power in power_levels:
            print(f"\nTesting power: {power} dBm")
            try:
                test_lora = sx126x.sx126x(
                    serial_num="/dev/ttyS0",
                    freq=868,
                    addr=0,
                    power=power,
                    rssi=False,
                    air_speed=2400,
                    relay=False
                )
                
                # Quick test
                for i in range(10):
                    test_lora.send(pixmob_commands['gold'])
                    time.sleep(0.2)
                
                response = input(f"Any response at {power} dBm? (y/n): ").lower().strip()
                if response.startswith('y'):
                    print(f"[SUCCESS] {power} dBm works!")
                    return True
                    
            except Exception as e:
                print(f"Error at {power} dBm: {e}")
        
        return False
        
    except Exception as e:
        print(f"Waveshare test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frequency_variants():
    """Test if PIXMOB is actually on 915MHz instead of 868MHz"""
    print("\n=== Frequency Variant Test ===")
    print("Your RF captures exist for both 868MHz and 915MHz")
    print("Testing if PIXMOB expects 915MHz instead...")
    
    # Check if you have a 915MHz HAT or can modify frequency
    print("Note: Your HAT is 868MHz specific, but let's test frequency offset")
    
    try:
        # Try different frequency offsets within the 868MHz band
        base_freq = 868
        offsets = [0, 1, 2, -1, -2]  # MHz offsets
        
        for offset in offsets:
            test_freq = base_freq + offset
            if 850 <= test_freq <= 930:  # Valid range for SX1262
                print(f"\nTesting frequency: {test_freq} MHz")
                
                try:
                    lora = sx126x.sx126x(
                        serial_num="/dev/ttyS0",
                        freq=test_freq,
                        addr=0,
                        power=22,
                        rssi=False,
                        air_speed=2400,
                        relay=False
                    )
                    
                    gold_cmd = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
                    
                    # Quick test
                    for i in range(15):
                        lora.send(gold_cmd)
                        time.sleep(0.2)
                    
                    response = input(f"Any response at {test_freq} MHz? (y/n): ").lower().strip()
                    if response.startswith('y'):
                        print(f"[SUCCESS] {test_freq} MHz works!")
                        return test_freq
                        
                except Exception as e:
                    print(f"Error at {test_freq} MHz: {e}")
        
        return None
        
    except Exception as e:
        print(f"Frequency test error: {e}")
        return None

def main():
    """Main test function"""
    print("PIXMOB Controller for Waveshare SX1262 868M LoRa HAT")
    print("====================================================")
    print("Reference: https://www.waveshare.com/wiki/SX1262_868M_LoRa_HAT")
    print()
    print("Important notes:")
    print("- Your HAT uses LoRa modulation (not OOK/ASK)")
    print("- PIXMOB typically expects OOK/ASK modulation")
    print("- This test explores compatibility workarounds")
    print()
    
    # Test Waveshare-specific approaches
    if test_waveshare_protocol():
        print("\n[SUCCESS] Found working method with Waveshare HAT!")
        return
    
    # Test frequency variants
    working_freq = test_frequency_variants()
    if working_freq:
        print(f"\n[SUCCESS] Found working frequency: {working_freq} MHz")
        return
    
    # Final diagnosis
    print("\n=== FINAL DIAGNOSIS ===")
    print("No PIXMOB response detected with any method.")
    print()
    print("Root cause analysis:")
    print("1. PROTOCOL MISMATCH:")
    print("   - Waveshare HAT: LoRa modulation")
    print("   - PIXMOB devices: OOK/ASK modulation")
    print("   - These are incompatible at RF level")
    print()
    print("2. SOLUTIONS:")
    print("   - Get an OOK/ASK transmitter (like CC1101 or RFM69)")
    print("   - Use a different LoRa module that supports OOK mode")
    print("   - Try PIXMOB devices that support LoRa (if they exist)")
    print("   - Use SDR (Software Defined Radio) for OOK transmission")
    print()
    print("3. VERIFICATION:")
    print("   - Use RTL-SDR to monitor actual PIXMOB frequency/modulation")
    print("   - Capture signals from working PIXMOB transmitter")
    print("   - Compare with your HAT's output spectrum")

if __name__ == "__main__":
    main() 