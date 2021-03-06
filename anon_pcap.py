#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
anon_pcap.py - Mini python script to replace specified value in PCAP file.

Copyright(C) 2016 Yoshiyuki Kurauchi
License: MIT (https://github.com/wmnsk/anon_pcap/blob/master/MIT.md)
Latest version is available on GitHub(https://github.com/wmnsk/anon_pcap).
'''

import argparse
import binascii

def validate_args(v, a):
    '''Check the length of each argment in pairs. (Need better error handling...)'''
    if v is None and a is None:
        print 'ERROR: No replace argument specified. Quitting.'
        quit(-1)
    if v is not None:
        for x in v:
            if len(x[0]) != len(x[1]):
                print 'ERROR: Value to be replaced should be the same in length.'
                print '%s\t : %d' % (x[0], len(x[0]))
                print '%s\t : %d' % (x[1], len(x[1]))
                quit(-1)
            else:
                pass

    if a is not None:
        for x in a:
            if len(x[0]) != len(x[1]):
                print 'ERROR: Value to be replaced should be the same in length.'
                print '%s\t : %d' % (x[0], len(x[0]))
                print '%s\t : %d' % (x[1], len(x[1]))
                quit(-1)
            else:
                pass

parser = argparse.ArgumentParser(description='Mini python script to replace specified value in PCAP(or any binary) file.')
parser.add_argument('-s', '--srcpcap', help='Path to the raw PCAP file to be anonymized.', required=True)
parser.add_argument('-d', '--dstpcap', help='Filename of the anonymized PCAP file.', default='anonymized.pcap')
parser.add_argument('-v', '--strvals', help='A pair of values before/after anonymized in STRING format.', metavar='STRVAL', nargs=2, action='append')
parser.add_argument('-x', '--hexvals', help='A pair of values before/after anonymized in HEX format.', metavar='HEXVAL', nargs=2, action='append')
args = parser.parse_args()

src_pcap  = args.srcpcap
dst_pcap  = args.dstpcap
str_pairs = args.strvals
hex_pairs = args.hexvals

class PcapData():
    'Main class for PCAP to be handled.'
    def __init__(self, srcpath, dstpath):
        self.dstfile = open(dstpath, 'w')
        self.pcap_bin = self.file2bin(srcpath)
        self.pcap_hex = self.bin2hex(self.pcap_bin)

    def file2bin(self, path):
        ''' read pcap file as binary. '''
        with open(path, 'rb') as d:
            bindata = d.read()
        return bindata

    def bin2hex(self, bindata):
        ''' convert binary into hexadecimal. '''
        hexdata = binascii.hexlify(bindata)
        return hexdata

    def str2hex(self, strdata):
        ''' convert string into hexadecimal. '''
        hexdata = binascii.hexlify(strdata)
        return hexdata

    def swap_str(self, strdata, fill):
        ''' swap argument string by two characters(for the legacy protocols like SS7). '''
        if len(strdata) % 2 == 1:
            strdata = strdata + fill
        swapped = ''.join(map(lambda x: x[::-1], [strdata[i: i+2] for i in range(0, len(strdata), 2)])) # python magic!
        return swapped

    def replace_strval(self, strargs):
        ''' replace value with string-formatted argument(-v). '''
        for l in strargs:
            if self.str2hex(l[0]) not in self.pcap_hex:
                self.pcap_hex = self.pcap_hex.replace(self.swap_str(l[0], 'f'), self.swap_str(l[1], l[1][-1]))
                self.pcap_hex = self.pcap_hex.replace(self.swap_str(l[0], '0'), self.swap_str(l[1], l[1][-1]))
                print 'Replaced "%s" as "%s"' % (l[0], l[1])
            else:
                self.pcap_hex = self.pcap_hex.replace(self.str2hex(l[0]), self.str2hex(l[1]))
                print 'Replaced "%s" as "%s"' % (l[0], l[1])
        return self.pcap_hex

    def replace_hexval(self, hexargs):
        ''' replace value with hex-formatted argument(-x). '''
        for l in hexargs:
            self.pcap_hex = self.pcap_hex.replace(l[0], l[1])
            print 'Replaced "%s" as "%s"' % (l[0], l[1])
        return self.pcap_hex

    def write_pcap(self, hexdata):
        ''' write modified data as binary(pcap) file. '''
        self.dstfile.write(bytearray.fromhex(hexdata))
        self.dstfile.close()

def main():
    validate_args(str_pairs, hex_pairs)
    p = PcapData(src_pcap, dst_pcap)
    if str_pairs is not None:
        r = p.replace_strval(str_pairs)
    if hex_pairs is not None:
        r = p.replace_hexval(hex_pairs)
    p.write_pcap(r)

if __name__ == '__main__':
    main()
