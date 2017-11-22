#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

from wakeonlan import wol
wol.send_magic_packet('F8.0F.41.7C.F6.E4', ip_address=wol.BROADCAST_IP, port=wol.DEFAULT_PORT)
