
from datetime import timedelta

from flask import request, Blueprint, abort
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity

from init import db, bcrypt
from models.user import User, UserSchema

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/users')
def all_users():
    stmt = db.select(User)
    users = db.session.scalars(stmt)
    return UserSchema(many=True).dump(users)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        # auth_bpending .json to request allows access to parsed json body from post request
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



@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        stmt = db.select(User).filter_by(email=request.json['email'])
        # stmt = db.select(User).where(User.email==request.json['email'])
        user = db.session.scalar(stmt)
        if user and bcrypt.check_password_hash(user.password, request.json['password']):
            token = create_access_token(identity=user.id, expires_delta=timedelta(days=1))
            return {'token': token, 'user': UserSchema(exclude=['password']).dump(user)}
        else:
            return {'error': 'Invalid password or email address provided'}, 401
    except KeyError:
        return {'error': 'Email and password are required'}, 401
    

def admin_required():
    # function assumes jwt is valid
    # retrieve users email from bearer token
    user_id = get_jwt_identity()
    # query db for user
    stmt = db.select(User).filter_by(email=user_email)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin):
        # in order exit from all local scope use abort()
        abort(401) 

def admin_or_owner_required(owner_id):
    # function assumes jwt is valid
    # retrieve users email from bearer token
    user_id = get_jwt_identity()
    # query db for user
    stmt = db.select(User).filter_by(email=user_email)
    user = db.session.scalar(stmt)
    if not (user and user.is_admin or user_id == owner_id):
        # in order exit from all local scope use abort()
        abort(401) 