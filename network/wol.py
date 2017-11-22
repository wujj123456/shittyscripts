#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import argparse

from wakeonlan import wol
# F8.0F.41.7C.F6.E4
# F8.0F.41.7C.F6.CC

parser = argparse.ArgumentParser(
    description='Wake one or more computers using the wake on lan protocol')
parser.add_argument(
    'macs', metavar='mac addresses', nargs='+',
    help='The mac addresses or of the computers you are trying to wake. e.g. F8.0F.41.7C.F6.E4')
parser.add_argument(
    '-i', metavar='ip', default=wol.BROADCAST_IP,
    help='The ip address of the host to send the magic packet to. (default {})'
    .format(wol.BROADCAST_IP))
parser.add_argument(
    '-p', metavar='port', default=wol.DEFAULT_PORT,
    help='The port of the host to send the magic packet to (default 9)')
args = parser.parse_args()
wol.send_magic_packet(*args.macs, ip_address=args.i, port=args.p)
