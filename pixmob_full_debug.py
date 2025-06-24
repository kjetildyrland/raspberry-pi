#!/usr/bin/env python3
"""
Comprehensive PIXMOB Debug Script
Tests multiple approaches and identifies issues
"""

import sys
import time
import os
import RPi.GPIO as GPIO
import sx126x

def test_gpio_connection():
    """Test if GPIO pins are working"""
    print("=== GPIO Connection Test ===")
    
    test_pins = [22, 23, 27]  # M0, DIO2, M1 from sx126x class
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for pin in test_pins:
        try:
            GPIO.setup(pin, GPIO.OUT)
            print(f"Testing GPIO {pin}...")
            
            # Blink test
            for i in range(5):
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(pin, GPIO.LOW)
                time.sleep(0.1)
            
            print(f"  GPIO {pin}: OK")
            
        except Exception as e:
            print(f"  GPIO {pin}: ERROR - {e}")
    
    GPIO.cleanup()

def test_frequency_variants():
    """Test both 868MHz and 915MHz variants"""
    print("\n=== Frequency Variant Test ===")
    
    # Your RF captures exist for both frequencies
    frequencies = [868, 915]
    
    for freq in frequencies:
        print(f"\n--- Testing {freq} MHz ---")
        
        try:
            lora = sx126x.sx126x(
                serial_num="/dev/ttyS0",
                freq=freq,
                addr=0,
                power=22,
                rssi=False,
                air_speed=2400,
                relay=False
            )
            
            # Use frequency-specific commands if available
            if freq == 868:
                # 868MHz commands from your RF captures
                gold_cmd = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
                wake_cmd = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])
            else:
                # 915MHz - same commands but different frequency
                gold_cmd = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
                wake_cmd = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])
            
            print(f"Initialized LoRa at {freq} MHz")
            print(f"Actual frequency: {lora.start_freq + lora.offset_freq} MHz")
            
            # Short wake sequence
            print("Sending 10-second wake sequence...")
            for i in range(50):  # 10 seconds at 5Hz
                lora.send(wake_cmd)
                time.sleep(0.2)
            
            # Test gold command
            print("Sending gold command...")
            for i in range(10):
                lora.send(gold_cmd)
                time.sleep(0.2)
            
            response = input(f"Any response at {freq} MHz? (y/n): ").lower().strip()
            if response.startswith('y'):
                print(f"[SUCCESS] {freq} MHz works!")
                return freq
                
        except Exception as e:
            print(f"Error testing {freq} MHz: {e}")
    
    return None

def test_rf_capture_replay():
    """Test with exact RF capture data"""
    print("\n=== RF Capture Replay Test ===")
    
    # Try to read your actual .sub files and extract timing data
    rf_files = [
        "rf/edited_rf_captures/868Mhz/gold_fade_in.sub",
        "rf/edited_rf_captures/915Mhz/gold_fade_in.sub",
        "rf/edited_rf_captures/868Mhz/nothing.sub"
    ]
    
    for rf_file in rf_files:
        if os.path.exists(rf_file):
            print(f"\nTesting with: {rf_file}")
            try:
                with open(rf_file, 'r') as f:
                    content = f.read()
                    
                # Extract frequency from filename
                freq = 868 if "868Mhz" in rf_file else 915
                
                # Initialize LoRa for this frequency
                lora = sx126x.sx126x(
                    serial_num="/dev/ttyS0",
                    freq=freq,
                    addr=0,
                    power=22,
                    rssi=False,
                    air_speed=2400,
                    relay=False
                )
                
                # Extract RAW_Data lines
                raw_lines = [line for line in content.split('\n') if line.startswith('RAW_Data:')]
                if raw_lines:
                    # Convert first RAW_Data line using your PIXMOB.py method
                    raw_data = raw_lines[0].split('RAW_Data: ')[1]
                    
                    # Your conversion method from PIXMOB.py
                    l = [int(int(x)/510) for x in raw_data.split(' ') if x.strip()]
                    s = ''
                    for i in l:
                        if i > 0:
                            for d in range(i):
                                s += '1'
                        else:
                            for d in range(-1*i):
                                s += '0'
                    s = s + '00000000'
                    
                    # Convert to bytes
                    byte_data = []
                    for i in range(0, len(s), 8):
                        if i + 8 <= len(s):
                            byte_val = int(s[i:i+8], 2)
                            byte_data.append(byte_val)
                    
                    if byte_data:
                        converted_data = bytes(byte_data)
                        print(f"Converted data: {converted_data.hex()}")
                        
                        # Send this exact data
                        print("Sending converted RF capture data...")
                        for i in range(15):
                            lora.send(converted_data)
                            time.sleep(0.3)
                        
                        response = input(f"Any response from RF capture replay? (y/n): ").lower().strip()
                        if response.startswith('y'):
                            print(f"[SUCCESS] RF capture replay works!")
                            return True
                
            except Exception as e:
                print(f"Error with {rf_file}: {e}")
        else:
            print(f"File not found: {rf_file}")
    
    return False

def test_radiolib_approach():
    """Test approach similar to your C++ radiolib code"""
    print("\n=== RadioLib-Style Approach ===")
    print("This tries to replicate your radiolib C++ code behavior")
    
    try:
        # Initialize with specific settings from your C++ code
        lora = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,  # Your C++ code uses 868.0F
            addr=0,
            power=22,  # Your C++ code uses 22 dBm max power
            rssi=False,
            air_speed=2400,
            relay=False
        )
        
        print("LoRa initialized in RadioLib style")
        
        # Your C++ code has these exact byte arrays
        nothing_array = bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40])
        gold_array = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
        
        print("Starting continuous transmission like C++ code...")
        
        # Simulate the C++ main loop behavior
        start_time = time.time()
        transmission_count = 0
        
        while time.time() - start_time < 45:  # 45 seconds total
            # Send "nothing" command (like C++ loop)
            lora.send(nothing_array)
            transmission_count += 1
            time.sleep(0.01)  # 10ms like C++ delay
            
            # Every 2 seconds, send a color command (like C++ timer)
            if transmission_count % 200 == 0:  # Every 2 seconds at 10ms intervals
                print(f"  Sending color command at {time.time() - start_time:.0f}s")
                lora.send(gold_array)
                time.sleep(0.01)
            
            # Progress update
            if transmission_count % 500 == 0:
                elapsed = time.time() - start_time
                print(f"  RadioLib style: {elapsed:.0f}s, {transmission_count} transmissions")
        
        print(f"RadioLib-style test complete. Sent {transmission_count} transmissions.")
        
        response = input("Any response from RadioLib-style approach? (y/n): ").lower().strip()
        return response.startswith('y')
        
    except Exception as e:
        print(f"RadioLib approach error: {e}")
        return False

def test_power_and_settings():
    """Test different power levels and settings"""
    print("\n=== Power and Settings Test ===")
    
    # Test different power levels
    power_levels = [10, 13, 17, 22]
    air_speeds = [1200, 2400, 4800]
    
    for power in power_levels:
        for air_speed in air_speeds:
            print(f"\nTesting Power: {power} dBm, Air Speed: {air_speed} bps")
            
            try:
                lora = sx126x.sx126x(
                    serial_num="/dev/ttyS0",
                    freq=868,
                    addr=0,
                    power=power,
                    rssi=False,
                    air_speed=air_speed,
                    relay=False
                )
                
                # Quick test
                gold_cmd = bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40])
                
                for i in range(5):
                    lora.send(gold_cmd)
                    time.sleep(0.2)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error: {e}")
                continue
            
            response = input(f"Any response with {power}dBm/{air_speed}bps? (y/n): ").lower().strip()
            if response.startswith('y'):
                print(f"[SUCCESS] {power}dBm/{air_speed}bps works!")
                return (power, air_speed)
    
    return None

def diagnose_issues():
    """Comprehensive issue diagnosis"""
    print("\n=== Issue Diagnosis ===")
    
    issues = []
    
    # Check 1: PIXMOB bracelet status
    print("1. PIXMOB Bracelet Check:")
    print("   - Is the bracelet powered on?")
    print("   - Does it light up when shaken/tapped?")
    print("   - Is it within 2 meters of the transmitter?")
    bracelet_ok = input("   Bracelet seems OK? (y/n): ").lower().strip()
    if not bracelet_ok.startswith('y'):
        issues.append("PIXMOB bracelet might be off/broken/out of range")
    
    # Check 2: Frequency match
    print("\n2. Frequency Check:")
    print("   - You have both 868MHz and 915MHz RF captures")
    print("   - Different regions use different frequencies")
    print("   - US/Canada: 915MHz, Europe: 868MHz")
    region = input("   What region are you in? (US/Europe/Other): ").strip()
    if region.upper() == "US":
        issues.append("Try 915MHz instead of 868MHz")
    elif region.upper() == "EUROPE":
        issues.append("868MHz should be correct for Europe")
    else:
        issues.append("Check local LoRa frequency regulations")
    
    # Check 3: Protocol compatibility
    print("\n3. Protocol Check:")
    print("   - PIXMOB typically uses OOK/ASK modulation")
    print("   - Your LoRa module uses LoRa modulation") 
    print("   - These are fundamentally different")
    issues.append("Protocol mismatch: PIXMOB (OOK/ASK) vs LoRa modulation")
    
    # Check 4: Hardware setup
    print("\n4. Hardware Check:")
    print("   - Your LoRa HAT uses UART, not direct GPIO")
    print("   - Direct GPIO method requires DIO2 pin access")
    print("   - Your HAT might not expose DIO2")
    issues.append("Hardware limitation: UART HAT vs direct GPIO requirement")
    
    return issues

def main():
    """Main debug function"""
    print("PIXMOB Comprehensive Debug")
    print("==========================")
    print("This will test multiple approaches to identify the issue")
    print()
    
    # Test 1: Basic GPIO
    test_gpio_connection()
    
    # Test 2: Frequency variants
    working_freq = test_frequency_variants()
    if working_freq:
        print(f"\n[SUCCESS] Found working frequency: {working_freq} MHz")
        return
    
    # Test 3: RF capture replay
    if test_rf_capture_replay():
        print("\n[SUCCESS] RF capture replay worked!")
        return
    
    # Test 4: RadioLib approach
    if test_radiolib_approach():
        print("\n[SUCCESS] RadioLib approach worked!")
        return
    
    # Test 5: Power/settings
    working_settings = test_power_and_settings()
    if working_settings:
        print(f"\n[SUCCESS] Found working settings: {working_settings}")
        return
    
    # If nothing worked, diagnose
    print("\n[NO SUCCESS] No method worked. Diagnosing issues...")
    issues = diagnose_issues()
    
    print("\n=== DIAGNOSIS RESULTS ===")
    print("Likely issues found:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    print("\n=== RECOMMENDATIONS ===")
    print("1. Try a different PIXMOB bracelet to rule out hardware failure")
    print("2. Test at different frequencies (868MHz vs 915MHz)")
    print("3. Consider getting an OOK/ASK transmitter instead of LoRa")
    print("4. Try capturing new RF signals with your specific bracelet")
    print("5. Check if your LoRa module can be put into OOK/ASK mode")

if __name__ == "__main__":
    main() 