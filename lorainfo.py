#!/usr/bin/env python3
import time
import sys
import serial
import argparse 

from serial.threaded import LineReader, ReaderThread

parser = argparse.ArgumentParser(description='LoRa Radio information.')
parser.add_argument('port', help="LoRa-E5 module Serial port")
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
        self.send_cmd('AT+ID')
        self.send_cmd('AT+CLASS')
        self.send_cmd('AT+DR=SCHEME')
        self.send_cmd('AT+CH')
        self.send_cmd('AT+BEACON=INFO')        
        self.send_cmd('AT+MODE')   
        self.send_cmd('AT+TEMP')      
        

    def send_cmd(self, cmd, delay=0.8):
        print("SEND: %s" % cmd)
        self.write_line(cmd)
        time.sleep(delay)


ser = serial.Serial(args.port, baudrate=9600)
with ReaderThread(ser, PrintLines) as protocol:
    while(1):
        protocol.test()
        time.sleep(10)
        break
