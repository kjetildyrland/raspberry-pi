#!/usr/bin/env python3
"""
PIXMOB Controller using Official Waveshare Message Format
Based on the official main.py format discovered in SX126X_LoRa_HAT_Code
"""

import sys
import time
import sx126x

def create_waveshare_message(target_addr, target_freq, source_addr, source_freq, payload):
    """
    Create message in official Waveshare format:
    [Target High][Target Low][Target Freq][Source High][Source Low][Source Freq][Payload]
    """
    offset_freq_target = target_freq - (850 if target_freq > 850 else 410)
    offset_freq_source = source_freq - (850 if source_freq > 850 else 410)
    
    message = (
        bytes([target_addr >> 8]) +           # Target address high byte
        bytes([target_addr & 0xff]) +         # Target address low byte  
        bytes([offset_freq_target]) +         # Target frequency offset
        bytes([source_addr >> 8]) +           # Source address high byte
        bytes([source_addr & 0xff]) +         # Source address low byte
        bytes([offset_freq_source]) +         # Source frequency offset
        payload                               # Actual payload
    )
    
    return message

def test_official_format():
    """Test PIXMOB using the official Waveshare message format"""
    print("=== PIXMOB Test: Official Waveshare Format ===")
    print("Using the exact format from official main.py")
    print()
    
    # Initialize exactly like the official example
    print("Initializing with official settings...")
    node = sx126x.sx126x(
        serial_num="/dev/ttyS0",
        freq=868,           # Official example uses 868
        addr=0,             # Our address
        power=22,           # Max power
        rssi=False,         # Disable for cleaner output
        air_speed=2400,     # Official default
        relay=False         # No relay
    )
    
    print(f"Node initialized: Address {node.addr}, Frequency {node.start_freq + node.offset_freq} MHz")
    
    # PIXMOB command data
    pixmob_commands = {
        'wake': bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40]),
        'gold': bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]),
        'red': bytes([0xaa, 0xaa, 0x55, 0xa1, 0x25, 0x25, 0x25, 0x18, 0x8d, 0xa1, 0x0a, 0x40]),
        'blue': bytes([0xaa, 0xaa, 0x65, 0x21, 0x26, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]),
    }
    
    # Test 1: Broadcast to all devices
    print("\n=== Test 1: Broadcast Format ===")
    print("Broadcasting to address 65535 (all devices)")
    
    wake_msg = create_waveshare_message(
        target_addr=65535,      # Broadcast address
        target_freq=868,        # PIXMOB frequency
        source_addr=0,          # Our address  
        source_freq=868,        # Our frequency
        payload=pixmob_commands['wake']
    )
    
    # Extended wake sequence (30+ seconds as recommended)
    print("Sending 45-second wake sequence in official format...")
    wake_start = time.time()
    wake_count = 0
    
    while time.time() - wake_start < 45:
        node.send(wake_msg)
        wake_count += 1
        time.sleep(0.2)  # 5 Hz
        
        if wake_count % 25 == 0:
            elapsed = time.time() - wake_start
            print(f"  Wake progress: {elapsed:.0f}s, {wake_count} messages")
    
    print(f"Wake complete: {wake_count} messages sent")
    
    # Send gold command
    print("\nSending GOLD command in official format...")
    gold_msg = create_waveshare_message(
        target_addr=65535,      # Broadcast
        target_freq=868,
        source_addr=0,
        source_freq=868,
        payload=pixmob_commands['gold']
    )
    
    for i in range(20):
        node.send(gold_msg)
        time.sleep(0.3)
        print(f"  Gold message {i+1}/20")
    
    response = input("\nAny PIXMOB response to official format? (y/n): ").lower().strip()
    if response.startswith('y'):
        print("[SUCCESS] Official format works!")
        return True
    
    # Test 2: Direct addressing (try common PIXMOB addresses)
    print("\n=== Test 2: Direct Addressing ===")
    print("Trying specific addresses that PIXMOB might use")
    
    pixmob_addresses = [0, 1, 255, 1000, 8888, 12345]
    
    for addr in pixmob_addresses:
        print(f"\nTesting address {addr}...")
        
        test_msg = create_waveshare_message(
            target_addr=addr,
            target_freq=868,
            source_addr=0,
            source_freq=868,
            payload=pixmob_commands['gold']
        )
        
        for i in range(10):
            node.send(test_msg)
            time.sleep(0.2)
        
        response = input(f"Any response to address {addr}? (y/n): ").lower().strip()
        if response.startswith('y'):
            print(f"[SUCCESS] Address {addr} works!")
            return True
    
    # Test 3: Frequency variants
    print("\n=== Test 3: Frequency Variants ===")
    print("Testing different frequencies in official format")
    
    test_frequencies = [868, 869, 870, 915, 916, 433, 434]
    
    for freq in test_frequencies:
        if freq < 410 or (freq > 493 and freq < 850) or freq > 930:
            continue  # Skip invalid frequencies
            
        print(f"\nTesting frequency {freq} MHz...")
        
        try:
            # Reconfigure node for this frequency
            test_node = sx126x.sx126x(
                serial_num="/dev/ttyS0",
                freq=freq,
                addr=0,
                power=22,
                rssi=False,
                air_speed=2400,
                relay=False
            )
            
            freq_msg = create_waveshare_message(
                target_addr=65535,
                target_freq=freq,
                source_addr=0,
                source_freq=freq,
                payload=pixmob_commands['gold']
            )
            
            for i in range(15):
                test_node.send(freq_msg)
                time.sleep(0.2)
            
            response = input(f"Any response at {freq} MHz? (y/n): ").lower().strip()
            if response.startswith('y'):
                print(f"[SUCCESS] {freq} MHz works!")
                return True
                
        except Exception as e:
            print(f"Error at {freq} MHz: {e}")
    
    return False

def test_raw_vs_formatted():
    """Test both raw PIXMOB data and formatted versions"""
    print("\n=== Test 4: Raw vs Formatted Comparison ===")
    
    node = sx126x.sx126x(
        serial_num="/dev/ttyS0",
        freq=868, addr=0, power=22, rssi=False, air_speed=2400, relay=False
    )
    
    gold_raw = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
    
    print("Testing RAW PIXMOB data (no Waveshare wrapper)...")
    for i in range(10):
        node.send(gold_raw)
        time.sleep(0.2)
    
    response1 = input("Any response to RAW data? (y/n): ").lower().strip()
    
    print("\nTesting FORMATTED PIXMOB data (with Waveshare wrapper)...")
    gold_formatted = create_waveshare_message(65535, 868, 0, 868, gold_raw)
    
    for i in range(10):
        node.send(gold_formatted)
        time.sleep(0.2)
    
    response2 = input("Any response to FORMATTED data? (y/n): ").lower().strip()
    
    if response1.startswith('y') or response2.startswith('y'):
        print("[SUCCESS] Found working format!")
        return True
    
    return False

def main():
    """Main test function"""
    print("PIXMOB Controller: Official Waveshare Format Test")
    print("=================================================")
    print("Using the exact message format from official main.py")
    print("Reference: SX126X_LoRa_HAT_Code/raspberrypi/python/main.py")
    print()
    
    try:
        # Run all tests
        success = (
            test_official_format() or
            test_raw_vs_formatted()
        )
        
        if success:
            print("\n[SUCCESS] Found working method!")
        else:
            print("\n=== FINAL CONCLUSION ===")
            print("Official Waveshare format also unsuccessful.")
            print()
            print("This confirms the fundamental issue:")
            print("- PIXMOB expects OOK/ASK modulation")
            print("- Waveshare HAT only supports LoRa modulation") 
            print("- Protocol incompatibility at RF level")
            print()
            print("Recommended next steps:")
            print("1. Get CC1101 or RFM69 module for OOK")
            print("2. Use RTL-SDR to analyze PIXMOB signals")
            print("3. Verify PIXMOB devices are functional")
            print("4. Consider Software Defined Radio approach")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 