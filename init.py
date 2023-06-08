
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


# create an instance of SQLAlchemy and pass in Flask app instance as argument to link the two together and open connectionn to DB.
db = SQLAlchemy()
# print(db.__dict__)
# create instance of Marshmallow and pass App instance (flask)
ma = Marshmallow()
# create instance of Bcrypt and pass in app
bcrypt = Bcrypt()
# create instance of JWT manageer
jwt = JWTManager()

