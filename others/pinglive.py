#!/usr/bin/env python3

import socket
import os
import time

hostname = socket.gethostname()
with open(hostname, 'w') as f:
    f.write(time.strftime('%d %b %Y %H:%M:%S', time.localtime()))
