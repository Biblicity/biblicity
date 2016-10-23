
import uuid
from datetime import datetime
import bweb.models.user

class User(bweb.models.user.User):
    
    def before_insert(self):
        """create the id for the user from their email address when their account is created.
        This id stays constant in the system, even if their email changes.
        """
        assert self.email is not None
        self.id = str(uuid.uuid5(uuid.NAMESPACE_URL, self.email))
        if self.name is None or self.name.strip()=='':
            self.name = self.email.split('@')[0].strip()
        self.registered = datetime.now()
        self.verified = self.registered

    def items(self, update=True, orderby='created desc', **kwargs):
        from .item import Item
        return self.to_many(Item, update=update, orderby=orderby, **kwargs)