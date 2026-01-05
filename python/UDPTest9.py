# this script will read all 22, 4 byte words.

import socket
import struct
import time

# Get the target IP address from the user
UDP_IP = input("Enter the target IP address (e.g., 10.4.24.100): ")
UDP_PORT = 5000  # You can also make this user input if needed

# Create a UDP socket for sending and receiving
sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock1.settimeout(2)  # Set a timeout for receiving data
server_address = (UDP_IP, UDP_PORT)

def decode_status(index_value):
    """Decode the status from the given index value."""
    network_command = (index_value >> 0) & 1
    fp_command = (index_value >> 1) & 1
    rp_command = (index_value >> 2) & 1
    relay_status = (index_value >> 3) & 1
    aux_relay = (index_value >> 4) & 1

    # Print the decoded statuses
    print(f"Integer value: {index_value}")
    print(f"Network Command: {'ON' if network_command else 'OFF'}")
    print(f"FP Command: {'ON' if fp_command else 'OFF'}")
    print(f"RP Command: {'ON' if rp_command else 'OFF'}")
    print(f"3-PH Relay: {'Output OK' if relay_status else 'Bad Output'}")
    print(f"Aux Relay: {'Closed' if aux_relay else 'Open'}")

def process_response(received_values, message):
    """Process the received values based on the command."""
    # Expect PDUdata[2] = 1000.0 and PDUdata[21] = 1001.0
    if received_values[2] == 1000.0 and received_values[21] == 1001.0:
        if message == "Status":
            print("All 22 values received:")
            for i, value in enumerate(received_values):
                # Truncate values at indexes 3, 4, 5 to one decimal point
                if i in [3, 4, 5]:
                    value = float(f"{value:.1f}")
                print(f"Index {i}: {value}")
        else:
            channel_map = {
                "Ch1Status": 4,
                "Ch2Status": 5,
                "Ch3Status": 6,
                "Ch4Status": 7,
            }
            if message in channel_map:
                index_to_decode = channel_map[message]
                int_value_at_index = int(received_values[index_to_decode])
                print(f"\nDecoding status for {message}:")
                decode_status(int_value_at_index)
    else:
        print("Checksum error: values do not match expected checksum. :(")

try:
    while True:
        message = input("Enter the command to send (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break

        # Check if the message is one of the special commands
        if message in ["Ch1Status", "Ch2Status", "Ch3Status", "Ch4Status", "Status"]:
            sock1.sendto("Status".encode(), server_address)
            print(f"Sent UDP packet to {UDP_IP}:{UDP_PORT}: Status")

            try:
                data, addr = sock1.recvfrom(2048)  # Buffer size is 2048 bytes
                print(f"Received response from {addr}: length = {len(data)} bytes")

                # Unpack 22 floats (22 * 4 = 88 bytes)
                received_values = struct.unpack('22f', data)
                process_response(received_values, message)

            except socket.timeout:
                print("No response received within the timeout period.")
        else:
            # Send the command without expecting a response
            sock1.sendto(message.encode(), server_address)
            print(f"Sent UDP packet to {UDP_IP}:{UDP_PORT}: {message} (no response expected)")

        time.sleep(1)

finally:
    sock1.close()