import socket
import struct
import time

# Get the target IP address from the user
UDP_IP = input("Enter the target IP address (e.g., 10.4.24.100): ").strip()
UDP_PORT = 5000
SERVER = (UDP_IP, UDP_PORT)

# Fixed 8-byte header (network byte order representation as raw bytes)
HEADER = bytes((0x50, 0x53, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x50))
HEADER_LEN = 8

# Expected Status response: 22 words * 4 bytes = 88 bytes total (includes 8-byte header)
STATUS_WORDS = 22
STATUS_BYTES = STATUS_WORDS * 4

# Create a UDP socket for sending and receiving
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2.0)

def _verify_header(data: bytes) -> bool:
    return len(data) >= HEADER_LEN and data[:HEADER_LEN] == HEADER

def _send(payload: bytes) -> None:
    """Send a packet with the required firmware header."""
    sock.sendto(HEADER + payload, SERVER)

def send_status():
    """
    Send 'Status' with header, expect 88 bytes (22 words).
    Verify header, then decode remaining 80 bytes (20 words) as big-endian floats.
    """
    try:
        _send(b"Status")
        data, addr = sock.recvfrom(2048)
        print(f"Received response from {addr}: {len(data)} bytes")

        if len(data) != STATUS_BYTES:
            print(f"Unexpected response size (expected {STATUS_BYTES} bytes).")
            print("HEX:", data.hex(" ", 1))
            return

        if not _verify_header(data):
            print("Header check failed.")
            print("Expected header:", HEADER.hex(" ", 1))
            print("Received header:", data[:HEADER_LEN].hex(" ", 1))
            return

        payload = data[HEADER_LEN:]  # 80 bytes expected
        if len(payload) != 80:
            print(f"Unexpected payload size after header (expected 80 bytes, got {len(payload)}).")
            return

        # Decode payload as network byte order (big-endian) 20 floats
        values = struct.unpack("!20f", payload)

        # Marker check (kept from original logic, now using big-endian decoded floats)
        ok = (values[0] == 1000.0 and values[19] == 1001.0)
        print(f"Marker check -> Payload[0]: {values[0]} | Payload[19]: {values[19]} | OK: {ok}")
        if not ok:
            print("Markers not valid (or payload is no longer float data).")

        print("All 20 payload values:")
        for i, v in enumerate(values):
            print(f"Payload[{i:2d}]: {v}")

    except socket.timeout:
        print("No response to Status within timeout.")

def send_status_raw():
    """Send 'Status' with header and print raw bytes (useful for debugging)."""
    try:
        _send(b"Status")
        data, addr = sock.recvfrom(2048)
        print(f"Received response from {addr}: {len(data)} bytes")
        print("HEX:", data.hex(" ", 1))
        print("Header OK:", _verify_header(data))
    except socket.timeout:
        print("No response to Status within timeout.")

def send_two_hex_bytes(b1_str: str, b2_str: str):
    """Send exactly two hex bytes, preceded by the required 8-byte header."""
    b1 = int(b1_str, 16)
    b2 = int(b2_str, 16)
    if not (0 <= b1 <= 0xFF and 0 <= b2 <= 0xFF):
        raise ValueError("Hex byte out of range 0x00..0xFF")
    pkt = bytes((b1, b2))
    _send(pkt)
    print(f"Sent hex bytes (with header): {b1:02X} {b2:02X}")

print("\nCommands:")
print("  status          -> send 'Status' (with header), expect 88-byte reply, verify header, decode payload")
print("  statusraw       -> send 'Status' (with header), print raw reply bytes")
print("  0x55 0x11       -> send two hex bytes (with header)")
print("  hex:55 11       -> send two hex bytes (with header)")
print("  exit            -> quit\n")

try:
    while True:
        msg = input("cmd> ").strip()
        if not msg:
            continue
        low = msg.lower()

        if low == "exit":
            break

        if low == "status":
            send_status()
            time.sleep(0.2)
            continue

        if low == "statusraw":
            send_status_raw()
            time.sleep(0.2)
            continue

        # Support "0x55 0x11"
        toks = msg.split()
        if len(toks) == 2 and all(t.lower().startswith("0x") for t in toks):
            try:
                send_two_hex_bytes(toks[0], toks[1])
            except ValueError as e:
                print(f"Error: {e}")
            time.sleep(0.2)
            continue

        # Support "hex:55 11" or "hex: 55 11"
        if low.startswith("hex:"):
            parts = msg[4:].strip().split()
            if len(parts) == 2:
                try:
                    send_two_hex_bytes(parts[0], parts[1])
                except ValueError:
                    print("Invalid hex. Use: hex:55 11  (bytes are hex, 00..FF)")
            else:
                print("Usage: hex:AA BB")
            time.sleep(0.2)
            continue

        print("Unknown command. Try: status | statusraw | 0x55 0x11 | hex:55 11 | exit")

finally:
    sock.close()
