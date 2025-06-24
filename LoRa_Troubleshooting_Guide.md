# LoRa SX126X Troubleshooting Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the simple test:**
   ```bash
   python3 lora_simple_test.py
   ```

3. **Run the full transmitter:**
   ```bash
   python3 lora_transmitter.py
   ```

## Common Issues and Solutions

### 1. "Failed to initialize LoRa module"

**Possible causes:**
- Incorrect wiring
- SPI not enabled
- Wrong GPIO pin configuration
- Power supply issues

**Solutions:**
- Check SPI wiring:
  - MOSI: GPIO 10 (Pin 19)
  - MISO: GPIO 9 (Pin 21)
  - SCK: GPIO 11 (Pin 23)
  - CS0: GPIO 8 (Pin 24)
- Enable SPI: `sudo raspi-config` → Interface Options → SPI → Enable
- Verify 3.3V power supply to LoRa module
- Check Reset and DIO pin connections

### 2. "LoRaRF library not found"

**Solution:**
```bash
pip install LoRaRF
```

### 3. No signal transmission detected

**Possible causes:**
- Wrong frequency setting
- Incorrect modulation parameters
- Hardware connection issues
- Antenna not connected

**Solutions:**
- Verify frequency matches your module (868MHz/915MHz)
- Check antenna connection
- Verify all GPIO pin connections
- Test with spectrum analyzer or another LoRa device

### 4. Permission denied errors

**Solution:**
```bash
sudo usermod -a -G spi,gpio $USER
# Then log out and log back in
```

## Hardware Connections

### Standard SX126X LoRa HAT Pinout:
```
LoRa Module   →   Raspberry Pi
VCC           →   3.3V (Pin 1)
GND           →   GND (Pin 6)
MOSI          →   GPIO 10 (Pin 19)
MISO          →   GPIO 9 (Pin 21)
SCK           →   GPIO 11 (Pin 23)
NSS/CS        →   GPIO 8 (Pin 24)
RESET         →   GPIO 22 (Pin 15)
DIO1          →   GPIO 17 (Pin 11)
BUSY          →   GPIO 7 (Pin 26)
```

## Testing Signal Transmission

### Method 1: Use another LoRa device
Set up a receiver with matching frequency and parameters.

### Method 2: Use RTL-SDR
```bash
# Install rtl-sdr tools
sudo apt install rtl-sdr

# Monitor 868MHz for LoRa signals
rtl_sdr -f 868000000 -s 1000000 - | hexdump -C
```

### Method 3: Use spectrum analyzer software
- SDR# (Windows)
- GQRX (Linux)
- CubicSDR (Cross-platform)

## Your Previous Code Issues

### script.py problems:
1. ❌ Using serial port directly instead of LoRa library
2. ❌ Converting RF timing data to UTF-8 text
3. ❌ No proper LoRa initialization

### script2.py problems:
1. ❌ Sending raw SubGHz timing data as LoRa packets
2. ❌ Wrong data format conversion

### Correct approach:
1. ✅ Use LoRaRF library for proper LoRa communication
2. ✅ Send actual data bytes (not timing data)
3. ✅ Proper module initialization and configuration

## Frequency Bands

Make sure your module frequency matches your region:
- **Europe**: 868 MHz
- **North America**: 915 MHz  
- **Asia**: 433 MHz or 470 MHz

## Advanced Configuration

### For longer range:
```python
lora.setModulationParams(SF=12, BW=125, CR=8)  # Max range, slow speed
```

### For faster transmission:
```python
lora.setModulationParams(SF=7, BW=500, CR=5)   # Short range, fast speed
```

### For better reliability:
```python
lora.setModulationParams(SF=9, BW=125, CR=8)   # Balanced
```

## Contact and Support

If you continue having issues:
1. Check the LoRaRF library documentation
2. Verify hardware with manufacturer specs
3. Test with known working LoRa code examples
4. Consider using an oscilloscope to verify SPI communication 