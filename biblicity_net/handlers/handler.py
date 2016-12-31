
import os, re, time, logging
from glob import glob
from bl.dict import Dict
from bl.url import URL
import bweb.handler

log = logging.getLogger(__name__)

class Handler(bweb.handler.Handler):

    # request life cycle

    def initialize(c):
        super().initialize()
        c.db = c.settings.get('db')
        c.init_session()
        if c.session.get('messages') is not None:
            c.messages.update(**c.session.get('messages'))
        c.session['messages'] = Dict()            
        log.debug({'url': str(c.url), 'method': c.request.method, 'handler': c.__class__.__name__})

    def prepare(c):
        c.set_header('Content-Type', 'text/html')       # this is the default

    def on_finish(c):                   # logging
        c.save_session()
#        c.log_request(session=c.session)

    def write_error(c, status_code, **kwargs):
        c.set_status(status_code)
        c.render("http_error.xhtml", status=status_code)

