from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# print(app.config)
# Set database connection path giving database type and adapter, then path and user/password local host port
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://trello_dev:spameggs123@localhost:5432/trello'

db = SQLAlchemy(app)
# print(db.__dict__)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    date_created = db.Column(db.Date())


@app.cli.command('create')
def create():
    db.create_all()
    print('tables created successfully')

@app.route('/')

def index():
    return '<p> Hello world!</p>'

if __name__ == '__main__':
    app.run(debug=True)