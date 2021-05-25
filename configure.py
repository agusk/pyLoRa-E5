##!/usr/bin/env python3

import serial
import time
import io
import argparse
import configparser


parser = argparse.ArgumentParser(description='Configure LoRa-E5')
parser.add_argument('port', help="Serial port of LoRa-E5")
parser.add_argument('config', help="Configuration File")
parser.add_argument('--debug', '-d', help="Print debug output", action='store_const', const=True, default=False)

args = parser.parse_args()

config = configparser.ConfigParser()
config.read(args.config)

ser = serial.Serial(args.port, baudrate=9600)


# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()

# import pdb; pdb.set_trace()
def send_cmd(cmd):
    if args.debug:
        print(cmd)
    ser.write(("%s"% cmd).encode("UTF-8"))
    time.sleep(.2)

def get_var(cmd):
    send_cmd(cmd)
    var = ser.readline().strip().decode("UTF8")
    if args.debug:
        print(var)
    return var

def set_confirm(cmd):
    res = get_var(cmd)
    if args.debug:
        print(res)

    if res != "ok":
        raise Exception("Error in command: %s\r\n Response: %s" % (cmd, res))

send_cmd('AT+VER')
verinfo = ser.readline().decode("UTF-8")

config_channels = config.items('channels')
auth_method = config.get('mac', 'auth')

print(verinfo.strip())
print('Auth Method: %s' % auth_method)

if auth_method == 'otaa':
    print('Configuring otaa')
    set_confirm('AT+ID= AppEui,%s' % config.get('otaa', 'appeui'))
    set_confirm('AT+KEY=APPKEY,%s' % config.get('otaa', 'appkey'))
    set_confirm('AT+ID=DevEui,%s' % config.get('otaa', 'deveui'))
elif auth_method == 'abp':
    print('Configuring apb')
    set_confirm('AT+ID=DevAddr,%s' % config.get('abp', 'devaddr'))
    set_confirm('AT+KEY=NWKSKEY,%s' % config.get('abp', 'nwkskey'))
    set_confrim('AT+KEY=APPSKEY,%s' % config.get('abp', 'appskey'))
else:
    raise Exception('Invaoid auth method %s' % auth_method)

adr_on = config.get('mac', 'adr')
print('ADR: %s' % adr_on)
set_confirm('AT+ADR=%s' % config.get('mac', 'adr'))

print("Configuring Channels:")
ch_count = len(config_channels)
i = 0

def update_progress():
    global i
    i = i + 1
    printProgressBar(i, ch_count, "Channels")
    if args.debug:
        print() # extra newline for progress bar

for config_entry in config_channels:
    config_fields = config_entry[1].split(',')
    ch_id = int(config_entry[0].replace("ch", "").strip())

    ch_freq = get_var('mac get ch freq %d' % ch_id)
    config_freq = config_fields[0].replace('"', '').strip()
    if config_freq == '':
        update_progress()
        continue
        if args.debug:
            print("Blank frequency on channel %d, skipping" % ch_id)

    if(len(config_fields) >= 4):
        config_drrange = "%d %d" % (int(config_fields[2]), int(config_fields[3]))
        set_confirm('mac set ch drrange %d %s' % (ch_id, config_drrange))

    if(len(config_fields) >= 5):
        config_dcycle = int(config_fields[4])
        set_confirm('mac set ch dcycle %d %d' % (ch_id, config_dcycle))

    # US SKU has 72 fixed freq channels
    # EU version has only 16 channels, but freq is user configurable on ch 3-15
    if sku == "RN2903":
        if config_freq != ch_freq:
            raise Exception("Frequency %s for channel %s is does not match device." % (config_freq, ch_id))
    else:
        if ch_id < 3:
            if config_freq != ch_freq:
                raise Exception("Frequency %s for channel %s is does not match device." % (config_freq, ch_id))
        else:
            set_confirm('mac set ch freq %d %s' % (ch_id, config_freq))

    config_status = config_fields[1].replace('"', '').strip()
    set_confirm('mac set ch status %d %s' % (ch_id, config_status))
    update_progress()

print("Saving settings")
set_confirm('mac save')