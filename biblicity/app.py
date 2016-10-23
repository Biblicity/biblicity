
import logging
from bweb.application import Application
from bweb.patterns import Patterns
from tornado.web import url
from tornado.ioloop import IOLoop
from biblicity import config, db
from biblicity.handlers.template import *
from biblicity.handlers.user import *
from biblicity.handlers.item import *

log = logging.getLogger(__name__)

routes = [
    # == User Management == 
    url(r"^/user/?signup/?" % Patterns, UserSignup),
    url(r"^/user/?login/?" % Patterns, UserLogin),
    url(r"^/user/?logout/?" % Patterns, UserLogout),
    
    # == Users == 
    url(r"^/users/(?P<id>%(slug)s)" % Patterns, UserView),
    # url(r"^/users/?(?P<id>%(slug)s)?/edit/?" % Patterns, UserEdit),

    # == Items == 
    url(r"^/items/(?P<id>%(slug)s)" % Patterns, ItemView),

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
    log.info('serving at ' + config.Site.url)
    IOLoop.instance().start()
