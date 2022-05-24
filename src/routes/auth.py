from flask import Blueprint, jsonify, request, make_response, session
import datetime
import os, jwt
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import cross_origin

# models
from models.UserModel import UserModel, UserSchema
from decorators import token_required

# create a blueprint
auth_bp = Blueprint("auth_bp", __name__)


def create_token(id, exp=30):
    return jwt.encode(
        {
            "id": id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=exp),
        },
        os.environ.get("JWT_SECRET_KEY"),
    )


# verify token
@auth_bp.route("/verify", methods=["GET"])
@token_required
def verify_token(user):
    return jsonify({"message": "Token is valid"})


# Login user
@auth_bp.route("/login", methods=["POST"])
# @cross_origin()
def login():
    # creates dictionary of form data
    auth = request.json

    # checks if username and password are in the form data
    if not auth or not auth["email"] or not auth["password"]:
        # returns 401 if any email or / and password is missing
        return (jsonify({"ERROR": "Credentials missing!"}), 401)

    user = UserModel.query.filter_by(email=auth["email"]).first()
    if not user:
        # returns 401 if user does not exist
        return (
            jsonify({"ERROR": f"Could not find user with email : {auth['email']}"}),
            401,
        )

    try:
        valid, status = user.check_hash(auth["password"])
        if valid:
            # generates the JWT Token
            token = create_token(user.id)

            # set cookie on client
            # res = make_response({"token": token})
            # res.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            # res.headers["Access-Control-Allow-Credentials"] = "true"
            # res.set_cookie("token", value=token, httponly=True, domain=".localhost")
            # return res
            print(token)
            return (jsonify({"token": token}), status)

        # returns 403 if password is wrong
        return jsonify(f"Could not verify - {status}"), 403
    except Exception as e:
        return jsonify(f"Could not verify - {e}"), 403


# Register user
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Create a new user record
    @params: UserModel
        :- fname
        :- lname
        :- email
        :- password
        :- created_at (default date time)
        :- modified_at (date time)
    """
    data = request.get_json()
    user = UserModel.query.filter_by(email=data.get("email")).first()
    handle = UserModel.query.filter_by(handle=data.get("username")).first()

    if user:
        # returns 500 if user not exist
        return (
            jsonify({"Integreity Error": f"Email ({user.email}) already exists!"}),
            500,
        )
    if handle:
        # returns 500 if user not exist
        return (
            jsonify(
                {"Integreity Error": f"Username ({handle.handle}) already exists!"}
            ),
            500,
        )

    user = UserModel(
        fname=data.get("fname"),
        lname=data.get("lname"),
        email=data.get("email"),
        password=data.get("password"),
        handle=data.get("username"),
        modified_at=datetime.datetime.utcnow(),
        profanity_filter=data.get("profanity_filter"),
    )

    user.password = user.generate_hash(user.password)

    try:
        user.save()
        serializer = UserSchema()
        data = serializer.dump(user)
        return jsonify({"email": data["email"]}), 201
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        return jsonify({"SQLALCHEMY ERROR": error}), 500


# logout
@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user):
    """
    Logout a user
    @params: id
    """
    try:
        current_user.logout(request.headers["x-access-token"])
        return jsonify({"message": "Logged out"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
