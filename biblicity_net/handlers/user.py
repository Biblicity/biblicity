
import json, logging, sys, traceback
from bl.dict import Dict, StringDict
from bl.url import URL
from biblicity_net.models.user import User
from bweb.handler import require_login
from .handler import Handler

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class UserHandler(Handler):
    "shared initialization for user"
    def initialize(c):
        super().initialize()
        c.user = User(c.db).select_one(email=c.session.get('email'))

class UserSignup(UserHandler):
    def get(c, user=None, form_errors=None):
        """The user and form_errors keywords are useful for redisplaying the form after POST"""
        user = user or User(c.db)
        c.render('user/signup.xhtml', user=user, form_errors=form_errors)

    def post(c):
        try:
            # everything in a single database transaction
            cursor = c.db.cursor()
            # Create the user
            user = User(c.db).select_one(email=c.get_argument('user_email'), cursor=cursor)
            if user is None:
                # Register new user
                user = User(c.db, 
                        email=c.get_argument('user_email'), 
                        password=c.get_argument('user_password'),
                        name=c.get_argument('user_name'),
                        bio=c.get_argument('user_bio'))
                agreed = c.get_argument('user_agreed', default='')
                if False and agreed.lower() not in ['on', 'true', '1']:
                    raise ValueError("You must agree to the terms of service to register.")
                else:
                    log.info("Register new user: %s" % c.get_argument('user_email'))
                    user.agreed = True
                    registration_errors = user.register(cursor=cursor)
                    if registration_errors is not None:
                        raise ValueError(
                            "Registration failed for " + user.email + ': ' 
                            + ' '.join(registration_errors))
            else:
                # Authenticate existing user
                log.info("Authenticate existing user: %s" % c.get_argument('user_email'))
                user = User(c.db).authenticate(user.email, c.get_argument('user_password'))
                if user is None:
                    # The user did not authenticate -- perhaps forgot password? Miskeyed?
                    raise ValueError("Sorry, we don’t recognize that email and password combination.")

            cursor.connection.commit()
            cursor.close

            # log the user in
            c.session['email'] = user.email
            c.session['user_id'] = user.id
            c.session['user_name'] = user.name
            c.save_session()

            # redirect to the user's new account
            # url = '/'.join([c.config.Site.url, 'user', user.id_slash_name])
            # log.info("Signup completed successfully, redirecting to %s" % url)
            # c.redirect(str(url))

            c.render('user/signup-completed.xhtml')

        except:
            cursor.connection.rollback()
            cursor.close()

            # -- redisplay form with error message(s)
            c.messages.error = str(sys.exc_info()[1])
            c.get(user=user)

            # -- log the error
            log.info("ERROR:", traceback.format_exc())

            c.write_error(500)

            # -- send an error email to the dev team to see what needs to be done, if anything 
            

class UserLogin(UserHandler):
    def get(c, user=None):
        if user is None: 
            user = User(c.db)
        log.debug("session = " + str(c.session))
        if c.session.get('email') is not None:  # the user is already logged in
            c.messages.notice = """You’re already logged in as %s, but you’re welcome 
                                to log in with a different user account""" % c.session.get('email')
        c.render("user/login.xhtml", user=user)

    def post(c):
        user = User(c.db).authenticate(
                c.get_argument('user_email', default=None),
                c.get_argument('user_password', default=None),
                unverified=True)                                # Don't require email verification
        if user is None:
            c.messages.error = "Sorry, we don’t recognize that email and password combination."
            c.get()
        else:
            c.session['email'] = user.email
            c.session['user_id'] = user.id
            c.session['user_name'] = user.name
            c.session.save()
            if c.get_argument('return', default=None) not in [None, '']:
                c.redirect(c.get_argument('return'))
            else:
                c.redirect(c.config.Site.url + '/user/' + user.id_slash_name)

class UserLogout(UserHandler):
    def get(c):
        c.reset_session()
        c.redirect(c.config.Site.url)

class UserIndex(UserHandler):
    @require_login
    def get(c):
        # omit blocked users from the user list
        users = User(c.db).select(
            where="""
                email not in (
                    select rel.other_email from users_relationships rel
                    where rel.user_email=%s
                    and kind='blocking')""",
            vals=[c.user.email],
            orderby="registered")
        c.render("user/index.xhtml", users=users)

class UserView(UserHandler):
    def get(c, id):
        user = User(c.db).select_one(id=id)
        if user is None:
            c.write_error(404)
        else:
            c.render("user/view.xhtml", user=user)

class UserEdit(UserHandler):
    @require_login
    def get(c, id):
        user = User(c.db).select_one(id=id)
        if user.email != c.session.get('email'):
            c.write_error(403)
        else:
            c.render("user/edit.xhtml", user=user)

    @require_login
    def post(c, id):
        user = User(c.db).select_one(id=id)
        if user.email != c.session.get('email'):
            c.write_error(403)
        else:
            user.update(
                name=c.get_argument('user_name', default=''),
                email=c.get_argument('user_email'),
                bio=c.get_argument('user_bio'))
            try:
                if c.get_argument("user_password", default='').strip() != '':
                    log.debug("password = " + c.get_argument('user_password'))
                    user.set_password(c.get_argument('user_password'))
                user.commit()
                c.redirect(c.config.Site.url + '/user/'+ user.id_slash_name)
            except:
                c.messages.error = str(sys.exc_info()[1])
                c.render("user/edit.xhtml", user=user)
                
class UserFollow(UserHandler):
    @require_login
    def get(c, id):
        other= User(c.db).select_one(id=id)
        if other.email in [o.email for o in c.user.following]:
            c.session['messages'].error = "You are already following %s" % other.name
        else:
            try:
                c.user.follow(other.email)
                c.session['messages'].notice = "You are now following %s" % other.name
            except:
                c.session['messages'].error = str(sys.exc_info()[1])
        if c.get_argument('return', default=None) is not None:
            c.redirect(c.get_argument('return'))
        else:
            c.redirect(c.config.Site.url+'/user/'+other.id)

class UserUnfollow(UserHandler):
    @require_login
    def get(c, id):
        other= User(c.db).select_one(id=id)
        if other.email not in [o.email for o in c.user.following]:
            c.session['messages'].error = "You are already not following %s" % other.name
        else:
            try:
                c.user.unfollow(other.email)
                c.session['messages'].notice = "You are no longer following %s" % other.name
            except:
                c.session['messages'].error = str(sys.exc_info()[1])
        if c.get_argument('return', default=None) is not None:
            c.redirect(c.get_argument('return'))
        else:
            c.redirect(c.config.Site.url+'/user/'+other.id)

class UserBlock(UserHandler):
    @require_login
    def get(c, id):
        other= User(c.db).select_one(id=id)
        if other.email in [o.email for o in c.user.blocking]:
            c.session['messages'].error = "You are already blocking %s" % other.name
        else:
            try:
                c.user.block(other.email)
                c.session['messages'].notice = "You are now blocking %s" % other.name
            except:
                c.session['messages'].error = str(sys.exc_info()[1])
        if c.get_argument('return', default=None) is not None:
            c.redirect(c.get_argument('return'))
        else:
            c.redirect(c.config.Site.url+'/user/'+other.id)

class UserUnblock(UserHandler):
    @require_login
    def get(c, id):
        other= User(c.db).select_one(id=id)
        if other.email not in [o.email for o in c.user.blocking]:
            c.session['messages'].error = "You are already not blocking %s" % other.name
        else:
            try:
                c.user.unblock(other.email)
                c.session['messages'].notice = "You are no longer blocking %s" % other.name
            except:
                c.session['messages'].error = str(sys.exc_info()[1])
        if c.get_argument('return', default=None) is not None:
            c.redirect(c.get_argument('return'))
        else:
            c.redirect(c.config.Site.url+'/user/'+other.id)

