
import json, logging, sys, traceback
from bl.dict import Dict, StringDict
from bl.url import URL
from biblicity.models.user import User
from .handler import Handler

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class UserHandler(Handler):
    "shared initialization for user"

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
                agreed = c.get_argument('user_agreed', default='')
                if agreed.lower() not in ['on', 'true', '1']:
                    raise ValueError("You must agree to the terms of service to register.")
                else:
                    log.info("Register new user: %s" % c.get_argument('user_email'))
                    user = User(c.db, 
                                email=c.get_argument('user_email'), 
                                password=c.get_argument('user_password'),
                                name=c.get_argument('user_name'),
                                bio=c.get_argument('user_bio'),
                                agreed=True)
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
            c.save_session()

            # redirect to the user's new account
            url = '/'.join([c.config.Site.url, 'users', user.id])
            log.info("Signup completed successfully, redirecting to %s" % url)
            c.redirect(str(url))

        except:
            cursor.connection.rollback()
            cursor.close()

            # -- redisplay form with error message(s)
            c.messages.error = str(sys.exc_info()[1])
            c.get(user=user)

            # -- log the error
            log.info("ERROR:", traceback.format_exc())

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
                c.get_argument('user_password', default=None))
        if user is None:
            c.messages.error = "Sorry, we don’t recognize that email and password combination."
            c.get()
        else:
            c.session['email'] = user.email
            c.session.save()
            if c.get_argument('return', default=None) not in [None, '']:
                c.redirect(c.get_argument('return'))
            else:
                c.redirect(c.config.Site.url + '/users/' + user.id)

class UserLogout(UserHandler):
    def get(c):
        c.reset_session()
        c.redirect(c.config.Site.url)

