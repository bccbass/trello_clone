from datetime import date, timedelta
from os import environ

from flask import Flask
# from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
# from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity



from init import db, ma, bcrypt, jwt
from models.user import User, UserSchema
from blueprints.cli_bp import db_commands
from blueprints.auth_bp import auth_bp
from blueprints.cards_bp import cards_bp


load_dotenv()
# print(environ)

# install flask-marshmallow and marshmallow-sqlalchemy




# pip install: flask, flask-sqlalchemy, sqlalchemy, psycopg2-binary

# When setting up new database create a new user for the app 
# CREATE USER <user> WITH PASSWORD <password>;
# and give them
# correct permissions: 
# grant all privileges on database <database_name> to <username>;

# print(app.config)
# Set database connection path giving database type and adapter, then path and user/password local host port
# Setting database connection string - this is a universal format URI for connecting to any database and must be in this configuration.
# Databse+adapter://<user>:<password>@<host name>:port/<database>

# Create instance of flask app
app = Flask(__name__)
# After installing python-dotenv and importing environ from os
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')
# JWT secret key
app.config['JWT_SECRET_KEY'] = environ.get('JWT_KEY')


app.register_blueprint(db_commands)
app.register_blueprint(auth_bp)
app.register_blueprint(cards_bp)

# passes each object the 'app' instance
db.init_app(app)
ma.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)



    # error handler to to return json message (for admin_required function):
@app.errorhandler(401)
def unauthorized(err):
    return {'error': 'You must be an admin'}, 401

















if __name__ == '__main__':
    app.run(port=8000, debug=True)