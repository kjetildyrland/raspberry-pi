#!/usr/bin/env python3
"""
PIXMOB Bracelet Controller
Controls PIXMOB bracelets using LoRa SX126X HAT
"""

import sys
import time
import os
import sx126x

class PIXMOBController:
    def __init__(self):
        """Initialize PIXMOB controller with LoRa module"""
        print("=== PIXMOB Controller Initialization ===")
        
        # Initialize LoRa with PIXMOB-compatible settings
        try:
            self.lora = sx126x.sx126x(
                serial_num="/dev/ttyS0",
                freq=868,           # 868 MHz - same as PIXMOB
                addr=0,             # Address 0
                power=22,           # Maximum power for better range
                rssi=True,          # Enable RSSI for debugging
                air_speed=2400,     # 2400 bps
                relay=False
            )
            print("[SUCCESS] LoRa module initialized for PIXMOB control")
            print(f"- Frequency: {self.lora.start_freq + self.lora.offset_freq} MHz")
            print(f"- Power: {self.lora.power} dBm")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize LoRa: {e}")
            raise
    
    def get_pixmob_commands(self):
        """Get PIXMOB command data from your converted .sub files"""
        # These are the hex patterns from your PIXMOB.py conversion
        # Each represents a different lighting pattern/color
        commands = {
            'gold_fade_in': bytes([0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]),
            'gold_fast_fade': bytes([0xaa, 0xaa, 0x5b, 0x61, 0x24, 0x6d, 0x61, 0x12, 0x51, 0x61, 0x22, 0x80]),
            'white_fastfade': bytes([0xaa, 0xaa, 0x56, 0xa1, 0x2d, 0x6d, 0x6d, 0x52, 0x51, 0x61, 0x0b]),
            'wine_fade_in': bytes([0xaa, 0xaa, 0x69, 0xa1, 0x21, 0x2d, 0x61, 0x23, 0x11, 0x61, 0x28, 0x40]),
            'nothing': bytes([0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40]),
            
            # Additional patterns from your RF captures
            'rand_blue_fade': bytes([0xaa, 0xaa, 0x61, 0x21, 0x0c, 0xa1, 0x2d, 0x62, 0x62, 0x61, 0x0d, 0x80]),
            'rand_red_fade': bytes([0xaa, 0xaa, 0x69, 0x21, 0x21, 0x2d, 0x61, 0x22, 0x62, 0x61, 0x19, 0x40]),
            'rand_white_blink': bytes([0xaa, 0xaa, 0x52, 0xa1, 0x2d, 0x6d, 0x6d, 0x59, 0x1a, 0xa1, 0x22, 0x40]),
            'rand_turq_blink': bytes([0xaa, 0xaa, 0x4d, 0xa1, 0x2d, 0x61, 0x2c, 0x6d, 0x93, 0x61, 0x24, 0x40]),
        }
        return commands
    
    def send_pixmob_command(self, command_name, repeat=3):
        """Send a PIXMOB command with proper LoRa packet format"""
        commands = self.get_pixmob_commands()
        
        if command_name not in commands:
            print(f"[ERROR] Unknown command: {command_name}")
            print(f"Available commands: {list(commands.keys())}")
            return False
        
        command_data = commands[command_name]
        print(f"\nSending PIXMOB command: {command_name}")
        print(f"Command data: {command_data.hex()}")
        print(f"Repeating {repeat} times for better reception...")
        
        try:
            for i in range(repeat):
                # Create LoRa packet in the format expected by your module
                # Broadcast to all PIXMOB devices
                target_addr = 65535  # Broadcast address
                packet_data = (bytes([target_addr >> 8]) + 
                              bytes([target_addr & 0xff]) + 
                              bytes([self.lora.offset_freq]) + 
                              bytes([self.lora.addr >> 8]) + 
                              bytes([self.lora.addr & 0xff]) + 
                              bytes([self.lora.offset_freq]) + 
                              command_data)
                
                self.lora.send(packet_data)
                print(f"  [SENT] Transmission {i+1}/{repeat}")
                time.sleep(0.5)  # Wait between transmissions
            
            print(f"[SUCCESS] PIXMOB command '{command_name}' transmitted!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send command: {e}")
            return False
    
    def send_raw_pixmob_data(self, command_name, repeat=3):
        """Send raw PIXMOB data without LoRa packet wrapper"""
        commands = self.get_pixmob_commands()
        
        if command_name not in commands:
            print(f"[ERROR] Unknown command: {command_name}")
            return False
        
        command_data = commands[command_name]
        print(f"\nSending RAW PIXMOB data: {command_name}")
        print(f"Raw data: {command_data.hex()}")
        
        try:
            for i in range(repeat):
                # Send raw data directly without LoRa packet format
                self.lora.send(command_data)
                print(f"  [SENT] Raw transmission {i+1}/{repeat}")
                time.sleep(0.3)
            
            print(f"[SUCCESS] Raw PIXMOB data '{command_name}' transmitted!")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send raw data: {e}")
            return False
    
    def wake_up_pixmob(self):
        """Send wake-up sequence to PIXMOB bracelets"""
        print("\n=== PIXMOB Wake-Up Sequence ===")
        
        # Try multiple wake-up approaches
        wake_commands = ['nothing', 'white_fastfade', 'gold_fade_in']
        
        for cmd in wake_commands:
            print(f"Sending wake-up command: {cmd}")
            self.send_pixmob_command(cmd, repeat=2)
            time.sleep(1)
        
        print("[INFO] Wake-up sequence completed")
    
    def demo_light_show(self):
        """Run a demo light show with different colors/patterns"""
        print("\n=== PIXMOB Demo Light Show ===")
        
        show_sequence = [
            ('gold_fade_in', 'Gold Fade In'),
            ('white_fastfade', 'White Fast Fade'),
            ('rand_blue_fade', 'Blue Fade'),
            ('rand_red_fade', 'Red Fade'),
            ('rand_turq_blink', 'Turquoise Blink'),
            ('rand_white_blink', 'White Blink'),
            ('wine_fade_in', 'Wine Fade In'),
            ('nothing', 'Turn Off')
        ]
        
        for cmd, description in show_sequence:
            print(f"\n--- {description} ---")
            self.send_pixmob_command(cmd, repeat=2)
            time.sleep(3)  # Wait to see the effect
        
        print("\n[SUCCESS] Demo light show completed!")

def main():
    """Main function"""
    print("PIXMOB Bracelet Controller")
    print("=========================")
    
    try:
        # Initialize controller
        controller = PIXMOBController()
        
        while True:
            print("\n=== PIXMOB Control Menu ===")
            print("1. Wake up PIXMOB bracelets")
            print("2. Send specific color command")
            print("3. Run demo light show")
            print("4. Send raw PIXMOB data (alternative method)")
            print("5. List available commands")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                controller.wake_up_pixmob()
                
            elif choice == "2":
                commands = controller.get_pixmob_commands()
                print(f"\nAvailable commands: {list(commands.keys())}")
                cmd = input("Enter command name: ").strip()
                if cmd in commands:
                    controller.send_pixmob_command(cmd)
                else:
                    print(f"Invalid command. Available: {list(commands.keys())}")
                    
            elif choice == "3":
                controller.demo_light_show()
                
            elif choice == "4":
                commands = controller.get_pixmob_commands()
                print(f"\nAvailable commands: {list(commands.keys())}")
                cmd = input("Enter command name for raw transmission: ").strip()
                if cmd in commands:
                    controller.send_raw_pixmob_data(cmd)
                else:
                    print(f"Invalid command. Available: {list(commands.keys())}")
                    
            elif choice == "5":
                commands = controller.get_pixmob_commands()
                print(f"\nAvailable PIXMOB commands:")
                for i, cmd in enumerate(commands.keys(), 1):
                    print(f"  {i}. {cmd}")
                    
            elif choice == "6":
                print("Exiting PIXMOB controller...")
                break
                
            else:
                print("Invalid choice. Please enter 1-6.")
                
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("PIXMOB controller finished.")

if __name__ == "__main__":
    main() 