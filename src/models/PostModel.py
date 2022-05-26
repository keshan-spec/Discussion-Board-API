import datetime
from marshmallow import fields, Schema
from models.UserModel import UserModel, UserSchema
from models.UpvoteModel import UpvoteModel
from models.UpvoteModel import CommentUpvoteModel
from . import db


class PostModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    contains_profanity = db.Column(db.Boolean, default=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    isClosed = db.Column(db.Boolean, default=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "user_model.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user = db.relationship("UserModel")

    def __repr__(self):
        return f"Post<id={self.id}>"

    @staticmethod
    def get_post(post_id, delete=False):
        # get post by id with user info
        post = PostModel.query.filter_by(id=post_id).first()
        if not post:
            return None

        if delete:
            return post

        user = UserModel.query.filter_by(id=post.user_id).first()
        meta = PostModel.get_post_meta(user, post_id, True)
        post = PostSchema().dump(post)
        return {**post, **meta}

    # get user info
    @staticmethod
    def get_post_meta(user, post_id, verbose=False):
        user = UserSchema().dump(user)
        author = {"handle": user.get("handle"), "id": user.get("id")}

        # if getting all posts, there is no need
        # to get the meta data for the post
        # counts should be enough, as it saves time and space
        if not verbose:
            return {
                "author": author,
                "upvote_count": UpvoteModel.get_upvote_count(post_id) or 0,
                "comment_count": ReplyModel.get_reply_count(post_id) or 0,
            }

        # if it is a verbose request, get the replies and upvotes
        # because they are needed for the post to be viewed
        upvotes = UpvoteModel.get_upvote_count(post_id)  # get upvotes
        # upvotes = UpvoteModel.get_upvotes(post_id)  # get upvotes
        comments = ReplyModel.get_comments(post_id)  # get replies

        return {"author": author, "upvotes": upvotes, "comments": comments}

    @staticmethod
    def paginate_posts(page, limit):
        # join by user_id to get users and paginate
        return (
            PostModel.query.join(UserModel, PostModel.user_id == UserModel.id)
            .order_by(PostModel.created_on.asc())
            .paginate(page, limit, False)
        )

    # get a users posts
    @staticmethod
    def get_user_posts(user_id):
        posts = (
            PostModel.query.filter_by(user_id=user_id)
            .order_by(PostModel.created_on.desc())
            .all()
        )
        return posts

    @classmethod
    def get_all(cls):
        return list(cls.query.all())

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def close(self):
        self.isClosed = True
        db.session.commit()


class ReplyModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    contains_profanity = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, nullable=True, default=None)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user_model.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    post_id = db.Column(
        db.Integer,
        db.ForeignKey("post_model.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    user = db.relationship("UserModel")
    post = db.relationship("PostModel")

    def __repr__(self):
        return f"Comment<id={self.id}>"

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        # update comment to [deleted]
        # self.text = "[deleted]"
        # self.contains_profanity = False
        # db.session.commit()

        db.session.delete(self)
        db.session.commit()

    def get_comments(post_id):
        # get replies and filter by parent_id
        comments = ReplyModel.query.filter_by(post_id=post_id).all()
        root_comments = {}

        for comment in comments:
            likes = CommentUpvoteModel.get_upvotes(comment.id)
            if comment.parent_id is None:
                root_comments[comment.id] = {
                    **ReplySchema().dump(comment),
                    **{"likes": likes},
                }
                root_comments[comment.id]["replies"] = []
            elif comment.parent_id:
                if comment.parent_id in root_comments:
                    root_comments[comment.parent_id]["replies"].append(
                        {**ReplySchema().dump(comment), **{"likes": likes}}
                    )
                else:
                    print(f"parent_id {comment.parent_id} not found")
                    ReplyModel.recursive_sub_comment(comment, root_comments)

        comments = []
        for comment in root_comments.values():
            comments.append(comment)
        return comments

    @staticmethod
    def recursive_sub_comment(comment, comments_dict):
        for reply in comments_dict:
            try:
                sub = comments_dict[reply]["replies"]
            except TypeError:
                sub = comments_dict["replies"]

            for sub_comment in sub:
                if sub_comment.get("replies"):
                    ReplyModel.recursive_sub_comment(comment, sub_comment)
                else:
                    if sub_comment["id"] == comment.parent_id:
                        print(sub_comment["id"])
                        likes = CommentUpvoteModel.get_upvotes(sub_comment["id"])
                        if sub_comment.get("replies") is None:
                            print(sub_comment["id"])
                            sub_comment["replies"] = []
                            sub_comment["likes"] = likes

                        sub_comment["replies"].append(
                            {**ReplySchema().dump(comment), **{"likes": likes}}
                        )
                        break

    def get_replies(parent_id):
        replies = ReplyModel.query.filter_by(parent_id=parent_id).all()
        return ReplySchema().dump(replies, many=True)

    def get_reply_count(post_id):
        return ReplyModel.query.filter_by(post_id=post_id).count()

    def get_reply(reply_id):
        reply = ReplyModel.query.filter_by(id=reply_id).first()
        if not reply:
            return None

        return reply


class PostSchema(Schema):
    id = fields.Integer()
    text = fields.String()
    title = fields.String()
    created_on = fields.DateTime()
    contains_profanity = fields.Boolean()
    isClosed = fields.Boolean()


class ReplySchema(Schema):
    id = fields.Integer()
    text = fields.String()
    created_on = fields.DateTime()
    contains_profanity = fields.Boolean()
    user_id = fields.Integer()
    parent_id = fields.Integer()


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
            post = PostSchema().dump(item)
            meta = PostModel.get_post_meta(item.user, post["id"])
            posts.append({**post, **meta})
        self.items = posts

    def make_urls(self, pagination, url):
        if self.has_next:
            self.next_page = f"{url}?start={pagination.next_num}&limit={self.limit}"
        if self.has_prev:
            self.prev_page = f"{url}?start={pagination.prev_num}&limit={self.limit}"

    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return (
            "limit",
            "page",
            "pages",
            "total",
            "has_prev",
            "next_page",
            "has_next",
            "items",
            "prev_page",
        )
