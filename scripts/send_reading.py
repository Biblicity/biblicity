import os, re, sys
import emails
from datetime import datetime
from bl.dict import Dict
import tornado.template
from biblicity_net import config

loader=tornado.template.Loader(config.Tornado.template_path)

c = Dict(os=os, datetime=datetime, config=config, static_url=lambda x:config.Module.path+'/static/'+x)
html = loader.load('email/reading.html').generate(c=c, version='NLT').decode('utf-8')

message = emails.Message(html=html, subject='January 11 Biblicity', mail_from='admin@biblicity.net')
message.attach(data=open(c.static_url('img/biblicity_icon.png'),'rb'), filename='biblicity_icon.png', content_disposition='inline')
message.attachments['biblicity_icon.png'].is_inline = True
message.send(to='sah.harrison@gmail.com')
