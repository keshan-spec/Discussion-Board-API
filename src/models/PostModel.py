import datetime
from marshmallow import fields, Schema

from . import db

class PostModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    contains_profanity = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    user = db.relationship('UserModel')

    def __repr__(self):
        return f"Post<id={self.id}>"

    def get_post(self, post_id):
        return PostModel.query.filter_by(id=post_id).first()

    @staticmethod
    def paginate_posts(page, limit):
        return PostModel.query.paginate(page, limit, False)

    @classmethod
    def get_all(cls):
        return list(cls.query.all())

    def add(self):
        db.session.add(self)
        db.session.commit()

class UpvoteModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    liked_by = db.Column(db.Integer, db.ForeignKey('user_model.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post_model.id'), nullable=False)

    user = db.relationship('UserModel')
    post = db.relationship('PostModel')

    def __repr__(self):
        return f"Upvote<id={self.id}>"

    def upvote_post(self, post_id, user_id):
        upvote = self.user_has_upvoted(post_id, user_id)
        if upvote:
            db.session.delete(upvote)

        else:
            upvote = UpvoteModel(post_id=post_id, liked_by=self.liked_by)
            db.session.add(upvote)
    
        db.session.commit()
        return upvote

    def user_has_upvoted(self, post_id, user_id):
        upvote = UpvoteModel.query.filter_by(post_id=post_id, liked_by=user_id).first()
        if upvote:
            return upvote
        return False

class PostSchema(Schema):
    id = fields.Integer()
    text = fields.String()
    created_on = fields.DateTime()
    contains_profanity = fields.Boolean()
    

class UpvoteSchema(Schema):
    id = fields.Integer()
    liked_by = fields.Integer()
    post_id = fields.Integer()


class Pagination:
    def __init__(self, pagination, url):
        self.limit = pagination.per_page
        self.page = pagination.page
        self.pages = pagination.pages
        self.total = pagination.total
        self.has_prev = pagination.has_prev
        self.has_next = pagination.has_next
        self.items = PostSchema(many=True).dump(pagination.items)
        self.make_urls(pagination, url)

    def make_urls(self, pagination, url):
        if self.has_next:
            self.next_page = f"{url}?start={pagination.next_num}&limit={self.limit}"
        if self.has_prev:
            self.prev_page = f"{url}?start={pagination.prev_num}&limit={self.limit}"

    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return ('limit','page', 'pages', 'total', 'has_prev', 'next_page', 'has_next', 'items','prev_page')