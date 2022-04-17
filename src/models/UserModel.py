import datetime
from marshmallow import fields, Schema
from . import db, bcrypt
from models.BlackListTokensModel import BlackListTokensModel


class UserModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fname = db.Column(db.String(128), nullable=False)
    lname = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"User<id={self.id}, name={self.fname} {self.lname}, email={self.email}>"

    @classmethod
    def get_all(cls):
        results = []
        for result in cls.query.all():
            _ = result.__dict__.pop("password")
            results.append(result.__dict__)

        return results

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
            # print(f"Verifying User Password<{self.password}> with input<{password}>")
            return (bcrypt.check_password_hash(self.password, password), "ok")
        except Exception as e:
            return (False, e)

    def update(self, data):
        for key, item in data.items():
            if key == "password":
                self.password = self.generate_hash(item)
            setattr(self, key, item)
        self.modified_at = datetime.datetime.utcnow()
        db.session.commit()


class UserSchema(Schema):
    id = fields.Integer()
    fname = fields.String()
    lname = fields.String()
    email = fields.Email()
    # password = fields.String()
    created_at = fields.DateTime()
    modified_at = fields.DateTime()
