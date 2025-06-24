#!/usr/bin/env python3
"""
PIXMOB Direct GPIO Transmission
Bypasses LoRa protocol and sends direct OOK/ASK modulation
Based on the radiolib C++ approach
"""

import time
import sys
import RPi.GPIO as GPIO

class DirectPIXMOBTransmitter:
    def __init__(self, dio2_pin=23, bit_duration=500):
        """
        Initialize direct GPIO transmitter
        dio2_pin: GPIO pin connected to LoRa module's DIO2 (for direct modulation)
        bit_duration: Duration of each bit in microseconds (500µs = 2000 bits/sec)
        """
        self.dio2_pin = dio2_pin
        self.bit_duration = bit_duration  # microseconds
        
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dio2_pin, GPIO.OUT)
        GPIO.output(self.dio2_pin, GPIO.LOW)
        
        print(f"Direct GPIO transmitter initialized on pin {dio2_pin}")
        print(f"Bit duration: {bit_duration}µs")
    
    def microsecond_delay(self, microseconds):
        """Precise microsecond delay"""
        start = time.perf_counter()
        while (time.perf_counter() - start) * 1000000 < microseconds:
            pass
    
    def send_byte_array(self, byte_array):
        """Send byte array using OOK/ASK modulation"""
        print(f"Sending byte array: {byte_array.hex()}")
        
        # Send each byte
        for byte_val in byte_array:
            # Send each bit of the byte (MSB first)
            for bit_pos in range(8):
                bit_value = (byte_val >> (7 - bit_pos)) & 1
                
                # Set GPIO pin according to bit value
                GPIO.output(self.dio2_pin, GPIO.HIGH if bit_value else GPIO.LOW)
                
                # Hold for bit duration
                self.microsecond_delay(self.bit_duration)
        
        # End with low signal and additional zeros
        GPIO.output(self.dio2_pin, GPIO.LOW)
        for _ in range(8):  # 8 extra zero bits
            self.microsecond_delay(self.bit_duration)
        
        print("Byte array transmission complete")
    
    def send_pixmob_command(self, command_name, byte_array, repeat_count=5):
        """Send PIXMOB command with repetition"""
        print(f"\n=== Sending PIXMOB Command: {command_name} ===")
        print(f"Data: {byte_array.hex()}")
        print(f"Repeating {repeat_count} times...")
        
        for i in range(repeat_count):
            print(f"  Transmission {i+1}/{repeat_count}")
            self.send_byte_array(byte_array)
            time.sleep(0.1)  # 100ms between transmissions
        
        print(f"Command '{command_name}' transmission complete!")
    
    def wake_up_sequence(self, duration_seconds=30):
        """Send continuous wake-up sequence"""
        print(f"\n=== PIXMOB Wake-Up Sequence ===")
        print(f"Sending wake-up signal for {duration_seconds} seconds...")
        
        # "Nothing" command for wake-up
        wake_cmd = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])
        
        start_time = time.time()
        transmissions = 0
        
        while time.time() - start_time < duration_seconds:
            self.send_byte_array(wake_cmd)
            transmissions += 1
            
            # Progress update every 5 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 5 == 0 and elapsed % 5 < 0.2:
                remaining = duration_seconds - elapsed
                print(f"  Wake progress: {elapsed:.0f}s/{duration_seconds}s - {transmissions} transmissions")
            
            time.sleep(0.2)  # 200ms between wake transmissions
        
        print(f"Wake-up sequence complete! Sent {transmissions} wake signals")
    
    def cleanup(self):
        """Clean up GPIO"""
        GPIO.output(self.dio2_pin, GPIO.LOW)
        GPIO.cleanup()

def test_direct_pixmob():
    """Test direct PIXMOB transmission"""
    print("=== Direct GPIO PIXMOB Test ===")
    print("This method bypasses LoRa protocol and uses direct OOK/ASK modulation")
    print("Similar to the C++ radiolib approach")
    
    # Initialize transmitter
    transmitter = DirectPIXMOBTransmitter(dio2_pin=23, bit_duration=500)
    
    try:
        # PIXMOB commands from your conversions
        pixmob_commands = {
            'wake_up': bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40]),
            'gold_fade_in': bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]),
            'white_fastfade': bytes([0xaa, 0xaa, 0x56, 0xa1, 0x2d, 0x6d, 0x6d, 0x52, 0x51, 0x61, 0x0b]),
            'blue_fade': bytes([0xaa, 0xaa, 0x61, 0x21, 0x0c, 0xa1, 0x2d, 0x62, 0x62, 0x61, 0x0d, 0x80]),
            'red_fade': bytes([0xaa, 0xaa, 0x69, 0x21, 0x21, 0x2d, 0x61, 0x22, 0x62, 0x61, 0x19, 0x40]),
        }
        
        # Phase 1: Wake-up sequence
        transmitter.wake_up_sequence(30)
        
        # Phase 2: Test gold command
        print("\n=== Testing Gold Command ===")
        transmitter.send_pixmob_command('gold_fade_in', pixmob_commands['gold_fade_in'], repeat_count=10)
        
        response = input("\nDid you see GOLD light? (y/n): ").lower().strip()
        
        if response.startswith('y'):
            print("\n[SUCCESS] Direct GPIO method is working!")
            
            # Test more colors
            for cmd_name in ['white_fastfade', 'blue_fade', 'red_fade']:
                print(f"\n--- Testing {cmd_name} ---")
                transmitter.send_pixmob_command(cmd_name, pixmob_commands[cmd_name])
                time.sleep(3)
            
            # Turn off
            print("\n--- Turning off ---")
            transmitter.send_pixmob_command('turn_off', pixmob_commands['wake_up'])
            
        else:
            print("\n[ERROR] No response with direct GPIO method either")
            print("Possible issues:")
            print("- DIO2 pin (GPIO 23) might not be connected correctly")
            print("- Bit timing might need adjustment")
            print("- PIXMOB bracelet might use different frequency or protocol")
            print("- Bracelet might be out of range or not working")
            
            # Try different bit durations
            print("\n=== Trying Different Bit Durations ===")
            bit_durations = [250, 500, 1000, 2000]  # microseconds
            
            for duration in bit_durations:
                print(f"\nTrying bit duration: {duration}µs")
                transmitter.bit_duration = duration
                transmitter.send_pixmob_command('gold_test', pixmob_commands['gold_fade_in'], repeat_count=5)
                
                response = input(f"Any response with {duration}us timing? (y/n): ").lower().strip()
                if response.startswith('y'):
                    print(f"[SUCCESS] Bit duration {duration}us works!")
                    break
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transmitter.cleanup()

def continuous_direct_wake():
    """Continuous wake mode using direct GPIO"""
    print("=== Continuous Direct GPIO Wake ===")
    print("This will continuously send wake signals using direct GPIO")
    print("Press Ctrl+C to stop")
    
    transmitter = DirectPIXMOBTransmitter(dio2_pin=23, bit_duration=500)
    wake_cmd = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])
    
    try:
        transmissions = 0
        start_time = time.time()
        
        while True:
            transmitter.send_byte_array(wake_cmd)
            transmissions += 1
            
            if transmissions % 10 == 0:
                elapsed = time.time() - start_time
                rate = transmissions / elapsed
                print(f"Direct GPIO wake: {transmissions} transmissions in {elapsed:.0f}s ({rate:.1f}/s)")
            
            time.sleep(0.5)  # 500ms between transmissions
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\nStopped. Sent {transmissions} direct GPIO wake signals in {elapsed:.0f}s")
    finally:
        transmitter.cleanup()

if __name__ == "__main__":
    print("PIXMOB Direct GPIO Transmitter")
    print("==============================")
    print("This uses direct GPIO modulation instead of LoRa protocol")
    print("Based on the radiolib C++ approach")
    print()
    print("WARNING: This requires DIO2 pin connected to GPIO 23")
    print()
    
    choice = input("Choose mode:\n1. Full direct GPIO test\n2. Continuous direct wake\nEnter 1 or 2: ").strip()
    
    if choice == "2":
        continuous_direct_wake()
    else:
        test_direct_pixmob() 