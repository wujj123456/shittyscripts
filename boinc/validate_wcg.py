#!/usr/bin/env python3

import json
import gzip
import sys
import argparse
from pprint import pprint

TXT_FILE = 'worldcommunitygrid.txt'
GZ_FILE = 'worldcommunitygrid.txt.gz'

def get_txt_data(filename):
    data = dict(json.load(open(filename)))
    print('Results read from {}: {}'.format(TXT_FILE, len(data)))
    return data

def get_gz_data(filename):
    with gzip.open(filename) as f:
        gzdata = f.read().decode()
        data = dict(json.loads(gzdata))
        print('Results read from disk {}: {}'.format(GZ_FILE, len(data)))
        return data

def flattern_dict(d):
    flat = []
    for k, v in d.items():
        flat.append((k, tuple(sorted([(kk, vv) for kk, vv in v.items()]))))
    return tuple(flat)

def parse_args(args):
    parser = argparse.ArgumentParser(description='Compare WCG stat data files')
    parser.add_argument('--txt', metavar='TXT', default=TXT_FILE)
    parser.add_argument('--gz', metavar='GZ', default=GZ_FILE)
    return parser.parse_args(args)

def main(argv):
    args = parse_args(sys.argv[1:])
    txt = set(flattern_dict(get_txt_data(args.txt)))
    gz = set(flattern_dict(get_gz_data(args.gz)))
    if txt == gz:
        print("OK")
        return 0
    else:
        print("Mismatch")
        print("=== TXT - GZ ===")
        pprint(txt - gz)
        print("=== GZ - TXT ===")
        pprint(gz - txt)
        return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
