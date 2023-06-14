from datetime import date
from flask import Blueprint, abort, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required

from init import db
from models.comment import Comment, CommentSchema
from blueprints.auth_bp import admin_required, admin_or_owner_required
from flask_jwt_extended import get_jwt_identity


comments_bp = Blueprint('comments', __name__, url_prefix='/comments/')

#   *READ*
# GET ALL comments
@comments_bp.route('/')
# verifies signature on the token
@jwt_required()
def all_comments():
    # select * from comments
    # ordered by desc id
    stmt = db.select(Comment)
    # scalars executes statement. all converts scalar object to list
    comments = db.session.scalars(stmt).all()  
    # Marshmallow statement to convert to python data type. Creates Comment schema call dump on schema instance with passed in comments obj
    return CommentSchema(many=True).dump(comments)

# GET ONE Comment
@comments_bp.route("/<int:comment_id>")
@jwt_required()
def get_comment(comment_id):
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    if comment:
        return CommentSchema().dump(comment)
    else:
        return {'error': 'resource not found'}, 404
    
# CREATE NEW comment
@comments_bp.route("/", methods=["POST"])
@jwt_required()
def create_comment():
    #  Load incoming post data via the Schema 
    comment_info = CommentSchema().load(request.json)
    #  Create a new comment instance from comment_info
    comment = Comment(
        title = comment_info['title'],
        description = comment_info['description'],
        status = comment_info['status'],
        date_created = date.today(),
        user_id = get_jwt_identity()
    )
    # Add and commit the new comment to the session
    db.session.add(comment)
    db.session.commit()
    comment_info = CommentSchema().load(request.json)
    if comment:
        title = comment_info['title'],
        description = comment_info['description'],
        status = comment_info['status'],
        return CommentSchema().dump(comment)
    else:
        return {'error': 'comment not found'}, 404


#  UPDATE A comment
@comments_bp.route('/<int:comment_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_comment(comment_id):
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    db.session.add(comment)
    db.session.commit()
    comment_info = CommentSchema().load(request.json)
    if comment:
        admin_or_owner_required(comment.user.id)

        # Use get method to locate key value or provide default if not found
        comment.title = comment_info.get('title', comment.title)
        comment.description = comment_info.get('description', comment.description)
        comment.status = comment_info.get('status', comment.status)
        db.session.commit()
        return CommentSchema().dump(comment)
    else:
        return {'error': 'comment not found'}, 404
    
# DELETE A comment
@comments_bp.route("/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    stmt = db.select(Comment).filter_by(id=comment_id)
    comment = db.session.scalar(stmt)
    if comment:
        admin_or_owner_required(comment.user.id)

        db.session.delete(comment)
        db.session.commit()
        return {}, 200
    else:
        return {'error': 'resource not found'}, 404