
import json, logging, sys, traceback
from bl.dict import Dict, StringDict
from bl.url import URL
from biblicity.models.user import User
from .handler import Handler

log = logging.getLogger()
log.setLevel(logging.DEBUG)

class UserHandler(Handler):
    "shared initialization for users"

class UserSignup(UserHandler):
    def get(c, user=None, form_errors=None):
        """The user and form_errors keywords are useful for redisplaying the form after POST"""
        if user is None: user = StringDict(**User(c.db))    # this allows None values to be ''
        plans = c.db.select("""
            select id, price::varchar, projects
            from plans 
            where projects <= 25 and period=1 and price > 0 
            order by projects""")
        c.render('user/signup.xhtml', plans=plans, user=user, form_errors=form_errors)

    def post(c):
        try:
            # everything in a single database transaction
            cursor = c.db.cursor()
            # Create the bookgenesis user
            user = User(c.db).select_one(email=c.get_argument('user_email'), cursor=cursor)
            if user is None:
                # Register new user
                log.info("Register new user:", c.get_argument('user_email'))
                user = User(c.db, 
                            email=c.get_argument('user_email'), 
                            password=c.get_argument('user_password'))
                registration_errors = user.register(cursor=cursor)
                if registration_errors is not None:
                    raise ValueError(
                        "Registration failed for " + user.email + ': ' 
                        + ' '.join(registration_errors))
            else:
                # Authenticate existing user
                log.info("Authenticate existing user:", c.get_argument('user_email'))
                u = user.authenticate(user.email, c.get_argument('user_password'))
                if u is None:
                    # The user did not authenticate -- perhaps forgot password? Miskeyed?
                    raise ValueError("Sorry, we don’t recognize that email and password combination.")

            user.name = c.get_argument('user_name')

            # Create the user account with the chosen subscription plan
            account = Account.create(c.db, c.get_argument('user_site'), 
                        cursor=cursor, **c.config.Accounts)
            log.info("Created account:", account)
            account.add_user(user, cursor=cursor)
            log.info("Added user to account")

            plan = Plan(c.db).select_one(id=c.get_argument('account_plan'))
            log.info("Selected plan:", plan)
            subscription = Subscription(c.db,
                account_id=account.id,
                plan_id=plan.id)
            subscription.expires = subscription.expiration_date()
            subscription.insert(cursor=cursor)
            log.info("Added subscription:", subscription)

            # Create the Stripe customer and subscription if CC authorized
            if c.get_argument('stripe_token', default=None) is not None:
                stripe.api_key = c.config.Stripe.secret_key
                stripe_token = c.get_argument('stripe_token', default=None)
                user.stripe_id = stripe.Customer.create(
                    source=stripe_token,
                    email=user.email,
                    description=user.name,
                ).get('id')
                log.info("Added stripe_id to user")

            user.commit(cursor=cursor)
            cursor.connection.commit()
            cursor.close

            log.info("Signup completed successfully, redirecting to", account.url)

            # log the user in
            c.session['email'] = user.email
            c.save_session()

            # redirect to the user's new account
            url = URL(account.url, qargs={'session': c.session.id})
            c.redirect(str(url))

        except:
            cursor.connection.rollback()
            cursor.close()

            # -- redisplay form with error message(s)
            c.get(user=user, form_errors=sys.exc_info()[1])

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

