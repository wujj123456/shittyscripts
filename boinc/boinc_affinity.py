#!/usr/bin/python3

import psutil
import os
import logging
import time
from pprint import pprint

TARGET_CMD = ['/usr/bin/boinc', '--dir', '/var/lib/boinc-client']
BUSY_PCT = 90

logging.basicConfig(format='%(asctime)-15s [%(levelno)s] %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel('DEBUG')

def find_boinc_client():
    for p in psutil.process_iter():
        if p.cmdline() == TARGET_CMD and p.username() == 'boinc':
            LOG.debug('boinc PID: {}'.format(p.pid))
            return p
    raise

def process_is_busy(p):
    # Just assume true for now until I see weird threads
    return True
    if p.cpu_percent(0.1) < BUSY_PCT and p.cpu_percent(1) < BUSY_PCT:
        LOG.info('{} is not busy enough. Skip'.format(p.pid))
        return False
    return True

def get_boinc_workers(boinc):
    busy = []
    for p in boinc.children():
        if process_is_busy(p):
            busy.append(p)
    LOG.debug('Number of workers: {}'.format(len(busy)))
    return busy

def get_current_affinity(workers):
    bindings = list(0 for i in range(os.cpu_count()))
    unaff_workers = list()
    for w in workers:
        aff = w.cpu_affinity()
        if len(aff) != 1:
            unaff_workers.append(w)
        else:
            cpu = aff[0]
            if bindings[cpu]:
                # treat as if it's unbinded
                LOG.warning('PID {} and {} affined to same CPU {}'.format(
                    bindings[cpu], w.pid, cpu))
                unaff_workers.append(w)
            else:
                bindings[cpu] = w.pid
    LOG.info('Initial bindings: {}'.format(bindings))
    LOG.debug('Unbinded workers: {}'.format([w.pid for w in unaff_workers]))
    return bindings, unaff_workers

def set_affinity_helper(proc, affinity, dryrun=False):
    if dryrun:
        return True

    LOG.debug('Binding PID {} to CPU {}'.format(proc.pid, affinity))
    proc.cpu_affinity(affinity)
    if set(proc.cpu_affinity()) != set(affinity):
        LOG.error('Failed to set affine PID {} to CPU {}'.format(
                  proc.pid, affinity))
        return False
    return True

def assign_affinity(bindings, workers):
    for w in workers:
        # find first free CPU
        cpu = next((i for i, v in enumerate(bindings) if not v), None)
        if cpu is None:
            LOG.error('Not enough CPU for workers')
            return
        # bind w to cpu
        if set_affinity_helper(w, [cpu]):
            bindings[cpu] = w.pid
    LOG.info('Final bindings: {}'.format(bindings))

def main():
    boinc = find_boinc_client()
    workers = get_boinc_workers(boinc)
    bindings, workers = get_current_affinity(workers)
    assign_affinity(bindings, workers)

if __name__ == '__main__':
    main()
