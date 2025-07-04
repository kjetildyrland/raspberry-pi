#include <RadioLib/RadioLib.h>
#include <array>
#include <cstdint>

// include the hardware abstraction layer
#include "PiHal.h"

#include "BuildOpt.h"

// Define the GPIO pin for DIO2 output (choose an available GPIO pin)
#define RADIO_DIO_2_PORT 23

PiHal *hal = new PiHal(1);

unsigned long Timestamp;
SX1262 radio = new Module(hal, 8, 17, 22, 7);
// Waveshare SX1262 HAT pinout: NSS=8, DIO1=17, RESET=22, BUSY=7
// SX126X radio = new Module(RADIO_NSS_PORT, RADIO_DIO_1_PORT, RADIO_BUSY_PORT, RADIO_RESET_PORT, RADIO_DIO_1_PORT);
int ColorIndex = 0, BitDuration = 500;
#define ValidValuesCount 4
#define BytesCount 12

void MicrosDelay(unsigned long m)
{
    unsigned long n = hal->micros();
    while (hal->micros() - n < m)
    {
        // yield equivalent - just a small delay
        hal->delayMicroseconds(1);
    }
}

std::array<uint8_t, BytesCount> ByteArray;
std::array<std::array<int, BytesCount>, ValidValuesCount> ColorArrayArray{{
    {0xaa, 0xaa, 0x65, 0x21, 0x24, 0x6d, 0x61, 0x23, 0x11, 0x61, 0x2b, 0x40}, // gold_fade_in
    {0xaa, 0xaa, 0x5b, 0x61, 0x24, 0x6d, 0x61, 0x12, 0x51, 0x61, 0x22, 0x80}, // gold_fast_fade
    // {0xaa,0xaa,0x55,0xa1,0x21,0x21,0x21,0x18,0x8d,0xa1,0xa,0x40}, //nothing
    // {0xaa, 0xaa, 0x61, 0x21, 0xc, 0xa1, 0x2d, 0x62, 0x62, 0x61, 0xd, 0x80}, // rand_blue_fade
    // {0xaa,0xaa,0x50,0xa1,0x24,0x6d,0x61,0x19,0x1a,0xa1,0x12,0x40}, //rand_gold_blink
    // {0xaa,0xaa,0x52,0xa1,0x24,0x6d,0x61,0x22,0x6a,0x61,0xd}, //rand_gold_fade
    // {0xaa,0xaa,0x55,0xa1,0x24,0x6d,0x61,0xa,0x59,0x61,0x18,0x40}, //rand_gold_fastfade
    // {0xaa,0xaa,0x69,0x21,0x21,0x2d,0x61,0x22,0x62,0x61,0x19,0x40}, //rand_red_fade
    // {0xaa,0xaa,0x5b,0x61,0x21,0x2d,0x61,0x19,0x1a,0xa1,0xa,0x40}, //rand_red_fastblink
    // {0xaa,0xaa,0x53,0x21,0x21,0x2d,0x61,0xa,0x59,0x61,0x11,0x40}, //rand_red_fastfade
    // {0xaa,0xaa,0x4d,0xa1,0x2d,0x61,0x2c,0x6d,0x93,0x61,0x24,0x40}, //rand_turq_blink
    // {0xaa,0xaa,0x52,0xa1,0x2d,0x6d,0x6d,0x59,0x1a,0xa1,0x22,0x40}, //rand_white_blink
    // {0xaa,0xaa,0x59,0x61,0x2d,0x6d,0x6d,0x62,0x62,0x61,0x2b,0x40}, //rand_white_fade
    // {0xaa,0xaa,0x66,0xa1,0x2d,0x6d,0x6d,0x4a,0x59,0x61,0x2a,0x40}, //rand_white_fastfade
    {0xaa, 0xaa, 0x56, 0xa1, 0x2d, 0x6d, 0x6d, 0x52, 0x51, 0x61, 0xb},        // white_fastfade
    {0xaa, 0xaa, 0x69, 0xa1, 0x21, 0x2d, 0x61, 0x23, 0x11, 0x61, 0x28, 0x40}, // wine_fade_in
}};

void ByteArraySend(void)
{
    for (int j = 0; j < sizeof(ByteArray); j++)
        for (int i = 0; i < 8; i++)
        {
            hal->digitalWrite(RADIO_DIO_2_PORT, (128U & ByteArray[j]) / 128U);
            MicrosDelay(BitDuration);
            ByteArray[j] <<= 1;
        }
    hal->digitalWrite(RADIO_DIO_2_PORT, 0);
    for (int k = 0; k < 8; k++)
        MicrosDelay(BitDuration);
}

int main(int argc, char **argv)
{
    // Initialize the HAL first, before any other operations
    printf("Initializing GPIO and SPI... ");
    hal->init();
    printf("success!\n");
    
    // Set up the DIO2 pin as output
    hal->pinMode(RADIO_DIO_2_PORT, PI_OUTPUT);
    
    // Initialize radio
    printf("[SX1262] Initializing ... ");
    int state = radio.beginFSK(868.0, 4.8, 0.0, 20.0, 10, 16, 0.0, false);
    if (state != RADIOLIB_ERR_NONE)
    {
        printf("failed, code %d\n", state);
        hal->term();
        return (1);
    }
    printf("success!\n");
    
    radio.setFrequency(868.0F);
    // SX1262 doesn't support setOOK method - OOK mode is set during beginFSK
    radio.transmitDirect();
    
    // Initialize timestamp
    Timestamp = hal->millis();

    // Main loop
    for (;;)
    {
        ByteArray = {0xaa, 0xaa, 0x55, 0xa1, 0x21, 0x21, 0x21, 0x18, 0x8d, 0xa1, 0x0a, 0x40};
        ByteArraySend();
        
        if (hal->millis() - Timestamp > 2000)
        {
            Timestamp = hal->millis();
            for (int i = 0; i < BytesCount; i++)
                ByteArray[i] = ColorArrayArray[ColorIndex][i];
            ByteArraySend();
            ColorIndex = (ColorIndex + 1) % ValidValuesCount;
        }
        
        // Small delay to prevent excessive CPU usage
        hal->delay(10);
    }
    
    // Cleanup
    hal->term();
    return (0);
}