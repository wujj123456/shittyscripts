#!/usr/bin/env python3

import argparse
import calendar
from collections import defaultdict
import gzip
from http.cookiejar import CookieJar
import json
from pprint import pprint
import os
import statistics
import sys
from tabulate import tabulate
import time
from urllib import parse, request


USER = 'wujj123456'
KEY_FILE = '.wcg.key'
PASSWORD_FILE = '~/.wcg.password'
FILE_NAME = 'worldcommunitygrid.txt.gz'
STAT_URL = (
    'https://secure.worldcommunitygrid.org/api/members/{user}/'
    'results?code={key}&ValidateState=1'
)


PROPERTIES = (
    'GrantedCredit',
    'ElapsedTime',
    'DeviceName',
    'ReceivedTime',
    'AppName',
)


class DataMismatch(Exception):
    pass


def base_stat_url():
    with open(os.path.expanduser(KEY_FILE), 'r') as f:
        key = f.readlines()[0].strip()
    return STAT_URL.format(user=USER, key=key)


def wcgtime_to_epoch(time_str):
    return calendar.timegm(time.strptime(time_str, '%Y-%m-%dT%H:%M:%S'))


def format_json_to_dict(web_data):
    data = defaultdict(dict)
    for r in web_data['Results']:
        # only record valid results
        if r['ValidateState'] != 1:
            continue
        for p in PROPERTIES:
            if p == 'ReceivedTime':
                data[r['Name']][p] = wcgtime_to_epoch(r[p])
            elif p == 'ElapsedTime' and float(r[p]) == 0:
                data[r['Name']][p] = r['CpuTime']
            else:
                data[r['Name']][p] = r[p]
    return data


def get_web_data():
    """ The procedure is derived from
    https://www.worldcommunitygrid.org/forums/wcg/viewthread_thread,40823_offset,20#582183

    wget --save-cookies cookies.txt --keep-session-cookies \
        --post-data 'j_username=XYZ&j_password=ABC' --delete-after \
        https://www.worldcommunitygrid.org/j_security_check

    wget --load-cookies cookies.txt <stat url with verification code>
    """
    try:
        # get auth cookie due to GDPR change
        cj = CookieJar()
        with open(os.path.expanduser(PASSWORD_FILE), 'r') as f:
            password = f.readlines()[0].strip()
        data = {
            'j_username': USER,
            'j_password': password,
        }
        login_request = request.Request(
            'https://www.worldcommunitygrid.org/j_security_check',
            parse.urlencode(data).encode('utf-8'),
        )
        opener = request.build_opener(request.HTTPCookieProcessor(cj))
        response = opener.open(login_request)

        data = dict()
        offset = 0
        while True:
            opener = request.build_opener(request.HTTPCookieProcessor(cj))
            url = base_stat_url() + '&limit=1000&offset={}'.format(offset)
            result = opener.open(url).read()
            new_data = dict(json.loads(result.decode('utf-8')))['ResultsStatus']
            data.update(format_json_to_dict(new_data))
            print(
                'Fetch from offset={}. Returned {} results'
                .format(offset, new_data['ResultsReturned'])
            )

            returned = int(new_data['ResultsReturned'])
            available = int(new_data['ResultsAvailable'])
            if offset + returned >= available or not returned:
                break
            offset += returned

        print('Results returned from web: {}'.format(len(data)))
        return data
    except Exception as e:
        print('Failed to fetch web results: {}'.format(e))
        raise
        return None


def get_disk_data():
    try:
        with gzip.open(FILE_NAME) as f:
            gzdata = f.read().decode()
            data = defaultdict(dict, json.loads(gzdata))
            print('Results read from disk: {}'.format(len(data)))
            return data
    except Exception:
        print('Failed to read file from disk')
        return None


def validate_properties(disk, web):
    for p in PROPERTIES:
        if disk[p] != web[p]:
            print('Mismatch: ', p, disk[p], web[p])
            return False
    return True


def update_data_from_web(data, overwrites):
    web_data = get_web_data()
    if not web_data:
        return data

    for app, r in web_data.items():
        if data[app]:
            # verify all information match
            if not validate_properties(data[app], r):
                print('Data mismatch on {}'.format(app))
                print('Stored:')
                pprint(data[app])
                print('Web:')
                pprint(r)
                if overwrites <= 0:
                    raise DataMismatch()
                else:
                    overwrites -= 1
                    data[app] = r
        else:
            # update dict with new data
            data[app] = r
    print('Results combined: {}'.format(len(data)))
    return data


def trim_old_data(data, begin, end):
    if not begin and not end:
        return data
    begin = begin * 3600 * 24
    end = end * 3600 * 24
    cur_time = time.time()
    trimmed = dict()
    for k, v in data.items():
        if end <= cur_time - v['ReceivedTime'] <= begin:
            trimmed[k] = v
    print('Results after trimming: {}'.format(len(trimmed)))
    return trimmed


def save_data_to_disk(data):
    gz = json.dumps(data).encode()
    with gzip.open(FILE_NAME, 'wb') as f:
        f.write(gz)


def analyze_data(data):
    print()
    header = (
        'device',
        'app',
        'avg',
        'stdev',
        'min',
        'max',
        'cnt',
        'hr_avg',
        'hr_dev',
        'pts',
        'days',
    )
    device_stat = defaultdict(lambda : defaultdict(list))
    for v in data.values():
        device_stat[v['DeviceName']][v['AppName']].append(
            (v['GrantedCredit'], v['ElapsedTime'])
        )
    for d, app in sorted(device_stat.items()):
        d = '{:<15}|'.format(d)
        rows = []
        total_credits = 0
        total_time = 0
        total_samples = 0
        all_ratios = []
        for a, v in app.items():
            ratios = [c / t for c,t in v]
            times = [t for c,t in v]
            pts_sum = sum(c for c,t in v)
            time_sum = sum(t for c,t in v)
            rows.append((
                d,
                a,
                '{:.2f}'.format(pts_sum / time_sum),
                '{:.4f}'.format(statistics.pstdev(ratios)),
                '{:.2f}'.format(min(ratios)),
                '{:.2f}'.format(max(ratios)),
                len(v),
                '{:.2f}'.format(statistics.mean(times)),
                '{:.2f}'.format(statistics.pstdev(times)),
                int(pts_sum),
                '{:.2f}'.format(time_sum / 24),
            ))
            total_credits += pts_sum
            total_time += sum(times)
            total_samples += len(v)
            all_ratios += ratios

        summary = (
            d,
            'summary',
            '{:.2f}'.format(total_credits / total_time),
            None,
            None,
            None,
            total_samples,
            '{:.2f}'.format(total_time / total_samples),
            None,
            int(total_credits),
            '{:.1f}'.format(total_time / 24),
        )
        table = [header] + sorted(rows) + [summary]
        print(tabulate(table, headers='firstrow'))
        print()


def parse_args(args):
    parser = argparse.ArgumentParser(description='World Community Grid stats')
    parser.add_argument('-b', '--begin', metavar='BDAY', type=int, default=1,
        help='start analysis from BDAY days ago. Default: 1')
    mxg = parser.add_mutually_exclusive_group()
    mxg.add_argument('-e', '--end', metavar='EDAY', type=int, default=0,
        help='end analysis at EDAY days ago. Default: 0')
    mxg.add_argument('-d', '--days', metavar='DAYS', type=int,
        help='analyze for a period of DAYS. Mutually exclusive with [-e|--end]')
    parser.add_argument('-u', '--update-only', action='store_true',
        help='only update local file with new web data. Skip analysis')
    parser.add_argument('-a', '--analysis-only', action='store_true',
        help='only analyze data on the disk. Skip fetching')
    parser.add_argument('-o', '--overwrites', type=int, default=0,
        help='allow specified number of overwrites if data conflicts')

    args = parser.parse_args(args)
    if args.days:
        args.end = max(0, args.begin - args.days)

    return args


def main():
    args = parse_args(sys.argv[1:])
    data = get_disk_data()
    if not data:
        data = defaultdict(dict)
    if not args.analysis_only:
        data = update_data_from_web(data, args.overwrites)
        save_data_to_disk(data)
    if args.update_only:
        return

    data = trim_old_data(data, args.begin, args.end)
    analyze_data(data)


if __name__ == '__main__':
    sys.exit(main())
