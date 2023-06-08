from datetime import date, timedelta
from os import environ

from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv

load_dotenv()
# print(environ)

# install flask-marshmallow and marshmallow-sqlalchemy

app = Flask(__name__)


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

# After installing python-dotenv and importing environ from os
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URI')
# JWT secret key
app.config['JWT_SECRET_KEY'] = environ.get('JWT_KEY')
# create an instance of SQLAlchemy and pass in Flask app instance as argument to link the two together and open connectionn to DB.
db = SQLAlchemy(app)
# print(db.__dict__)
# create instance of Marshmallow and pass App instance (flask)
ma = Marshmallow(app)
# create instance of Bcrypt and pass in app
bcrypt = Bcrypt(app)
# create instance of JWT manageer
jwt = JWTManager(app)

def admin_required():
    # function assumes jwt is valid
    # retrieve users email from bearer token
    user_email = get_jwt_identity()
    # query db for user
    stmt = db.select(User).filter_by(email=user_email)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin):
        # in order exit from all local scope use abort()
        abort(401) 

    # error handler to to return json message:
@app.errorhandler(401)
def unauthorized(err):
    return {'error': 'You must be an admin'}, 401


# MODELS AREA
class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    status = db.Column(db.String(30))
    date_created = db.Column(db.Date())

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    # create user role:
    is_admin = db.Column(db.Boolean, default=False)


# Marshmallow shema
class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'status', 'date_created')

class UserSchema(ma.Schema):
    class Meta:
        fields = ('name', 'email', 'password', 'is_admin')


# ROUTES AREA
@app.route('/')
def index():
    return '<p> Hello world!</p>'

@app.route('/login', methods=['POST'])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json['email'])
        # stmt = db.select(User).where(User.email==request.json['email'])
        user = db.session.scalar(stmt)
        if user and bcrypt.check_password_hash(user.password, request.json['password']):
            token = create_access_token(identity=user.email, expires_delta=timedelta(days=1))
            return {'token': token, 'user': UserSchema(exclude=['password']).dump(user)}
        else:
            return {'error': 'Invalid password or email address provided'}, 401
    except KeyError:
        return {'error': 'Email and password are required'}, 401


@app.route('/cards')
# verifies signature on the token
@jwt_required()
def all_cards():

    admin_required()
    # select * from cards
    # ordered by desc id
    stmt = db.select(Card).order_by(Card.status.desc())
    # scalars executes statement. all converts scalar object to list
    cards = db.session.scalars(stmt).all()  
    # Marshmallow statement to convert to python data type. Creates Card schema call dump on schema instance with passed in cards obj
    return CardSchema(many=True).dump(cards)

@app.route('/register', methods=['POST'])
def register():
    try:
        # appending .json to request allows access to parsed json body from post request
        # print(request.json)
        # Parse, sanitize, and validate incoming json
        # via the schema
        user_info = UserSchema().load(request.json)
        # create a new User model instance with schema data user_info
        user = User(
            email=user_info['email'],
            password=bcrypt.generate_password_hash(user_info['password']).decode('utf-8'),
            name = user_info['name']
        )
        # add to session
        db.session.add(user)
        # commit to session
        db.session.commit()
        # return new user, excluding password
        return UserSchema(exclude=['password']).dump(user), 201 
    except IntegrityError:
        return {'error': 'email address already in use'}, 409
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

# CLI COMMAND AREA
@app.cli.command('one_card') 
def one_card():
    # select * from cards
    # you can limit the stmt results using .limit(number to see)
    # this returns a list of the number of cards you want to see
    # This is best practice because it will stop search when first result is found, and cease searching
    # add db.or_ for or queries
    # stmt = db.select(Card).where(db.or_(Card.status != 'Done', Card.id > 2))
    # 'and' is default. See above for or statements
    stmt = db.select(Card).where(Card.status != 'Done', Card.id > 2).order_by(Card.id.desc())
    cards = db.session.scalars(stmt).all()
    for card in cards:
        print(card.__dict__)

# @app.cli.command('one_card') 
# def one_card():
#     # select * from cards
#     # you can limit the stmt results using .limit(number to see)
#     # this returns a list of the number of cards you want to see
#     # This is best practice because it will stop search when first result is found, and cease searching
#     # add db.or_ for or queries
#     # stmt = db.select(Card).where(db.or_(Card.status != 'Done', Card.id > 2))
#     # 'and' is default. See above for or statements
#     stmt = db.select(Card).where(Card.status != 'Done', Card.id > 2).order_by(Card.id.desc())
#     cards = db.session.scalars(stmt).all()
#     for card in cards:
#         print(card.__dict__)


@app.cli.command('create')
def create():
    db.drop_all()
    db.create_all()
    print('tables created successfully')
    
@app.cli.command('seed')
def seed_db():

    users = [
        User(
        name='Guy Luxe',
        email='admin@example.com',
        # generate pw hash then decode to base64
        password=bcrypt.generate_password_hash('spiny').decode('utf-8'),
        is_admin=True
        ),
        User(
        name='John Clease',
        email='spam@example.com',
        password=bcrypt.generate_password_hash('tisbutascratch').decode('utf-8'),

        )
    ]

    # Create an instance of the card model in memory
    cards = [
        Card(
            title = 'Start the project',
            description = 'Create an ERD',
            status = 'Done',
            date_created = date.today()
        ),
        Card(
            title = 'ORM Queries',
            description = 'Stage 2',
            status = 'In progress',
            date_created = date.today()
        ),
        Card(
            title = 'Marshmallow',
            description = 'Stage 3',
            status = 'In progress',
            date_created = date.today()
        )
    ]
    # Truncate the Card table
    db.session.query(Card).delete()
    db.session.query(User).delete()

    # Add card to the session (transaction)
    db.session.add_all(cards)
    db.session.add_all(users)
    # commit the transaction to the database
    db.session.commit()
    print('models seeded')



if __name__ == '__main__':
    app.run(port=8000, debug=True)