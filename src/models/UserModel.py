import datetime
from marshmallow import fields, Schema
from . import db, bcrypt
from models.BlackListTokensModel import BlackListTokensModel


class UserModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fname = db.Column(db.String(128), nullable=False)
    lname = db.Column(db.String(128), nullable=False)
    handle = db.Column(db.String(128), nullable=False, unique=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"User<id={self.id}, handle={self.handle}, email={self.email}>"

    @classmethod
    def get_all(cls):
        return cls.query.all()

    def find(**kwargs):
        """Return filtered AND query results for passed in kwargs.
        Example:
            # find all instances of MyModel for first name 'John' AND last name 'Doe'
            MyModel.find(first_name='John', last_name='Doe')

        Returns result list or None.
        """
        return UserModel.query.filter_by(**kwargs).all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @staticmethod
    def logout(token):
        print(f"Logging out User<{token}>")
        bl_token = BlackListTokensModel(token=token)
        bl_token.add()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def generate_hash(self, password):
        return bcrypt.generate_password_hash(password, rounds=10).decode("utf-8")

    def check_hash(self, password):
        try:
            valid = bcrypt.check_password_hash(self.password, password)
            if valid:
                return True, None
            else:
                return False, "Password is incorrect"
        except Exception as e:
            return (False, e)

    def update(self, data):
        for key, item in data.items():
            if key == "password":
                # self.password = self.generate_hash(item)
                continue
            setattr(self, key, item)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()

    def update_password(self, old_password, new_password):
        valid, error = self.check_hash(old_password)
        if valid:
            self.password = self.generate_hash(new_password)
            self.modified_at = datetime.datetime.utcnow()
            db.session.commit()
            return True
        else:
            return False


class UserSchema(Schema):
    id = fields.Integer()
    fname = fields.String()
    lname = fields.String()
    handle = fields.String()
    email = fields.Email()
    # password = fields.String()
    created_at = fields.DateTime()
    modified_at = fields.DateTime()
