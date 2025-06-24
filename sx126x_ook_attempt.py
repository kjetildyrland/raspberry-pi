#!/usr/bin/env python3
"""
Modified SX126X driver attempting OOK mode through UART commands
This tries to find undocumented ways to enable OOK on Waveshare HAT
"""

import RPi.GPIO as GPIO
import serial
import time
import sx126x

class SX126X_OOK_Attempt(sx126x.sx126x):
    """
    Modified sx126x driver that attempts OOK mode
    """
    
    def __init__(self, *args, **kwargs):
        print("Initializing SX126X with OOK attempt...")
        super().__init__(*args, **kwargs)
        self.ook_mode = False
    
    def try_ook_mode_commands(self):
        """Try various undocumented commands to enable OOK"""
        print("Attempting to enable OOK mode through register commands...")
        
        # Set configuration mode
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)
        
        # Try different register configurations that might enable OOK
        ook_attempts = [
            # Attempt 1: Modify register 9 (communication control)
            # Standard: 0x43, Try: 0x47 (different modulation?)
            [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x12, 0x47, 0x00, 0x00],
            
            # Attempt 2: Modify register 6 (air speed + modulation?)
            # Try setting different bits that might control modulation
            [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x72, 0x00, 0x12, 0x43, 0x00, 0x00],
            
            # Attempt 3: Modify register 7 (power + possibly modulation control)
            # Try different values that might enable OOK
            [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x10, 0x12, 0x43, 0x00, 0x00],
            
            # Attempt 4: Try register 8 frequency with different encoding
            [0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x52, 0x43, 0x00, 0x00],
        ]
        
        for i, attempt_reg in enumerate(ook_attempts):
            print(f"\nTrying OOK configuration {i+1}/4...")
            
            # Send the modified configuration
            self.ser.flushInput()
            self.ser.write(bytes(attempt_reg))
            time.sleep(0.2)
            
            # Check response
            if self.ser.inWaiting() > 0:
                time.sleep(0.1)
                r_buff = self.ser.read(self.ser.inWaiting())
                if r_buff[0] == 0xC1:
                    print(f"  Configuration {i+1} accepted")
                    
                    # Test transmission with this config
                    GPIO.output(self.M0, GPIO.LOW)
                    GPIO.output(self.M1, GPIO.LOW)
                    time.sleep(0.1)
                    
                    # Send test data
                    test_data = bytes([0xaa, 0xaa, 0x55])
                    self.ser.write(test_data)
                    time.sleep(0.1)
                    
                    # Ask user for feedback
                    response = input(f"  Any different behavior with config {i+1}? (y/n): ").lower().strip()
                    if response.startswith('y'):
                        print(f"  [POTENTIAL] Config {i+1} shows different behavior!")
                        self.cfg_reg = attempt_reg.copy()  # Store working config
                        return True
                else:
                    print(f"  Configuration {i+1} rejected")
            else:
                print(f"  Configuration {i+1} no response")
        
        return False
    
    def try_special_commands(self):
        """Try special undocumented UART commands"""
        print("\nTrying special UART commands...")
        
        # Set to configuration mode
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)
        
        special_commands = [
            # Try to read all registers (extended)
            [0xC1, 0x00, 0x10],  # Read more registers
            [0xC1, 0x00, 0x20],  # Read even more
            
            # Try different command headers
            [0xC3, 0x00, 0x09],  # Different header
            [0xC4, 0x00, 0x09],  # Another header
            
            # Try direct modulation commands
            [0xC5, 0x01],        # Possible modulation command
            [0xC6, 0x00],        # Another possibility
        ]
        
        for i, cmd in enumerate(special_commands):
            print(f"  Trying special command {i+1}: {[hex(x) for x in cmd]}")
            
            self.ser.flushInput()
            self.ser.write(bytes(cmd))
            time.sleep(0.2)
            
            if self.ser.inWaiting() > 0:
                response = self.ser.read(self.ser.inWaiting())
                print(f"    Response: {[hex(x) for x in response]}")
                
                # Check if response is different from normal
                if len(response) > 12 or response[0] != 0xC1:
                    print(f"    [INTERESTING] Unusual response!")
            else:
                print("    No response")
    
    def send_ook_pattern(self, data, bit_duration_ms=1):
        """
        Attempt to send OOK-like pattern by rapidly switching between
        data transmission and silence
        """
        print(f"Sending OOK-like pattern: {len(data)} bytes")
        
        # Ensure we're in transmission mode
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.LOW)
        time.sleep(0.1)
        
        for byte_val in data:
            for bit_pos in range(7, -1, -1):  # MSB first
                bit = (byte_val >> bit_pos) & 1
                
                if bit:
                    # Send a short burst (represents '1')
                    self.ser.write(bytes([0xFF]))  # High signal
                else:
                    # Send silence or minimal signal (represents '0')
                    # Try different approaches for '0'
                    pass  # No transmission
                
                time.sleep(bit_duration_ms / 1000)
        
        # Final cleanup
        time.sleep(0.01)
    
    def test_ook_approaches(self):
        """Test all OOK approaches"""
        print("=== SX126X OOK Mode Attempts ===")
        print("Trying to enable OOK on Waveshare HAT...")
        
        # Attempt 1: Try undocumented register settings
        print("\n1. Trying undocumented register configurations...")
        if self.try_ook_mode_commands():
            print("[SUCCESS] Found working OOK configuration!")
            return True
        
        # Attempt 2: Try special commands
        print("\n2. Trying special UART commands...")
        self.try_special_commands()
        
        # Attempt 3: Manual OOK-like transmission
        print("\n3. Trying manual OOK-like pattern...")
        pixmob_data = [0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]
        
        for i in range(5):
            print(f"  Manual OOK attempt {i+1}/5")
            self.send_ook_pattern(pixmob_data, 2)  # 2ms bit duration
            time.sleep(0.5)
        
        response = input("\nAny PIXMOB response to manual OOK attempts? (y/n): ").lower().strip()
        if response.startswith('y'):
            print("[SUCCESS] Manual OOK pattern works!")
            return True
        
        return False

def main():
    """Main test function"""
    print("SX126X OOK Mode Attempt")
    print("=======================")
    print("Trying to enable OOK on Waveshare SX1262 HAT")
    print()
    
    try:
        # Initialize with OOK attempt
        lora_ook = SX126X_OOK_Attempt(
            serial_num="/dev/ttyS0",
            freq=868,
            addr=0,
            power=22,
            rssi=False,
            air_speed=2400
        )
        
        print("Standard initialization complete")
        
        # Test OOK approaches
        success = lora_ook.test_ook_approaches()
        
        if not success:
            print("\n=== CONCLUSION ===")
            print("Could not enable OOK mode on Waveshare HAT")
            print("\nReasons:")
            print("1. Firmware is locked to LoRa mode only")
            print("2. No documented OOK support")
            print("3. SPI access needed for direct chip control")
            print("\nRecommendations:")
            print("- Use CC1101 module for true OOK support")
            print("- Get RFM69 module (supports both LoRa and OOK)")
            print("- Consider Software Defined Radio approach")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 