"""
Each day, pull the reading for the day from the source API and save it for use.
"""

import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

import os, re, sys, json, traceback
from datetime import date
from lxml import etree
from tornado.httpclient import HTTPClient
from bl.text import Text
from bxml import XML
from biblicity_net import config, PATH, readings

VERSIONS = ['ESV', 'NLT', 'NLTUK', 'NTV', 'KJV']
SAVE_PATH = os.path.join(os.path.dirname(PATH), 'var', 'readings')
if not os.path.isdir(SAVE_PATH):
    os.makedirs(SAVE_PATH)

httpclient = HTTPClient()
htmlparser = etree.HTMLParser()

date = date.today()
reading = readings.date_reading(date).replace(' ', '.')
if reading is not None:
    for version in VERSIONS:
        tfn = os.path.join(SAVE_PATH, '%s_%s.html' % (date.strftime("%Y-%m-%d"), version))
        if os.path.exists(tfn):
            os.remove(tfn)
        try:
            url = config.OtherAPI[version.lower()] + reading
            log.info(url)
            text = httpclient.fetch(url).body.decode('utf-8')
            text = text.replace("&nbsp;", "&#x00a0;")
            html = XML(root=etree.fromstring(text, parser=htmlparser))
            div = html.root.xpath("//div")[0]
            h2 = div.xpath("//h2")[0]
            h2.text = h2.text.replace(', '+version, '').strip() + ', '
            link = etree.fromstring("<a class='caps-small' href='%s'>%s</a>" 
                % (config.Site.url+"/about/translations#"+version.lower().replace('uk',''), version))
            h2.insert(0, link)    
            t = Text(fn=tfn, text=etree.tounicode(div))
            t.write()
            log.info(tfn)
        except:
            log.error(traceback.format_exc())
                
