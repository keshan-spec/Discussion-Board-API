from dotenv import load_dotenv

load_dotenv()
from functools import wraps
from flask import request, jsonify, session
import jwt, os
from models.UserModel import UserModel
from models.BlackListTokensModel import BlackListTokensModel

# decorator for verifying the JWT in Request Header
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
        # return 401 if token is not passed
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        # if token is blacklisted
        if BlackListTokensModel.is_token_blacklisted(token):
            return jsonify({"message": "Token is blacklisted or invalid"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(
                token, os.environ.get("JWT_SECRET_KEY"), algorithms="HS256"
            )
            current_user = UserModel.query.filter_by(id=data["id"]).first()

            if current_user == None:
                return (
                    jsonify({"message": "User has been removed or token is invalid!"}),
                    401,
                )
        except Exception as e:
            print("Error: ", e)
            return jsonify({"message": f"Token is invalid"}), 401

        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


# decorator for verifying the JWT in Session
def session_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # check for session token
        if "access-token" in session:
            token = session["access-token"]
        
        # return 401 if token is empty
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        # if token is blacklisted
        if BlackListTokensModel.is_token_blacklisted(token):
            return jsonify({"message": "Token is blacklisted or invalid"}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(
                token, os.environ.get("JWT_SECRET_KEY"), algorithms="HS256"
            )

            current_user = UserModel.query.filter_by(id=data["id"]).first()

            if current_user == None:
                return (
                    jsonify({"message": "User has been removed or token is invalid!"}),
                    401,
                )
        except Exception as e:
            print("Error: ", e)
            return jsonify({"message": f"Token is invalid"}), 401

        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)
    return decorated
