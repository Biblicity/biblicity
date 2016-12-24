
import bsql.model

class UserRelationship(bsql.model.Model):
    pk = ['user_email', 'other_email']
    relation = 'users_relationships'