


from flask import Blueprint
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required

from init import db
from models.card import Card, CardSchema
from blueprints.auth_bp import admin_required


cards_bp = Blueprint('cards', __name__)



@cards_bp.route('/cards')
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