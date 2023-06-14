from init import db, ma
from marshmallow import fields

# MODELS AREA
class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))
    description = db.Column(db.Text())
    status = db.Column(db.String(30))
    date_created = db.Column(db.Date())

    # CREATE Foreign key association
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    user = db.relationship('User', back_populates='cards')
 

# Marshmallow shema
class CardSchema(ma.Schema):
    #  tell Marshmallow to use UserSchema to serialize the 'user' field below
    user = fields.Nested('UserSchema', exclude=['password', 'cards'])

    class Meta:
        fields = ('id', 'title', 'description', 'status', 'date_created', 'user')
        ordered = True