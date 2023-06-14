from flask import Blueprint
from datetime import date

from init import db, bcrypt
from models.user import User
from models.card import Card
from models.comment import Comment



#  To run cli commands use flask db <action>

db_commands = Blueprint('db', __name__)

# CLI COMMAND AREA
@db_commands.cli.command('one_card')
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

# @db_commands.cli.command('one_card')
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


@db_commands.cli.command('create')
def create():
    db.drop_all()
    db.create_all()
    print('tables created successfully')

@db_commands.cli.command('seed')
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
    db.session.query(User).delete()
    db.session.add_all(users)
    db.session.commit()

    # Create an instance of the card model in memory
    cards = [
        Card(
            title = 'Start the project',
            description = 'Create an ERD',
            status = 'Done',
            date_created = date.today(),
            user = users[0]
        ),
        Card(
            title = 'ORM Queries',
            description = 'Stage 2',
            status = 'In progress',
            date_created = date.today(),
            user = users[0]        
            ),
        Card(
            title = 'Marshmallow',
            description = 'Stage 3',
            status = 'In progress',
            date_created = date.today(),
            user = users[0]
        )
    ]


    db.session.query(Card).delete()
    db.session.add_all(cards)
    db.session.commit()

    comments = [
        Comment(
            message = 'Comment 1',
            date_created = date.today(),
            user = users[0],
            card = cards[1]
        ),
        Comment(
            message = 'Comment 2',
            date_created = date.today(),
            user = users[1],
            card = cards[1]
        ),
        Comment(
            message = 'Comment 3',
            date_created = date.today(),
            user = users[0],
            card = cards[0]
        )
    ]

    db.session.query(Comment).delete()
    db.session.add_all(comments)
    db.session.commit()

    print('models seeded')