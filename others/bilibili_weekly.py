#!/usr/bin/env python3

from PIL import Image
import subprocess
import os
import argparse
import re
import sys


TEMP_FILE='temp.png'
OUTPUT_FILE='links.html'
LINK_TEMPLATE=r'<br><a href="https://www.bilibili.com/video/{av}/">https://www.bilibili.com/video/{av}/</a></br>'


def frac_crop(img, x=38/1920, y=850/1080, w=318/1920, h=900/1080):
    width = img.size[0]
    height = img.size[1]
    return img.crop((int(x * width), int(y * height),
                     int(w * width), int(h * height)))


def ocr(img):
    img.save(TEMP_FILE)
    text = subprocess.check_output(['gocr', TEMP_FILE])
    text = text.decode().replace(' ', '').replace('l', '1').replace('O', '0').strip()
    return text


def process_image(filename):
    return ocr(frac_crop(Image.open(filename)))


def parse_args(args):
    parser = argparse.ArgumentParser(description='bilibili weekly')
    parser.add_argument('folder', help='Directory of screenshots')
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    links = []
    for root, dirs, files in os.walk(args.folder):
        for name in files:
            if not name.lower().endswith('png'):
                continue
            av = process_image(os.path.join(root, name))
            if not re.match(r'\s*av\d+', av):
                print('Failed to parse file {}'.format(name))
                continue
            links.append(LINK_TEMPLATE.format(av=av))

    with open(os.path.join(args.folder, OUTPUT_FILE), 'w') as f:
        f.write('\n'.join(links))

    if os.path.isfile(TEMP_FILE):
        os.remove(TEMP_FILE)


if __name__ == '__main__':
    sys.exit(main())
