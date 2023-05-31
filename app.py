from datetime import date 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# When settinput up new database create a new user for the app and give them
# correct permissions: grant all privileges on database <database_name> to <username>;
# print(app.config)
# Set database connection path giving database type and adapter, then path and user/password local host port
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:spameggs123@localhost:5432/trello'

db = SQLAlchemy(app)
# print(db.__dict__)

class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    date_created = db.Column(db.Date())


@app.cli.command('create')
def create():
    db.drop_all()
    db.create_all()
    print('tables created successfully')
    
@app.cli.command('seed')
def seed_db():
    # Create an instance of the card model in memory
    card = Card(
        title = 'Start the project',
        description = 'Create an ERD',
        date_created = date.today()
    )

    # Truncate the Card table
    db.session.query(Card).delete()

    # Add card to the session (transaction)
    db.session.add(card)
    # commit the transaction to the database
    db.session.commit()
    print('models seeded')

@app.route('/')

def index():
    return '<p> Hello world!</p>'

if __name__ == '__main__':
    app.run(debug=True)