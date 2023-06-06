from datetime import date 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

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
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:spameggs123@localhost:5432/trello'

# create an instance of SQLAlchemy and pass in Flask app instance as argument to link the two together and open connectionn to DB.
db = SQLAlchemy(app)
# print(db.__dict__)
# create instance of Marshmallow and pass App instance (flask)
ma = Marshmallow(app)


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
        fields = ('name', 'email', 'is_admin')


# ROUTES AREA
@app.route('/cards') 
def all_cards():
    # select * from cards
    # ordered by desc id
    stmt = db.select(Card).order_by(Card.status.desc())
    # scalars executes statement. all converts scalar object to list
    cards = db.session.scalars(stmt).all()  
    # Marshmallow statement to convert to python data type. Creates Card schema call dump on schema instance with passed in cards obj
    return CardSchema(many=True).dump(cards)

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
        password='spiny',
        is_admin=True
        ),
        User(
        name='John Clease',
        email='spam@example.com',
        password='passwordspam'
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

@app.route('/')

def index():
    return '<p> Hello world!</p>'

if __name__ == '__main__':
    app.run(port=8000, debug=True)