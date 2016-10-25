
import uuid
from datetime import datetime
import bleach
from bl.string import String
import bweb.models.user

class User(bweb.models.user.User):
    
    def before_insert(self):
        """create the id for the user from their email address when their account is created.
        This id stays constant in the system, even if their email changes.
        """
        assert self.email is not None
        self.id = str(uuid.uuid5(uuid.NAMESPACE_URL, self.email)).replace('-', '')
        if self.name is None or self.name.strip()=='':
            self.name = self.email.split('@')[0].strip()
        self.name = bleach.clean(self.name)
        self.bio = bleach.clean(self.bio, tags=bleach.ALLOWED_TAGS+['p','br'])
        self.registered = datetime.now()
        self.verified = self.registered

    def items(self, update=True, orderby='created desc', **kwargs):
        from .item import Item
        return self.to_many(Item, update=update, orderby=orderby, **kwargs)

    @property
    def id_slash_name(self):
        return "%s/%s" % (self.id, String(self.name).hyphenify())

    @property
    def following(self):
        return self.db.select("""
            select other.*, rel.created as rel_created 
            from users other
            inner join users_relationships rel
                on rel.other_email = other.email
            inner join users
                on rel.user_email = users.email
            where users.email=%s
            and kind='following'
            order by created desc
            """, vals=[self.email], Record=User)

    def follow(self, other_email, cursor=None):
        from .user_relationship import UserRelationship
        rel = UserRelationship(self.db, user_email=self.email, other_email=other_email, kind='following')
        rel.insert(cursor=cursor)

    def unfollow(self, other_email, cursor=None):
        from .user_relationship import UserRelationship
        rel = UserRelationship(self.db).select_one(user_email=self.email, other_email=other_email, kind='following')
        rel.delete(cursor=cursor)

    @property
    def blocking(self):
        return self.db.select("""
            select other.*, rel.created as rel_created
            from users other
            inner join users_relationships rel
                on rel.other_email = other.email
            inner join users
                on rel.user_email = users.email
            where users.email=%s
            and kind='blocking'
            order by created
            """, vals=[self.email], Record=User)

    def block(self, other_email, cursor=None):
        from .user_relationship import UserRelationship
        rel = UserRelationship(self.db, user_email=self.email, other_email=other_email, kind='blocking')
        rel.insert(cursor=cursor)

    def unblock(self, other_email, cursor=None):
        from .user_relationship import UserRelationship
        rel = UserRelationship(self.db).select_one(user_email=self.email, other_email=other_email, kind='blocking')
        rel.delete(cursor=cursor)
