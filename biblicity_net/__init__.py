
import os
from bl.config import Config
from bsql.database import Database

config = Config(os.path.join(os.path.dirname(__file__), "__config__.ini"))
db = Database(**config.Database)