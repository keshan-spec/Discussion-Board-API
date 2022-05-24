from flask import Blueprint, jsonify, request, session

# models
from models.PostModel import PostModel, ReplyModel, UpvoteModel, Pagination, ReplySchema
from models.UserModel import UserSchema
from decorators import token_required


# create a blueprint
post_bp = Blueprint("post_bp", __name__)

# get post by id
@post_bp.route("/post/<int:id>", methods=["GET"])
@token_required
def get_post(current_user, id):
    post = PostModel.get_post(id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if current_user.profanity_filter:
        if post["contains_profanity"]:
            post["text"] = censor_profanity(post["text"])
            post["title"] = censor_profanity(post["title"])

        if post["comments"]:
            for comment in post["comments"]:
                if comment["contains_profanity"]:
                    comment["text"] = censor_profanity(comment["text"])

    return jsonify(post), 200


# Get all user records
@post_bp.route("/posts", methods=["GET"])
@token_required
def get_paginated_posts(current_user):
    start = int(request.args.get("start", 1))
    limit = int(request.args.get("limit", 5))

    paginated = PostModel.paginate_posts(start, limit)
    # censor profanity if user has profanity filter enabled
    if current_user.profanity_filter:
        for post in paginated.items:
            if post.contains_profanity:
                post.text = censor_profanity(post.text)
                post.title = censor_profanity(post.title)

    pagination = Pagination(paginated, "/posts")
    return jsonify(pagination.__dict__), 200


@post_bp.route("/post", methods=["POST"])
@token_required
def create_post(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    if not data.get("text") or not data.get("title"):
        return jsonify({"message": "No input data provided"}), 400

    # censored_text = censor_profanity(data.get("text"))
    profanity = [
        contains_profanity(data.get("text")),
        contains_profanity(data.get("title")),
    ]
    post = PostModel(
        title=data.get("title"),
        text=data.get("text"),
        user_id=current_user.id,
        contains_profanity=any(profanity),
    )

    post.add()
    return jsonify({"Id": post.id}), 200


# close post
@post_bp.route("/post/<int:id>/close", methods=["PUT"])
@token_required
def close_post(current_user, id):
    post = PostModel.get_post(id, True)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if post.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 401

    post.close()
    return jsonify({"message": "Post closed"}), 200


@post_bp.route("/post/<int:id>", methods=["DELETE"])
@token_required
def delete_post(current_user, id):
    post = PostModel.get_post(id, True)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if post.user_id != current_user.id:
        return jsonify({"message": "Unauthorized action"}), 401

    post.delete()
    return jsonify({"message": "Post deleted successfully"}), 200


## upvote a post
@post_bp.route("/post/<int:post_id>/upvote", methods=["PUT"])
@token_required
def upvote_post(current_user, post_id):
    post = PostModel.get_post(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    upvoted = UpvoteModel.upvote_post(post_id, current_user.id)
    return jsonify({"message": "Vote posted successfully", "upvotes": upvoted}), 200
    # else:
    #     return (
    #         jsonify({"message": "Upvote removed successfully", "upvotes": upvoted}),
    #         200,
    #     )


@post_bp.route("/post/<int:post_id>/comment", methods=["POST"])
@token_required
def create_comment(current_user, post_id):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    if not data.get("text"):
        return jsonify({"message": "No input data provided"}), 400

    post = PostModel.get_post(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if post["isClosed"]:
        return jsonify({"message": "Post is closed"}), 400

    profanity = contains_profanity(data.get("text"))
    post = ReplyModel(
        text=data.get("text"),
        user_id=current_user.id,
        contains_profanity=profanity,
        post_id=post_id,
    )
    post.add()
    return jsonify(ReplySchema().dump(post)), 200


@post_bp.route("/reply/<int:reply_id>", methods=["PUT", "POST"])
@token_required
def create_reply(current_user, reply_id):
    reply = ReplyModel.get_reply(reply_id)
    if not reply:
        return jsonify({"message": "Comment not found"}), 404

    post = PostModel.get_post(reply.post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    if post["isClosed"]:
        return jsonify({"message": "Post is closed"}), 400
    # heirarchical reply
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    if not data.get("text"):
        return jsonify({"message": "No input data provided"}), 400

    profanity = contains_profanity(data.get("text"))
    reply = ReplyModel(
        text=data.get("text"),
        user_id=current_user.id,
        contains_profanity=profanity,
        post_id=reply.post_id,
        parent_id=reply_id,
    )

    reply.add()
    return jsonify({"message": "Reply posted successfully"}), 200


# delete a reply
@post_bp.route("/comment/remove/<int:comment_id>", methods=["DELETE"])
@token_required
def delete_comment(current_user, comment_id):
    comment = ReplyModel.get_reply(comment_id)
    if not comment:
        return jsonify({"message": "Comment not found"}), 404

    if comment.user_id != current_user.id:
        return jsonify({"message": "Unauthorized action"}), 401

    comment.delete()
    return jsonify({"message": "Comment deleted successfully"}), 200


# https://pypi.org/project/profanity-filter/
# from profanity_filter import ProfanityFilter

# pf = ProfanityFilter(lang)


def censor_profanity(text):
    # return pf.censor(text)
    return False


def contains_profanity(text):
    # return pf.is_profane(text)
    return False
