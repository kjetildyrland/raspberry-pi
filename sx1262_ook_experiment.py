#!/usr/bin/env python3
"""
Experimental SX1262 OOK Mode Driver
Attempts to bypass Waveshare firmware for direct chip access
WARNING: This is experimental and may not work with the HAT
"""

import RPi.GPIO as GPIO
import spidev
import time
import struct

class SX1262_OOK:
    """
    Experimental SX1262 driver with OOK support
    Requires direct SPI access to the chip
    """
    
    # SPI Configuration
    SPI_BUS = 0
    SPI_DEVICE = 0
    
    # GPIO Pins (adjust based on your HAT)
    RESET_PIN = 18    # Adjust based on HAT schematic
    BUSY_PIN = 24     # Adjust based on HAT schematic
    DIO1_PIN = 25     # Adjust based on HAT schematic
    
    # SX1262 Commands
    CMD_SET_SLEEP = 0x84
    CMD_SET_STANDBY = 0x80
    CMD_SET_TX = 0x83
    CMD_SET_RX = 0x82
    CMD_SET_PACKET_TYPE = 0x8A
    CMD_WRITE_REGISTER = 0x0D
    CMD_READ_REGISTER = 0x1D
    CMD_WRITE_BUFFER = 0x0E
    CMD_SET_TX_PARAMS = 0x8E
    CMD_SET_MODULATION_PARAMS = 0x8B
    CMD_SET_PACKET_PARAMS = 0x8C
    CMD_SET_RF_FREQUENCY = 0x86
    
    # Register Addresses
    REG_PACKET_TYPE = 0x0736
    REG_BITRATE_MSB = 0x06AC
    REG_BITRATE_LSB = 0x06AD
    REG_FDEV_MSB = 0x06AE
    REG_FDEV_LSB = 0x06AF
    
    # Packet Types
    PACKET_TYPE_GFSK = 0x00
    PACKET_TYPE_LORA = 0x01
    
    def __init__(self):
        """Initialize SX1262 for OOK mode"""
        print("Initializing SX1262 OOK experiment...")
        print("WARNING: This bypasses Waveshare firmware!")
        
        try:
            # Setup GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            if self.RESET_PIN:
                GPIO.setup(self.RESET_PIN, GPIO.OUT)
            if self.BUSY_PIN:
                GPIO.setup(self.BUSY_PIN, GPIO.IN)
            if self.DIO1_PIN:
                GPIO.setup(self.DIO1_PIN, GPIO.IN)
            
            # Setup SPI
            self.spi = spidev.SpiDev()
            self.spi.open(self.SPI_BUS, self.SPI_DEVICE)
            self.spi.max_speed_hz = 1000000  # 1MHz
            self.spi.mode = 0
            
            print("SPI and GPIO initialized")
            
        except Exception as e:
            print(f"Initialization error: {e}")
            print("This likely means direct SPI access isn't available")
            raise
    
    def reset(self):
        """Hardware reset of SX1262"""
        if self.RESET_PIN:
            GPIO.output(self.RESET_PIN, GPIO.LOW)
            time.sleep(0.01)
            GPIO.output(self.RESET_PIN, GPIO.HIGH)
            time.sleep(0.01)
    
    def wait_busy(self, timeout=1.0):
        """Wait for chip to not be busy"""
        if not self.BUSY_PIN:
            time.sleep(0.01)
            return True
            
        start = time.time()
        while GPIO.input(self.BUSY_PIN) and (time.time() - start) < timeout:
            time.sleep(0.001)
        return not GPIO.input(self.BUSY_PIN)
    
    def write_command(self, cmd, data=None):
        """Write command to SX1262"""
        if not self.wait_busy():
            raise Exception("Chip busy timeout")
        
        if data is None:
            data = []
        elif isinstance(data, int):
            data = [data]
        elif isinstance(data, bytes):
            data = list(data)
        
        packet = [cmd] + data
        result = self.spi.xfer2(packet)
        return result
    
    def read_register(self, addr, length=1):
        """Read register from SX1262"""
        addr_msb = (addr >> 8) & 0xFF
        addr_lsb = addr & 0xFF
        
        cmd = [self.CMD_READ_REGISTER, addr_msb, addr_lsb, 0x00] + [0x00] * length
        result = self.spi.xfer2(cmd)
        return result[4:4+length]
    
    def write_register(self, addr, data):
        """Write register to SX1262"""
        addr_msb = (addr >> 8) & 0xFF
        addr_lsb = addr & 0xFF
        
        if isinstance(data, int):
            data = [data]
        elif isinstance(data, bytes):
            data = list(data)
        
        cmd = [self.CMD_WRITE_REGISTER, addr_msb, addr_lsb] + data
        self.spi.xfer2(cmd)
    
    def set_standby(self):
        """Set chip to standby mode"""
        self.write_command(self.CMD_SET_STANDBY, 0x00)
        time.sleep(0.01)
    
    def set_packet_type_gfsk(self):
        """Set packet type to GFSK (needed for OOK)"""
        self.write_command(self.CMD_SET_PACKET_TYPE, self.PACKET_TYPE_GFSK)
        time.sleep(0.01)
    
    def set_frequency(self, freq_hz):
        """Set RF frequency"""
        # SX1262 frequency calculation: freq_reg = freq_hz * 2^25 / 32MHz
        freq_reg = int((freq_hz * (2**25)) / 32000000)
        
        freq_bytes = [
            (freq_reg >> 24) & 0xFF,
            (freq_reg >> 16) & 0xFF,
            (freq_reg >> 8) & 0xFF,
            freq_reg & 0xFF
        ]
        
        self.write_command(self.CMD_SET_RF_FREQUENCY, freq_bytes)
    
    def configure_ook_mode(self, bitrate=1000):
        """Configure OOK modulation parameters"""
        print(f"Configuring OOK mode, bitrate: {bitrate} bps")
        
        # Set modulation parameters for GFSK/OOK
        # Parameters: BitRate, ModulationShaping, Bandwidth, FreqDev
        
        # Calculate bitrate register value
        bitrate_reg = int(32000000 / bitrate)
        
        modulation_params = [
            (bitrate_reg >> 16) & 0xFF,  # Bitrate MSB
            (bitrate_reg >> 8) & 0xFF,   # Bitrate Mid
            bitrate_reg & 0xFF,          # Bitrate LSB
            0x00,                        # Modulation shaping (none)
            0x0E,                        # Bandwidth (467 kHz)
            0x00, 0x00, 0x00            # Frequency deviation (0 for OOK)
        ]
        
        self.write_command(self.CMD_SET_MODULATION_PARAMS, modulation_params)
        
        # Configure packet parameters for OOK
        packet_params = [
            0x00, 0x08,  # Preamble length
            0x00,        # Preamble detector off
            0xFF,        # Sync word length (disable)
            0x00,        # Address filtering off
            0x01,        # Variable length packet
            0xFF,        # Payload length
            0x00,        # CRC off
            0x00         # Whitening off
        ]
        
        self.write_command(self.CMD_SET_PACKET_PARAMS, packet_params)
    
    def set_tx_power(self, power_dbm=22):
        """Set TX power"""
        # SX1262 power configuration
        if power_dbm > 22:
            power_dbm = 22
        if power_dbm < -9:
            power_dbm = -9
        
        # Power value calculation for SX1262
        power_val = power_dbm
        
        self.write_command(self.CMD_SET_TX_PARAMS, [power_val, 0x04])
    
    def send_ook_data(self, data, bit_duration_us=1000):
        """Send OOK data by manually controlling TX"""
        print(f"Sending OOK data: {len(data)} bytes")
        
        for byte_val in data:
            for bit_pos in range(7, -1, -1):  # MSB first
                bit = (byte_val >> bit_pos) & 1
                
                if bit:
                    # Turn on transmitter
                    self.write_command(self.CMD_SET_TX, [0x00, 0x00, 0x00])
                else:
                    # Turn off transmitter (standby)
                    self.write_command(self.CMD_SET_STANDBY, 0x00)
                
                time.sleep(bit_duration_us / 1000000)  # Convert to seconds
        
        # Return to standby
        self.write_command(self.CMD_SET_STANDBY, 0x00)
    
    def test_ook_mode(self):
        """Test OOK mode with PIXMOB data"""
        print("=== SX1262 OOK Mode Test ===")
        
        try:
            # Initialize chip
            self.reset()
            time.sleep(0.1)
            
            self.set_standby()
            self.set_packet_type_gfsk()
            self.set_frequency(868000000)  # 868 MHz
            self.configure_ook_mode(1000)  # 1000 bps
            self.set_tx_power(22)          # Max power
            
            print("SX1262 configured for OOK mode")
            
            # PIXMOB test data
            pixmob_gold = [0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40]
            
            # Send wake sequence
            print("Sending OOK wake sequence...")
            wake_data = [0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40]
            for i in range(100):
                self.send_ook_data(wake_data, 1000)  # 1ms bit duration
                time.sleep(0.1)
                if i % 20 == 0:
                    print(f"  Wake transmission {i}/100")
            
            # Send color command
            print("Sending OOK gold command...")
            for i in range(20):
                self.send_ook_data(pixmob_gold, 1000)
                time.sleep(0.2)
                print(f"  Gold transmission {i+1}/20")
            
            return True
            
        except Exception as e:
            print(f"OOK test error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'spi'):
                self.spi.close()
            GPIO.cleanup()
        except:
            pass

def main():
    """Main test function"""
    print("SX1262 OOK Mode Experiment")
    print("==========================")
    print("Attempting direct SPI access to SX1262 chip")
    print("This bypasses the Waveshare firmware!")
    print()
    
    ook_radio = None
    try:
        ook_radio = SX1262_OOK()
        
        # Test OOK mode
        success = ook_radio.test_ook_mode()
        
        if success:
            response = input("\nAny PIXMOB response to OOK transmission? (y/n): ").lower().strip()
            if response.startswith('y'):
                print("[SUCCESS] OOK mode works with SX1262!")
            else:
                print("No response - OOK attempt unsuccessful")
        
    except Exception as e:
        print(f"Experiment failed: {e}")
        print("\nThis is expected because:")
        print("1. Waveshare HAT likely doesn't expose SPI pins")
        print("2. Firmware may block direct register access")
        print("3. Different pin configurations needed")
        
    finally:
        if ook_radio:
            ook_radio.cleanup()
    
    print("\n=== CONCLUSION ===")
    print("Direct SX1262 register access is likely impossible with")
    print("the Waveshare HAT due to firmware limitations.")
    print("\nRecommended solutions:")
    print("- Use CC1101 or RFM69 module for OOK")
    print("- Get a bare SX1262 breakout board")
    print("- Use Software Defined Radio (SDR)")

if __name__ == "__main__":
    main() 