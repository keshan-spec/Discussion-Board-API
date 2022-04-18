import requests
from flask import Blueprint, jsonify, request, session, abort

# models
from models.PostModel import PostModel, PostSchema, UpvoteModel, UpvoteSchema, Pagination
from models.UserModel import UserSchema
from decorators import token_required


# create a blueprint
post_bp = Blueprint("post_bp", __name__)

# get post by id
@post_bp.route("/post/<int:id>", methods=["GET"])
@token_required
def get_post(_, id):
    post = PostModel.get_post(id)
    if not post:
        return jsonify({"message": "Post not found"}), 404

    return jsonify(post), 200

# Get all user records
@post_bp.route("/posts", methods=["GET"])
@token_required
def get_paginated_posts(current_user):
    start = int(request.args.get('start', 1))
    limit = int(request.args.get('limit', 10))

    paginated = PostModel.paginate_posts(start, limit)
    # censor profanity if user has profanity filter enabled
    if current_user.profanity_filter:
        for post in paginated.items:
            post.text = censor_profanity(post.text)
    
    pagination = Pagination(paginated, "/posts")
    return jsonify(pagination.__dict__), 200

@post_bp.route("/post", methods=["POST"])
@token_required
def create_post(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    if not data.get("text"):
        return jsonify({"message": "No input data provided"}), 400

    # censored_text = censor_profanity(data.get("text"))
    profanity = contains_profanity(data.get("text"))
    post = PostModel(text=data.get("text"), user_id=current_user.id, contains_profanity=profanity)
    post.add()
    return jsonify({"message": "Post created successfully"}), 201


## upvote a post
@post_bp.route("/post/<int:post_id>/upvote", methods=["PUT"])
@token_required
def upvote_post(current_user, post_id):
    post = PostModel.get_post(post_id)
    if not post:
        return jsonify({"message": "Post not found"}), 404
    
    upvoted = UpvoteModel.upvote_post(post_id, current_user.id)
    if not upvoted:
        return jsonify({"message": "Upvoted successfully"}), 201
    else:
        return jsonify({"message": "Upvote removed successfully"}), 200


# https://pypi.org/project/profanity-filter/
def censor_profanity(text):
    url = "https://www.purgomalum.com/service/json"
    params = {'text': text, 'fill_char':'*'}
    response = requests.get(url, params=params).json()
    try:
        return response['result']
    except KeyError:
        return response['error']

def contains_profanity(text):
    url = "https://www.purgomalum.com/service/containsprofanity"
    params = {'text': text}
    response = requests.get(url, params=params).json()
    return response