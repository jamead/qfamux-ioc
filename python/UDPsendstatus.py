#!/usr/bin/env python3
import socket
import struct
import time
import math
import random


def build_status_frame(t):
    """Builds the original 80-byte ALS-U frame (20 × 4-byte words)."""

    frame_start = 1000

    ph_a = 10.0 + 5.0 * math.sin(2 * math.pi * (t / 60.0))
    ph_b = 11.0 + 5.0 * math.sin(2 * math.pi * (t / 60.0) + 2.0)
    ph_c = 12.0 + 5.0 * math.sin(2 * math.pi * (t / 60.0) + 4.0)

    ch1_status = 0x1
    ch2_status = 0x2
    ch3_status = 0x4
    ch4_status = 0x8

    nu8 = 0
    nu9 = 0

    front_temp = 30.0 + 2.0 * math.sin(2 * math.pi * (t / 300.0))
    rear_temp  = 32.0 + 2.0 * math.sin(2 * math.pi * (t / 300.0) + 1.0)

    serial_number = 12345678
    pdu_model     = 6404
    fw_version    = 1234 

    nu15 = nu16 = nu17 = 0

    wdt_flag = 1 if random.random() < 0.01 else 0
    frame_end = 1001

    fmt = '!I f f f I I I I I I f f I I I I I I i I'

    return struct.pack(fmt,
        frame_start, ph_a, ph_b, ph_c,
        ch1_status, ch2_status, ch3_status, ch4_status,
        nu8, nu9,
        front_temp, rear_temp,
        serial_number, pdu_model, fw_version,
        nu15, nu16, nu17,
        wdt_flag,
        frame_end
    )


def build_full_udp_packet(t, msg_id=15):
    """Builds the final UDP payload (8-byte header + 80-byte body)."""

    body = build_status_frame(t)       # 80 bytes
    body_len = len(body)               # 80

    # ---- 8-byte header ----
    # '!c c H I' layout:
    #   c = 'P'
    #   c = 'S'
    #   H = 2-byte message ID
    #   I = 4-byte body length
    header = struct.pack("!c c H I",
                         b'P',        # byte 0
                         b'S',        # byte 1
                         msg_id,      # bytes 2–3
                         body_len)    # bytes 4–7

    return header + body               # 88 bytes total


def main():
    UDP_IP = "192.168.1.87"
    UDP_PORT = 1234

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.bind(("0.0.0.0", 5000))


    print("Sending header + 80-byte frame at 1 Hz…")
    t = 0
    while True:
        packet = build_full_udp_packet(t)
        sock.sendto(packet, (UDP_IP, UDP_PORT))
        print(f"Sent {len(packet)} bytes")  # should print 88
        t += 1
        time.sleep(1)


if __name__ == "__main__":
    main()


