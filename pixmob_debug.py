#!/usr/bin/env python3
"""
PIXMOB Debug Script
Properly wakes up PIXMOB bracelets and debugs transmission
"""

import sys
import time
import sx126x

def pixmob_wake_and_test():
    """Proper PIXMOB wake-up sequence followed by color test"""
    print("=== PIXMOB Debug & Wake-Up Test ===")
    
    try:
        # Initialize LoRa
        print("Initializing LoRa for PIXMOB...")
        lora = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,
            addr=0,
            power=22,           # Maximum power
            rssi=False,         # Disable RSSI for cleaner output
            air_speed=2400,
            relay=False
        )
        print(f"[SUCCESS] LoRa initialized at {lora.start_freq + lora.offset_freq} MHz")
        
        # PIXMOB commands
        wake_up_cmd = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])  # nothing
        gold_cmd = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])     # gold_fade_in
        
        print(f"Wake-up command: {wake_up_cmd.hex()}")
        print(f"Gold command: {gold_cmd.hex()}")
        
        # === PHASE 1: Extended Wake-Up Sequence (30 seconds) ===
        print("\n=== PHASE 1: PIXMOB Wake-Up Sequence ===")
        print("Sending continuous wake-up signal for 30 seconds...")
        print("This activates sleeping PIXMOB bracelets")
        print("Watch for any brief flashes on the bracelet during this time")
        
        wake_duration = 30  # seconds
        transmissions_sent = 0
        start_time = time.time()
        
        while time.time() - start_time < wake_duration:
            # Send wake-up command multiple ways
            
            # Method 1: Raw PIXMOB data
            lora.send(wake_up_cmd)
            transmissions_sent += 1
            
            time.sleep(0.1)  # 100ms between transmissions
            
            # Method 2: LoRa packet format every 10th transmission
            if transmissions_sent % 10 == 0:
                target_addr = 65535  # Broadcast
                packet_data = (bytes([target_addr >> 8]) + 
                              bytes([target_addr & 0xff]) + 
                              bytes([lora.offset_freq]) + 
                              bytes([lora.addr >> 8]) + 
                              bytes([lora.addr & 0xff]) + 
                              bytes([lora.offset_freq]) + 
                              wake_up_cmd)
                lora.send(packet_data)
                transmissions_sent += 1
            
            # Progress indicator
            elapsed = time.time() - start_time
            if int(elapsed) % 5 == 0 and elapsed % 5 < 0.2:  # Every 5 seconds
                remaining = wake_duration - elapsed
                print(f"  Wake-up progress: {elapsed:.0f}s / {wake_duration}s (remaining: {remaining:.0f}s) - {transmissions_sent} transmissions sent")
        
        print(f"\n[COMPLETE] Wake-up phase finished!")
        print(f"Total wake-up transmissions sent: {transmissions_sent}")
        print("PIXMOB bracelets should now be active and listening...")
        
        # === PHASE 2: Color Command Test ===
        print("\n=== PHASE 2: Color Command Test ===")
        print("Now sending GOLD color command...")
        
        # Send gold command with high repetition
        for i in range(20):  # Send 20 times
            lora.send(gold_cmd)
            print(f"  [SENT] Gold command {i+1}/20")
            time.sleep(0.2)  # 200ms between commands
        
        print("\n[COMPLETE] Gold command sequence finished!")
        print("Check if PIXMOB bracelet shows GOLD light now!")
        
        # === PHASE 3: Additional Color Tests ===
        user_input = input("\nDid you see GOLD light? (y/n): ").lower().strip()
        
        if user_input.startswith('y'):
            print("\n🎉 SUCCESS! PIXMOB bracelet is responding!")
            print("\n=== PHASE 3: Testing More Colors ===")
            
            more_commands = {
                'white': bytes([0xaa, 0xaa, 0x56, 0xa1, 0x2d, 0x6d, 0x6d, 0x52, 0x51, 0x61, 0x0b]),
                'blue': bytes([0xaa, 0xaa, 0x61, 0x21, 0x0c, 0xa1, 0x2d, 0x62, 0x62, 0x61, 0x0d, 0x80]),
                'red': bytes([0xaa, 0xaa, 0x69, 0x21, 0x21, 0x2d, 0x61, 0x22, 0x62, 0x61, 0x19, 0x40]),
            }
            
            for color_name, color_cmd in more_commands.items():
                print(f"\n--- Testing {color_name.upper()} ---")
                for i in range(15):
                    lora.send(color_cmd)
                    time.sleep(0.2)
                print(f"Sent {color_name} command - check bracelet!")
                time.sleep(2)
            
            # Turn off
            print("\n--- Turning OFF ---")
            for i in range(10):
                lora.send(wake_up_cmd)  # "nothing" command turns off
                time.sleep(0.2)
            
        else:
            print("\n❌ No response detected. Let's try debugging...")
            debug_transmission_issues(lora, wake_up_cmd, gold_cmd)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_transmission_issues(lora, wake_cmd, gold_cmd):
    """Debug transmission issues"""
    print("\n=== TRANSMISSION DEBUG ===")
    
    # Test 1: Verify LoRa module is working
    print("1. Testing LoRa module basic functionality...")
    test_msg = "LoRa test message"
    try:
        lora.send(test_msg.encode())
        print("   ✓ LoRa module can send data")
    except Exception as e:
        print(f"   ✗ LoRa module error: {e}")
        return
    
    # Test 2: Try different transmission patterns
    print("\n2. Trying different transmission patterns...")
    
    patterns = [
        ("Rapid burst", 0.05, 50),      # 50ms intervals, 50 times
        ("Medium pace", 0.2, 25),       # 200ms intervals, 25 times  
        ("Slow pace", 0.5, 10),         # 500ms intervals, 10 times
        ("Very slow", 1.0, 5),          # 1s intervals, 5 times
    ]
    
    for pattern_name, interval, count in patterns:
        print(f"\nTrying {pattern_name} pattern...")
        for i in range(count):
            lora.send(wake_cmd)
            time.sleep(interval)
        print(f"   Sent {count} wake commands at {interval}s intervals")
        
        # Now try gold
        print(f"   Following with gold command...")
        for i in range(10):
            lora.send(gold_cmd)
            time.sleep(interval)
        
        response = input("   Any response? (y/n): ").lower().strip()
        if response.startswith('y'):
            print(f"   ✓ {pattern_name} pattern worked!")
            return
    
    # Test 3: Try longer wake-up period
    print("\n3. Trying extended 60-second wake-up...")
    print("This might take a while, but some PIXMOB devices need longer activation...")
    
    start_time = time.time()
    transmissions = 0
    
    while time.time() - start_time < 60:  # 60 seconds
        lora.send(wake_cmd)
        transmissions += 1
        time.sleep(0.1)
        
        if transmissions % 100 == 0:
            elapsed = time.time() - start_time
            print(f"   Extended wake: {elapsed:.0f}s, {transmissions} transmissions")
    
    print("   Extended wake complete, trying gold...")
    for i in range(30):
        lora.send(gold_cmd)
        time.sleep(0.2)
    
    response = input("   Any response after extended wake? (y/n): ").lower().strip()
    if response.startswith('y'):
        print("   ✓ Extended wake-up worked!")
    else:
        print("   ❌ Still no response")
        print("\n   Possible issues:")
        print("   - PIXMOB bracelet might be using different frequency")
        print("   - Protocol might need OOK/ASK modulation instead of LoRa")
        print("   - Timing or data format might be incorrect")
        print("   - Bracelet might be damaged or out of range")

def continuous_wake_mode():
    """Continuous wake-up mode for testing"""
    print("=== Continuous Wake Mode ===")
    print("This will continuously send wake-up signals.")
    print("Press Ctrl+C to stop")
    
    try:
        lora = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,
            addr=0,
            power=22,
            rssi=False,
            air_speed=2400,
            relay=False
        )
        
        wake_cmd = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])
        
        transmissions = 0
        start_time = time.time()
        
        while True:
            lora.send(wake_cmd)
            transmissions += 1
            
            if transmissions % 50 == 0:
                elapsed = time.time() - start_time
                rate = transmissions / elapsed
                print(f"Continuous wake: {transmissions} transmissions in {elapsed:.0f}s ({rate:.1f}/s)")
            
            time.sleep(0.1)  # 10 transmissions per second
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\nStopped. Sent {transmissions} wake signals in {elapsed:.0f}s")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("PIXMOB Debug & Test Script")
    print("==========================")
    print("This script will:")
    print("1. Send wake-up signals for 30 seconds")
    print("2. Test color commands")
    print("3. Debug any issues")
    print()
    print("Make sure your PIXMOB bracelet is nearby!")
    print()
    
    choice = input("Choose mode:\n1. Full debug test\n2. Continuous wake mode\nEnter 1 or 2: ").strip()
    
    if choice == "2":
        continuous_wake_mode()
    else:
        pixmob_wake_and_test() 