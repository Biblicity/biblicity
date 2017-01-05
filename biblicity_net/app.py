
import logging
from bweb.application import Application
from bweb.patterns import Patterns
from tornado.web import url
from tornado.ioloop import IOLoop
from biblicity_net import config, db
from tornado.web import StaticFileHandler
from biblicity_net.handlers.template import *
from biblicity_net.handlers.user import *
from biblicity_net.handlers.item import *

log = logging.getLogger(__name__)

routes = [
    # == Static Content == 
    url(r"^/static/(.*)", StaticFileHandler, {'path': config.Tornado.static_path}),
    url(r"/(favicon\.ico)", StaticFileHandler, {'path': config.Tornado.static_path}),

    # # == User Management == 
    url(r"^/user/?signup/?" % Patterns, UserSignup),
    url(r"^/user/?login/?" % Patterns, UserLogin),
    url(r"^/user/?logout/?" % Patterns, UserLogout),
    
    # # == Users == 
    # url(r"^/user/?" % Patterns, UserIndex),
    # url(r"^/user/?(?P<id>%(slug)s)/edit/?" % Patterns, UserEdit),
    # url(r"^/user/?(?P<id>%(slug)s)/follow/?" % Patterns, UserFollow),
    # url(r"^/user/?(?P<id>%(slug)s)/unfollow/?" % Patterns, UserUnfollow),
    # url(r"^/user/?(?P<id>%(slug)s)/block/?" % Patterns, UserBlock),
    # url(r"^/user/?(?P<id>%(slug)s)/unblock/?" % Patterns, UserUnblock),
    url(r"^/user/(?P<id>%(slug)s)/?(?:%(slug)s)?" % Patterns, UserView),    # user name slug can appear at end of url, ignored


    # # == Items == 
    # url(r"^/items/new" % Patterns, ItemNew),
    # url(r"^/items/(?P<id>%(slug)s)/edit" % Patterns, ItemEdit),
    # # url(r"^/items/(?P<id>%(slug)s)/copy" % Patterns, ItemCopy),
    # url(r"^/items/(?P<id>%(slug)s)/?(?:%(slug)s)?" % Patterns, ItemView),   # title slug can appear at end of url, ignored

    # == Templates in the site == 
    url(r"^(?P<path>%(path)s)" % Patterns, Template),
]

application = Application(
    routes, db=db, config=config, **config.Tornado
)

if __name__ == "__main__":
    application.listen(config.Site.port)
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s %(name)s %(lineno)s:\n\t%(message)s', 
        level=logging.DEBUG)
    logging.info(config.Site.url + ': serving at ' + config.Site.url)
    IOLoop.instance().start()
