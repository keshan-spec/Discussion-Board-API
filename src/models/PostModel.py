import datetime
from marshmallow import fields, Schema
from sqlalchemy import exists, true
from models.UserModel import UserModel, UserSchema
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

    @staticmethod
    def get_post(post_id):
        # get post by id with user info
        post = PostModel.query.filter_by(id=post_id).first()
        if not post:
            return None

        user = UserModel.query.filter_by(id=post.user_id).first()
        user = PostModel.get_author(user)
        post = PostSchema().dump(post)

        return {**post, "author":user}
    
    # get user info
    @staticmethod
    def get_author(user):
        user = UserSchema().dump(user)

        return {"handle": user.get("handle"), "id": user.get("id")}

    @staticmethod
    def paginate_posts(page, limit):
        # join by user_id to get users and paginate
        return PostModel.query.join(UserModel, PostModel.user_id == UserModel.id).paginate(page, limit, False)

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

    def upvote_post(post_id, user_id):
        existing_upvote = UpvoteModel.user_has_upvoted(post_id, user_id)
        if existing_upvote:
            db.session.delete(existing_upvote)
        else:
            upvote = UpvoteModel(post_id=post_id, liked_by=user_id)
            db.session.add(upvote)
    
        db.session.commit()
        return existing_upvote

    def user_has_upvoted(post_id, user_id):
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
        self.items = pagination.items
        self.make_urls(pagination, url)
        self.make_posts()
        
    def make_posts(self):
        posts = []
        for item in self.items:
            author = PostModel.get_author(item.user)
            post = PostSchema().dump(item)
            posts.append({**post, "author":author})

        self.items = posts
    def make_urls(self, pagination, url):
        if self.has_next:
            self.next_page = f"{url}?start={pagination.next_num}&limit={self.limit}"
        if self.has_prev:
            self.prev_page = f"{url}?start={pagination.prev_num}&limit={self.limit}"

    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return ('limit','page', 'pages', 'total', 'has_prev', 'next_page', 'has_next', 'items','prev_page')