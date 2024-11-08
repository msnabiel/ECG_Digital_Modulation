import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import serial
import time

# Configure the serial port
serial_port = '/dev/cu.usbmodem11201'  # Adjust to match your port
baud_rate = 9600  # Must match the baud rate in your Arduino code
threshold = 60

try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Connected to {serial_port} at {baud_rate} baud rate.")
    time.sleep(2)  # Allow time for the connection to stabilize
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
    exit()

# Parameters for the signal generation
fs = 1000  # Sampling frequency
fc = 10    # Carrier frequency
bit_rate = 1  # Bit rate for binary signal
t = np.arange(0, 1, 1/fs)  # Time vector for 1 second window

# Initialize an empty list to hold received data bits
data_bits = []

# Define the figure and subplots
fig, axs = plt.subplots(4, 1, figsize=(10, 8))

# Set up the initial empty plots
digital_line, = axs[0].plot([], [], 'r')
carrier_line, = axs[1].plot([], [], 'b')
ask_line, = axs[2].plot([], [], 'b')
fsk_line, = axs[3].plot([], [], 'orange')

# Plot titles
axs[0].set_title("Digital Signal")
axs[1].set_title("Carrier Signal")
axs[2].set_title("ASK Signal")
axs[3].set_title("FSK Signal")

# Plotting limits
for ax in axs:
    ax.set_xlim(0, 1)
    ax.set_ylim(-1.5, 1.5)
    ax.grid()

# Carrier signal
carrier_signal = np.sin(2 * np.pi * fc * t)

# Animation update function
def update(frame):
    global data_bits

    # Read data from serial port
    if ser.in_waiting > 0:  # Check if there's data in the serial buffer
        data = ser.readline().decode('utf-8').strip()
        try:
            # Extract numeric part of the data (if it starts with 'a0:')
            if data.startswith('a0:'):
                value = float(data.split(':')[1].strip())  # Get the numeric value after 'a0:'
                print("Received Value: ", value)
                # Append 1 if value > threshold, otherwise append 0
                if value > threshold:
                    data_bits.append(1)
                else:
                    data_bits.append(0)
        except ValueError:
            print(f"Invalid data received: {data}")
    
    # Ensure data_bits has enough data for the animation
    if len(data_bits) < (frame + 1):
        data_bits.append(0)  # Default to 0 if not enough data

    # Make sure the frame is within the bounds of the available data
    frame %= len(data_bits)
    
    # Segment for the current frame
    digital_signal_segment = np.repeat(data_bits[frame], len(t))

    # ASK signal
    ask_signal = carrier_signal * digital_signal_segment
    
    # FSK signal with different frequencies for 0 and 1
    f_high = 15
    f_low = 5
    fsk_signal = np.sin(2 * np.pi * (f_low + (f_high - f_low) * digital_signal_segment) * t)

    # Update the plots
    digital_line.set_data(t, digital_signal_segment)
    carrier_line.set_data(t, carrier_signal)
    ask_line.set_data(t, ask_signal)
    fsk_line.set_data(t, fsk_signal)
    
    return digital_line, carrier_line, ask_line, fsk_line

# Create the animation with a slower interval
ani = FuncAnimation(fig, update, frames=range(1000), blit=True, interval=300)  # 300 ms interval

# Display the animation
plt.tight_layout()
plt.show()

# Close the serial connection
ser.close()
