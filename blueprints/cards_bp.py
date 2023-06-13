


from datetime import date
from flask import Blueprint, abort, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required

from init import db
from models.card import Card, CardSchema
from blueprints.auth_bp import admin_required


cards_bp = Blueprint('cards', __name__, url_prefix='/cards/')

#   *READ*
# GET ALL CARDS
@cards_bp.route('/')
# verifies signature on the token
@jwt_required()
def all_cards():
    # select * from cards
    # ordered by desc id
    stmt = db.select(Card).order_by(Card.status.desc())
    # scalars executes statement. all converts scalar object to list
    cards = db.session.scalars(stmt).all()  
    # Marshmallow statement to convert to python data type. Creates Card schema call dump on schema instance with passed in cards obj
    return CardSchema(many=True).dump(cards)

# GET ONE CARD
@cards_bp.route("/<int:card_id>")
@jwt_required()
def get_card(card_id):
    admin_required()
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        return CardSchema().dump(card)
    else:
        return {'error': 'resource not found'}, 404
    
# CREATE NEW CARD
@cards_bp.route("/", methods=["POST"])
@jwt_required()
def create_card():
    #  Load incoming post data via the Schema 
    card_info = CardSchema().load(request.json)
    #  Create a new card instance from card_info
    card = Card(
        title = card_info['title'],
        description = card_info['description'],
        status = card_info['status'],
        date_created = date.today()
    )
    # Add and commit the new card to the session
    db.session.add(card)
    db.session.commit()
    card_info = CardSchema().load(request.json)
    if card:
        title = card_info['title'],
        description = card_info['description'],
        status = card_info['status'],
        return CardSchema().dump(card)
    else:
        return {'error': 'card not found'}, 404


#  UPDATE A CARD
@cards_bp.route('/<int:card_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_card(card_id):
    admin_required()
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    db.session.add(card)
    db.session.commit()
    card_info = CardSchema().load(request.json)
    if card:
        # Use get method to locate key value or provide default if not found
        card.title = card_info.get('title', card.title)
        card.description = card_info.get('description', card.description)
        card.status = card_info.get('status', card.status)
        db.session.commit()
        return CardSchema().dump(card)
    else:
        return {'error': 'card not found'}, 404
    
# DELETE A CARD
@cards_bp.route("/<int:card_id>", methods=["DELETE"])
@jwt_required()
def delete_card(card_id):
    admin_required()
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {}, 200
    else:
        return {'error': 'resource not found'}, 404