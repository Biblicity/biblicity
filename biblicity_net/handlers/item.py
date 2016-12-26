
from biblicity_net.models.item import Item
from bweb.handler import *
from .handler import Handler

class ItemView(Handler):
    def get(c, id):
        item = Item(c.db).select_one(id=id)
        if item is None:
            c.write_error(404)
        else:
            c.render("items/view.xhtml", item=item)

class ItemNew(Handler):
    
    @require_login
    def get(c):
        item = Item(c.db)
        c.render("items/new.xhtml", item=item)

    @require_login
    def post(c):
        item = Item(c.db,
            user_email=c.session.get('email'),
            title=c.get_argument('item_title', default=''),
            bref=c.get_argument('item_bref', default=''),
            bversion=c.get_argument('item_bversion', default=''),
            body=c.get_argument('item_body', default=''))
        # if c.get_argument('item_agreement', default='false').lower() not in ['on', 'true', '1']:
        #     c.messages.error = "Please agree to the license terms in order to save the item."
        #     c.render("items/new.xhtml", item=item)
        # else:
        item.commit()
        c.redirect(c.config.Site.url + '/items/' + item.id_slash_title)

class ItemEdit(Handler):

    @require_login
    def get(c, id):
        item = Item(c.db).select_one(id=id)
        if item is None:
            c.write_error(404)
        else:
            c.render("items/edit.xhtml", item=item)

    @require_login
    def post(c, id):
        item = Item(c.db).select_one(id=id)
        if item is None:
            c.write_error(404)
        else:
            item.update(
                user_email=c.session.get('email'),
                title=c.get_argument('item_title', default=''),
                bref=c.get_argument('item_bref', default=''),
                bversion=c.get_argument('item_bversion', default=''),
                body=c.get_argument('item_body', default=''))
            # if c.get_argument('item_agreement', default='false').lower() not in ['on', 'true', '1']:
            #     c.messages.error = "Please agree to the license terms in order to save the item."
            #     c.render("items/edit.xhtml", item=item)
            # else:
            item.commit()
            c.redirect(c.config.Site.url + '/items/' + item.id_slash_title)

class ItemCopy(Handler):

    @require_login
    def get(c, id):
        item = Item(c.db).select_one(id=id)
        if item is None:
            c.write_error(404)
        elif item.user_email == c.session.get('email'):
            c.session['messages'].error = "No need to copy your own item, you already have it."
            c.redirect(c.config.Site.url + '/items/' + item.id_slash_title)
        else:
            item.user_email = c.session.get('email')
            item.commit()
            c.session['messages'].notice = "You have copied “%s” to your account." % item.title
            c.redirect(c.config.Site.url + '/items/' + item.id_slash_title)
