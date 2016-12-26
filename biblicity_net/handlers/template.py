
import logging, os, sys, traceback
from .handler import Handler

log = logging.getLogger(__name__)

class Template(Handler):
    def get(c, path):
        """look for the template at [path+'.xhtml', path+'/index.html']"""
        path = path.strip('/')
        log.debug("path=%r" % path)
        template_path = '/'.join([c.settings.get('template_path'), path])
        log.debug('template_path=%r' % template_path)
        if os.path.exists(template_path+'.xhtml'):
            c.render(path+'.xhtml')
        elif os.path.exists(template_path+'/index.xhtml'):
            c.render('/'.join([path, 'index.xhtml']).strip('/'))
        else:
            c.write_error(404)
        