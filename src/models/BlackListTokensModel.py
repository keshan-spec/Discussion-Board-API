import datetime
from marshmallow import fields, Schema
from . import db


class BlackListTokensModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String(255), nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"BlackListToken<id={self.id}, token={self.token}, blacklisted_on={self.blacklisted_on}>"

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def is_token_blacklisted(cls, token):
        return True if cls.query.filter_by(token=token).first() != None else False

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete_old_records():
        # # delete the recorrd if date is older than 24 hours
        # if self.blacklisted_on < datetime.datetime.utcnow() - datetime.timedelta(minutes=30):
        #     db.session.delete(self)
        #     db.session.commit()
        # delete all records older than 24 hours
        expiry = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)
        db.session.query(BlackListTokensModel).filter(BlackListTokensModel.blacklisted_on < expiry).delete()
        db.session.commit()

class BlackListTokensSchema(Schema):
    id = fields.Integer()
    blacklisted_on = fields.DateTime()
    token = fields.String()
