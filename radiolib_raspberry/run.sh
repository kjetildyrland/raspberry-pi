#!/bin/bash

# Script to run the PixMob controller with proper permissions

echo "Starting PixMob Controller..."
echo "Note: This program requires root privileges to access GPIO pins."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo:"
    echo "sudo ./run.sh"
    exit 1
fi

# Check if the executable exists
if [ ! -f "./main" ]; then
    echo "Executable 'main' not found. Please compile first:"
    echo "make"
    exit 1
fi

# Stop any running pigpio daemon
sudo killall pigpiod 2>/dev/null || true

# Start pigpio daemon
echo "Starting pigpio daemon..."
sudo pigpiod

# Wait a moment for daemon to start
sleep 1

# Run the program
echo "Running PixMob controller..."
./main

# Clean up - stop pigpio daemon when done
echo "Stopping pigpio daemon..."
sudo killall pigpiod 2>/dev/null || true

echo "Done." 