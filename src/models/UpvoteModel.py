from marshmallow import fields, Schema
from . import db


class UpvoteModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    liked_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "user_model.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    post_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "post_model.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user = db.relationship("UserModel")
    post = db.relationship("PostModel")

    def __repr__(self):
        return f"Upvote<id={self.id}>"

    def get_upvote_count(post_id):
        return UpvoteModel.query.filter_by(post_id=post_id).count()

    def get_upvotes(post_id):
        upvotes = UpvoteModel.query.filter_by(post_id=post_id).all()
        return [upvote.liked_by for upvote in upvotes]

    def upvote_post(post_id, user_id):
        existing_upvote = UpvoteModel.user_has_upvoted(post_id, user_id)
        if existing_upvote:
            db.session.delete(existing_upvote)
        else:
            existing_upvote = UpvoteModel(post_id=post_id, liked_by=user_id)
            db.session.add(existing_upvote)

        db.session.commit()
        return UpvoteModel.get_upvote_count(post_id)

    def user_has_upvoted(post_id, user_id):
        upvote = UpvoteModel.query.filter_by(post_id=post_id, liked_by=user_id).first()
        if upvote:
            return upvote
        return False


class CommentUpvoteModel(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    liked_by = db.Column(
        db.Integer,
        db.ForeignKey(
            "user_model.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    comment_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "reply_model.id",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    user = db.relationship("UserModel")
    comment = db.relationship("ReplyModel")

    def __repr__(self):
        return f"CommentUpvote<id={self.id}>"

    def get_upvote_count(comment_id):
        return CommentUpvoteModel.query.filter_by(comment_id=comment_id).count()

    def get_upvotes(comment_id):
        upvotes = CommentUpvoteModel.query.filter_by(comment_id=comment_id).all()
        return [upvote.liked_by for upvote in upvotes]

    def upvote_comment(comment_id, user_id):
        existing_upvote = CommentUpvoteModel.user_has_upvoted(comment_id, user_id)
        if existing_upvote:
            db.session.delete(existing_upvote)
        else:
            existing_upvote = CommentUpvoteModel(
                comment_id=comment_id, liked_by=user_id
            )
            db.session.add(existing_upvote)

        db.session.commit()
        return CommentUpvoteModel.get_upvote_count(comment_id)

    def user_has_upvoted(comment_id, user_id):
        upvote = CommentUpvoteModel.query.filter_by(
            comment_id=comment_id, liked_by=user_id
        ).first()
        if upvote:
            return upvote
        return False


class UpvoteSchema(Schema):
    id = fields.Integer()
    liked_by = fields.Integer()
    post_id = fields.Integer()


class CommentUpvoteSchema(Schema):
    id = fields.Integer()
    liked_by = fields.Integer()
    comment_id = fields.Integer()
