
from biblicity.models.item import Item
from .handler import Handler

class ItemView(Handler):
    def get(c, id):
        item = Item(c.db).select_one(id=id)
        if item is None:
            c.write_error(404)
        else:
            c.render("item/view.xhtml", item=item)

