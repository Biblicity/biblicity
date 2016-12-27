"""
Each day, pull the reading for the day from the source API and save it for use.
"""

import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

import os, re, sys, json
from datetime import datetime
from lxml import etree
from tornado.httpclient import HTTPClient
from bl.text import Text
from bxml import XML
from biblicity_net import config

VERSIONS = ['ESV', 'NLT', 'NLTUK', 'NTV', 'KJV']
SAVE_PATH = os.path.join(config.Tornado.template_path, 'today-2017')

with open(os.path.splitext(__file__)[0]+'.json') as f:
    readings = json.loads(f.read())

date = datetime.now().strftime("%B %d")
reading = readings.get(date) or ""

httpclient = HTTPClient()

if reading != "":
    for version in VERSIONS:
        url = config.OtherAPI[version.lower()] + reading
        log.info(url)
        text = httpclient.fetch(url).body.decode('utf-8')
        text = text.replace("&nbsp;", "&#x00a0;")
        html = XML(root=text)
        div = html.root.xpath("//div")[0]
        tfn = os.path.join(SAVE_PATH, version+'.html')
        t = Text(fn=tfn, text=etree.tounicode(div))
        t.write()
