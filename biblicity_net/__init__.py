
import os
from bl.config import Config
from bsql.database import Database

PATH = os.path.dirname(os.path.normpath(__file__))
config = Config(os.path.join(PATH, "__config__.ini"))
db = Database(**config.Database)
