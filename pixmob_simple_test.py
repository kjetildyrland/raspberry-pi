#!/usr/bin/env python3
"""
Simple PIXMOB Test
Quick test to see if PIXMOB bracelets respond
"""

import sys
import time
import sx126x

def simple_pixmob_test():
    """Simple test to wake up and control PIXMOB bracelets"""
    print("=== Simple PIXMOB Test ===")
    
    try:
        # Initialize LoRa for PIXMOB
        print("Initializing LoRa for PIXMOB control...")
        lora = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,           # 868 MHz
            addr=0,
            power=22,           # Max power
            rssi=True,
            air_speed=2400,
            relay=False
        )
        print("[SUCCESS] LoRa initialized")
        
        # PIXMOB command data (from your converted .sub files)
        pixmob_commands = {
            'wake_up': bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40]),  # nothing/wake
            'gold': bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]),     # gold_fade_in
            'white': bytes([0xaa, 0xaa, 0x56, 0xa1, 0x2d, 0x6d, 0x6d, 0x52, 0x51, 0x61, 0x0b]),          # white_fastfade
            'blue': bytes([0xaa, 0xaa, 0x61, 0x21, 0x0c, 0xa1, 0x2d, 0x62, 0x62, 0x61, 0x0d, 0x80]),     # rand_blue_fade
            'red': bytes([0xaa, 0xaa, 0x69, 0x21, 0x21, 0x2d, 0x61, 0x22, 0x62, 0x61, 0x19, 0x40]),      # rand_red_fade
        }
        
        print("\n=== Testing PIXMOB Commands ===")
        
        # Test sequence
        test_sequence = [
            ('wake_up', 'Wake Up / Turn Off'),
            ('gold', 'Gold Fade'),
            ('white', 'White Flash'),
            ('blue', 'Blue Fade'),
            ('red', 'Red Fade'),
            ('wake_up', 'Turn Off')
        ]
        
        for cmd_name, description in test_sequence:
            print(f"\n--- Testing: {description} ---")
            command_data = pixmob_commands[cmd_name]
            
            # Method 1: Send as LoRa packet
            print("Method 1: LoRa packet format")
            target_addr = 65535  # Broadcast
            packet_data = (bytes([target_addr >> 8]) + 
                          bytes([target_addr & 0xff]) + 
                          bytes([lora.offset_freq]) + 
                          bytes([lora.addr >> 8]) + 
                          bytes([lora.addr & 0xff]) + 
                          bytes([lora.offset_freq]) + 
                          command_data)
            
            for i in range(3):  # Repeat 3 times
                lora.send(packet_data)
                print(f"  [SENT] LoRa packet {i+1}/3")
                time.sleep(0.3)
            
            time.sleep(1)
            
            # Method 2: Send raw data
            print("Method 2: Raw data format")
            for i in range(3):  # Repeat 3 times
                lora.send(command_data)
                print(f"  [SENT] Raw data {i+1}/3")
                time.sleep(0.3)
            
            print(f"Command '{description}' sent! Watch for PIXMOB response...")
            time.sleep(3)  # Wait to observe effect
        
        print("\n=== Test Complete ===")
        print("If PIXMOB bracelets responded, you should have seen:")
        print("- Gold fading light")
        print("- White flashing")
        print("- Blue fading light")
        print("- Red fading light")
        print("- Lights turning off")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PIXMOB bracelet is nearby (within 10 meters)")
        print("2. Make sure bracelet is awake/active")
        print("3. Try shaking the bracelet to activate it")
        print("4. Verify 868MHz frequency matches your region")
        return False

def quick_color_test():
    """Quick test of just one color"""
    print("\n=== Quick Gold Test ===")
    
    try:
        lora = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,
            addr=0,
            power=22,
            rssi=False,  # Disable RSSI for cleaner output
            air_speed=2400,
            relay=False
        )
        
        # Gold fade command
        gold_cmd = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
        
        print("Sending GOLD FADE command...")
        print(f"Command: {gold_cmd.hex()}")
        
        # Send multiple times with different methods
        for method in ["LoRa packet", "Raw data"]:
            print(f"\nTrying {method} method:")
            
            if method == "LoRa packet":
                # LoRa packet format
                target_addr = 65535
                data = (bytes([target_addr >> 8]) + 
                       bytes([target_addr & 0xff]) + 
                       bytes([lora.offset_freq]) + 
                       bytes([lora.addr >> 8]) + 
                       bytes([lora.addr & 0xff]) + 
                       bytes([lora.offset_freq]) + 
                       gold_cmd)
            else:
                # Raw data
                data = gold_cmd
            
            for i in range(5):
                lora.send(data)
                print(f"  Sent transmission {i+1}/5")
                time.sleep(0.2)
            
            time.sleep(2)
        
        print("\nGold command sent! Check if PIXMOB bracelet shows gold light.")
        
    except Exception as e:
        print(f"Quick test failed: {e}")

if __name__ == "__main__":
    print("PIXMOB Simple Test")
    print("==================")
    print("This will test basic PIXMOB control.")
    print("Make sure your PIXMOB bracelet is nearby and active!")
    print()
    
    choice = input("Choose test:\n1. Full test sequence\n2. Quick gold test\nEnter 1 or 2: ").strip()
    
    if choice == "1":
        simple_pixmob_test()
    elif choice == "2":
        quick_color_test()
    else:
        print("Invalid choice, running quick test...")
        quick_color_test() 