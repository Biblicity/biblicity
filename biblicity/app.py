
import logging
from bweb.application import Application
from bweb.patterns import Patterns
from tornado.web import url
from tornado.ioloop import IOLoop
from biblicity import config, db
from tornado.web import StaticFileHandler
from biblicity.handlers.template import *
from biblicity.handlers.user import *
from biblicity.handlers.item import *

log = logging.getLogger(__name__)

routes = [
    # == Static Content == 
    url(r"^/static/(.*)", StaticFileHandler, {'path': config.Tornado.static_path}),
    url(r"/(favicon\.ico)", StaticFileHandler, {'path': config.Tornado.static_path}),

    # == User Management == 
    url(r"^/user/?signup/?" % Patterns, UserSignup),
    url(r"^/user/?login/?" % Patterns, UserLogin),
    url(r"^/user/?logout/?" % Patterns, UserLogout),
    
    # == Users == 
    url(r"^/users/(?P<id>%(slug)s)" % Patterns, UserView),
    # url(r"^/users/?(?P<id>%(slug)s)?/edit/?" % Patterns, UserEdit),

    # == Items == 
    url(r"^/items/new" % Patterns, ItemNew),
    url(r"^/items/(?P<id>%(slug)s)/edit" % Patterns, ItemEdit),
    url(r"^/items/(?P<id>%(slug)s)/?(?:%(slug)s)?" % Patterns, ItemView),   # title slug can appear at end of url, ignored

    # == Templates in the site == 
    url(r"^(?P<path>%(path)s)" % Patterns, Template),
]

application = Application(
    routes, db=db, config=config, **config.Tornado
)

if __name__ == "__main__":
    application.listen(config.Site.port)
    loghandler = logging.StreamHandler()
    log.addHandler(loghandler)
    log.setLevel(logging.INFO)
    log.info(config.Site.url + ': serving at ' + config.Site.url)
    IOLoop.instance().start()
