
import json, uuid
import datetime
import bleach
from markdown import markdown
from bl.string import String
from bl.dict import Dict
import bsql.model

class Item(bsql.model.Model):
    relation = 'items'
    pk = ['id']

    def before_insert_or_update(self):
        """items are not updated per se -- a new version is always created, linked to the previous."""
        # make sure we have a valid user
        from .user import User
        assert self.user_email is not None
        user = User(self.db).select_one(email=self.user_email)

        # create a new id and link to the previous version
        if self.id is not None:
            self.previous_id = self.id
        self.created = datetime.datetime.now()
        self.id = str(uuid.uuid5(uuid.UUID(user.id), str(self.created))).replace('-', '')

        # scrub the title, reference, version, and body
        self.title = bleach.clean(self.title or '')
        self.bref = bleach.clean(self.bref or '')
        self.bversion = bleach.clean(self.bversion or '')
        self.body = bleach.clean(self.body or '')

        # cache the history in the item itself
        history = self.history or []
        history_entry = {
            'id': self.id, 
            'created': str(self.created),
            'title': self.title, 
            'bref': self.bref,
            'bversion': self.bversion,
            'user':{k:user[k] for k in ['id', 'email', 'name']}}
        history.append(history_entry)
        self.history = json.dumps(history)

    def after_select(self):
        self.history = [Dict(**h) for h in self.history]

    def after_insert(self):
        self.history = [Dict(**h) for h in self.history]

    def commit(self, cursor=None, **args):
        self.insert(cursor=cursor, **args)

    @property
    def title_with_bref(self):
        s = self.title
        if self.bref not in [None, '']:
            s += " (%s)" % self.bref
        return s

    @property
    def id_slash_title(self):
        return "%s/%s" % (self.id, String(self.title or '').hyphenify())

    @property
    def body_html(self):
        return markdown(self.body)

    @property
    def user(self):
        from .user import User
        return self.to_one(User)

    @property
    def previous(self):
        return self.to_one(Item, foreign_key=['previous_id'])