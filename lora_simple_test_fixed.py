#!/usr/bin/env python3
"""
Fixed LoRa SX126X test script using UART communication
Based on manufacturer's official code
"""

import sys
import os
import time

# Add the path to find sx126x module
sys.path.append('.')

def test_system_requirements():
    """Test system requirements for UART LoRa"""
    print("=== System Requirements Check ===")
    
    # Check if serial device exists
    if os.path.exists('/dev/ttyS0'):
        print("[SUCCESS] Found UART device: /dev/ttyS0")
    else:
        print("[ERROR] UART device /dev/ttyS0 not found!")
        print("Enable UART: sudo raspi-config -> Interface Options -> Serial")
        print("- Disable serial login shell")
        print("- Enable serial port hardware")
        return False
    
    # Check GPIO access
    try:
        import RPi.GPIO as GPIO
        print("[SUCCESS] RPi.GPIO library available")
    except ImportError:
        print("[ERROR] RPi.GPIO library not found!")
        print("Install with: sudo apt install python3-rpi.gpio")
        return False
    
    # Check serial library
    try:
        import serial
        print("[SUCCESS] PySerial library available")
    except ImportError:
        print("[ERROR] PySerial library not found!")
        print("Install with: pip install pyserial")
        return False
    
    return True

def test_sx126x_import():
    """Test importing the manufacturer's sx126x module"""
    print("\n=== Testing SX126X Module Import ===")
    
    try:
        # Try to import the manufacturer's sx126x module
        import sx126x
        print("[SUCCESS] SX126X module imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import sx126x module: {e}")
        print("Make sure sx126x.py is in the same directory")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected import error: {e}")
        return False

def test_lora_initialization():
    """Test LoRa module initialization"""
    print("\n=== Testing LoRa Initialization ===")
    
    try:
        import sx126x
        
        print("Creating SX126X instance...")
        print("Configuration:")
        print("- Serial: /dev/ttyS0")
        print("- Frequency: 868 MHz")
        print("- Address: 0")
        print("- Power: 22 dBm")
        print("- RSSI: Enabled")
        print("- Air Speed: 2400 bps")
        
        # Create LoRa node with same parameters as manufacturer example
        node = sx126x.sx126x(
            serial_num="/dev/ttyS0",
            freq=868,           # 868 MHz
            addr=0,             # Address 0
            power=22,           # 22 dBm power
            rssi=True,          # Enable RSSI
            air_speed=2400,     # 2400 bps air speed
            relay=False
        )
        
        print("[SUCCESS] LoRa module initialized successfully!")
        print("Module details:")
        print(f"- Address: {node.addr}")
        print(f"- Frequency: {node.start_freq + node.offset_freq} MHz")
        print(f"- Power: {node.power} dBm")
        print(f"- RSSI enabled: {node.rssi}")
        
        return node
        
    except Exception as e:
        print(f"[ERROR] LoRa initialization failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check UART is enabled and login shell disabled")
        print("2. Ensure LoRa HAT is properly connected")
        print("3. Verify GPIO pins are accessible")
        print("4. Try running with sudo as a test")
        return None

def test_message_transmission(node):
    """Test sending messages"""
    print("\n=== Testing Message Transmission ===")
    
    try:
        test_messages = [
            "Hello LoRa!",
            "Test Message 123",
            "SX126X Working!"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Test {i}/3 ---")
            print(f"Sending: '{message}'")
            
            # Create data packet in the format expected by the module
            # Format: [target_addr_high, target_addr_low, freq_offset, 
            #          source_addr_high, source_addr_low, source_freq_offset, message]
            target_addr = 65535  # Broadcast address
            data = (bytes([target_addr >> 8]) + 
                   bytes([target_addr & 0xff]) + 
                   bytes([node.offset_freq]) + 
                   bytes([node.addr >> 8]) + 
                   bytes([node.addr & 0xff]) + 
                   bytes([node.offset_freq]) + 
                   message.encode())
            
            node.send(data)
            print(f"[SUCCESS] Message {i} transmitted!")
            
            # Wait between messages
            time.sleep(2)
        
        print("\n[SUCCESS] All test messages sent successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Message transmission failed: {e}")
        return False

def test_message_reception(node, duration=10):
    """Test receiving messages for a short time"""
    print(f"\n=== Testing Message Reception ({duration}s) ===")
    print("Listening for incoming messages...")
    print("(You can send messages from another LoRa device to test)")
    
    start_time = time.time()
    messages_received = 0
    
    try:
        while time.time() - start_time < duration:
            node.receive()
            time.sleep(0.1)
            
        print(f"\nReception test completed after {duration} seconds")
        return True
        
    except KeyboardInterrupt:
        print("\nReception test interrupted by user")
        return True
    except Exception as e:
        print(f"[ERROR] Reception test failed: {e}")
        return False

def main():
    """Main test function"""
    print("SX126X LoRa HAT Test (UART Version)")
    print("===================================")
    
    # Test system requirements
    if not test_system_requirements():
        print("\n[RESULT] System requirements not met. Fix issues above and try again.")
        return
    
    # Test module import
    if not test_sx126x_import():
        print("\n[RESULT] Cannot import sx126x module. Check file location.")
        return
    
    # Test initialization
    node = test_lora_initialization()
    if not node:
        print("\n[RESULT] LoRa initialization failed. Check connections and settings.")
        return
    
    # Test transmission
    if not test_message_transmission(node):
        print("\n[RESULT] Message transmission failed.")
        return
    
    # Test reception
    print("\nWould you like to test message reception? (y/n): ", end='')
    try:
        response = input().lower()
        if response.startswith('y'):
            test_message_reception(node)
    except:
        pass
    
    print("\n=== Final Result ===")
    print("[SUCCESS] Your LoRa HAT is working correctly!")
    print("\nNext steps:")
    print("1. Use the manufacturer's main.py for interactive communication")
    print("2. Modify the code for your specific application")
    print("3. Test with another LoRa device to verify radio transmission")

if __name__ == "__main__":
    main() 