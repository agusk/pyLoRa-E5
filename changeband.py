#!/usr/bin/env python3
import time
import sys
import serial
import argparse 

from serial.threaded import LineReader, ReaderThread

# sample python changeband.py COM16 US915
parser = argparse.ArgumentParser(description='LoRa Radio Band')
parser.add_argument('port', help="LoRa-E5 module Serial port")
parser.add_argument('band', help="LoRa-E5 module Band")
args = parser.parse_args()

class PrintLines(LineReader):
    def connection_made(self, transport):
        print("connection made")
        self.transport = transport

    def handle_line(self, data):
        # if data == "ok":
        #     return
        print("RECV: %s" % data)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")

    def test(self):        
        self.send_cmd('AT+VER')
        self.send_cmd("AT+DR=%s" % args.band)
        self.send_cmd('AT+DR=SCHEME')
        

    def send_cmd(self, cmd, delay=0.5):
        print("SEND: %s" % cmd)
        self.write_line(cmd)
        time.sleep(delay)


ser = serial.Serial(args.port, baudrate=9600)
with ReaderThread(ser, PrintLines) as protocol:
    while(1):
        protocol.test()
        time.sleep(5)
        break
