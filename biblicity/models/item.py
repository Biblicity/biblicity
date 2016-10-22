
import json, uuid
import datetime
from bl.dict import Dict
import bsql.model

class Item(bsql.model.Model):
    relation = 'items'
    pk = ['id']

    def before_insert_or_update(self):
        """items are not updated per se -- a new version is always created, linked to the previous."""
        from .user import User
        assert self.user_email is not None
        user = User(self.db).select_one(email=self.user_email)

        if self.id is not None:
            self.previous_id = self.id
        self.created = datetime.datetime.now()
        self.id = str(uuid.uuid5(uuid.UUID(user.id), str(self.created)))

        # cache the history in the item itself
        history = self.history or []
        history.append({k:str(self.get(k)) for k in ['id', 'user_email', 'created']})
        self.history = json.dumps(history)

    def after_select(self):
        self.history = [Dict(**h) for h in self.history]

    def after_insert(self):
        self.history = [Dict(**h) for h in self.history]

    def commit(self, cursor=None, **args):
        self.insert(cursor=cursor, **args)

    @property
    def user(self):
        from .user import User
        return self.to_one(User)

    @property
    def previous(self):
        return self.to_one(Item, foreign_key=['previous_id'])