from sqlalchemy.ext.automap import automap_base
from flask_login import UserMixin

Base = automap_base()


class User(Base, UserMixin):
    __tablename__ = "users"

    def get_id(self):
        return self.user_id
