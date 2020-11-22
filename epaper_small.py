#!/usr/bin/python3
# -*- coding:utf-8 -*-

import logging
import time
import requests
import random

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd1in54b_V2

API_URL = 'http://pi.hole/admin/api.php'
# TOKEN = os.environ.get('PIHOLE_TOKEN')
TOKEN = ''  # TOKEN not needed
HEADERS = {'Authorization': f'Token {TOKEN}'}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    filename='/var/log/pihole-stats/pihole-stats.log')

# get the font here: https://www.fontspring.com/fonts/typodermic/monofonto
try:
    # My laptop
    font_mono = ImageFont.truetype('fonts/monofonto.ttf', 24)
    font_debug = ImageFont.truetype('/usr/share/fonts/TTF/DejaVuSansMono.ttf', 16)
except OSError:
    # Raspbian
    font_mono = ImageFont.truetype('/home/pi/pihole-stats/fonts/monofonto.ttf', 24)
    font_debug = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 16)

try:
    logging.info("epd1in54b_V2 PiHole monitor")

    epd = epd1in54b_V2.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    HEIGHT = epd.height
    WIDTH = epd.width
    # HEIGHT = 200
    # WIDTH = 200

    text_x = 10
    data_x = 115
    graph_size = 20
    graph_height = 75
    graph_width = 180
    graph_spacing = graph_width // graph_size
    graph_rect = (0, 95, WIDTH - 1, HEIGHT - (95 - graph_height))
    refresh = (65, HEIGHT - 20)

    block_text = ('YEETed', 'Banned', 'Denied', 'PiHoled', 'BALEETED', 'Blocked')

    logging.info(f'Fetching API data')
    try:
        r = requests.get(API_URL, headers=HEADERS)
        data = r.json()
        domains_blocked = int(data['domains_being_blocked']) // 1000
        dns_queries = int(data['dns_queries_today']) // 1000
        ads_blocked = data['ads_blocked_today']
        ads_percent = data['ads_percentage_today']
    except KeyError as e:
        logging.error(e)
        domains_blocked = 'e'
        dns_queries = 'e'
        ads_blocked = 'e'
        ads_percent = 'e'
    logging.debug('Fetching overTimeData')
    try:
        r = requests.get(f'{API_URL}?overTimeData10mins', headers=HEADERS)
        data = r.json()
        domains_over_time = data['domains_over_time']
        ads_over_time = data['ads_over_time']
    except KeyError as e:
        logging.error(e)
        domains_over_time = []
        ads_over_time = []
    logging.debug('Data retrieved')

    logging.info("Drawing image...")
    black_image = Image.new('1', (HEIGHT, WIDTH), 255)  # 255: clear the frame
    red_image = Image.new('1', (HEIGHT, WIDTH), 255)  # 255: clear the frame

    black_draw = ImageDraw.Draw(black_image)
    red_draw = ImageDraw.Draw(red_image)

    black_draw.rectangle([(0, 0), (WIDTH - 1, HEIGHT - 1)], outline=0)  # Screen outline

    black_draw.text((text_x, 5),
                    'Domains:',
                    font=font_mono, fill=0)
    red_draw.text((data_x, 5),
                  f'{domains_blocked}k',
                  font=font_mono, fill=0)

    black_draw.text((text_x, 25),
                    'Queries:',
                    font=font_mono, fill=0)
    red_draw.text((data_x, 25),
                  f'{dns_queries}k',
                  font=font_mono, fill=0)

    black_draw.text((text_x, 45),
                    f'{random.choice(block_text)}:',
                    font=font_mono, fill=0)
    red_draw.text((data_x, 45),
                  f'{ads_blocked}',
                  font=font_mono, fill=0)

    black_draw.text((text_x, 65),
                    'Percent:',
                    font=font_mono, fill=0)
    red_draw.text((data_x, 65),
                  f'{ads_percent:.1f}%',
                  font=font_mono, fill=0)

    black_draw.rectangle([(graph_rect[0], graph_rect[1]), (graph_rect[2], graph_rect[3])], outline=0)

    black_draw.text((refresh[0], refresh[1]),
                    '↻: ',
                    font=font_debug, fill=0)
    red_draw.text((refresh[0] + 20, refresh[1]),
                  f'{time.strftime("%H:%M:%S", time.localtime())}',
                  font=font_debug, fill=0)

    logging.debug("Creating Graph")
    x = graph_width + int((WIDTH - graph_width) / 2)
    y = graph_rect[1] + 5
    trimmed_times = list(reversed(list(ads_over_time)))[-graph_size:]
    _max_d = max(domains_over_time[t] for t in trimmed_times)
    logging.debug(f'{_max_d}')
    for k in trimmed_times:
        x -= graph_spacing
        ads = ads_over_time[k]
        domains = domains_over_time[k]
        pct = int((ads / domains) * 100)
        pct /= 100  # Normalize to 2 sig digits

        h1 = graph_height - (graph_height * pct)

        x1 = x + 2
        x2 = x + graph_spacing - 2
        adj_start = graph_height * (1 - domains_over_time[k] / _max_d)
        adj_end = graph_height - (graph_height * pct) * (domains_over_time[k] / _max_d)

        logging.debug(f'{domains}, {ads}, {pct}, {adj_end}')

        black_y = (adj_start, adj_end)
        red_y = (black_y[1], graph_height)

        black_draw.rectangle([(x1, y + black_y[0]), (x2, y + black_y[1])], fill=0)
        red_draw.rectangle([(x1, y + red_y[0]), (x2, y + red_y[1])], fill=0)

    logging.debug("Display Image")
    epd.display(epd.getbuffer(black_image.rotate(90)), epd.getbuffer(red_image.rotate(90)))
    # black_image.show()
    # red_image.show()

    # logging.info("Clear...")
    # epd.init(epd.FULL_UPDATE)
    # epd.Clear(0xFF)

    logging.info("Sleep...")
    epd.sleep()
    epd.Dev_exit()

except IOError as e:
    logging.debug('IOError')
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd1in54b_V2.epdconfig.module_exit()
    exit()
