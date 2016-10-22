
import logging
from bweb.application import Application
from bweb.patterns import Patterns
from tornado.web import url
from tornado.ioloop import IOLoop
from biblicity import config, db
from biblicity.handlers import template
from biblicity.handlers.user import *

log = logging.getLogger(__name__)

routes = [
    # == User Management == 
    # (r"^/user/?" % Patterns, UserView),
    url(r"^/user/?signup/?" % Patterns, UserSignup),
    url(r"^/user/?login/?" % Patterns, UserLogin),
    url(r"^/user/?logout/?" % Patterns, UserLogout),

    # == Templates in the site == 
    url(r"^(?P<path>%(path)s)" % Patterns, template.Template),
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
