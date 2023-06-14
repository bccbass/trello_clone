from init import db, ma
from marshmallow import fields

# MODELS AREA
class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.Text())
    date_created = db.Column(db.Date())

    # CREATE Foreign key association
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', back_populates='comments')
 
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id', ondelete='cascade'), nullable=False)
    card = db.relationship('Card', back_populates='comments')
 
    

# Marshmallow shema
class CommentSchema(ma.Schema):
    #  tell Marshmallow to use UserSchema to serialize the 'user' field below
    user = fields.Nested('UserSchema', only=['name', 'email'])
    card = fields.Nested('CardSchema', only=['title', 'description', 'status'])

    class Meta:
        fields = ('id', 'message', 'date_created', 'user', 'card')
        ordered = True