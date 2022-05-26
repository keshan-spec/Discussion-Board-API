from flask import Blueprint, jsonify, request, session
from sqlalchemy.exc import SQLAlchemyError

# models
from models.UserModel import UserModel, UserSchema
from decorators import token_required

# create a blueprint
user_bp = Blueprint("user_bp", __name__)

# Get all user records
@user_bp.route("/users", methods=["GET"])
@token_required
def get_all_users(_):
    users = UserModel.get_all()
    serializer = UserSchema(many=True)
    data = serializer.dump(users)
    return jsonify(data), 200


"""
Find user by id
@param id: user id
"""


@user_bp.route("/user/<int:id>", methods=["GET"])
@token_required
def get_user(_, id):
    """
    Get a user record
    @params: id"""
    users = UserModel.get_by_id(id)
    serializer = UserSchema()
    data = serializer.dump(users)

    return jsonify(data), 200


"""
Find a user by their attributes
@param_type: json
"""


@user_bp.route("/users/find", methods=["POST"])
@token_required
def find(_):
    """
    Find specific records"""
    args = request.get_json()
    if args is None or args == {}:
        return jsonify({"ERROR": "No arguments provided!"}), 400

    users = UserModel.find(**args)
    serializer = UserSchema(many=True)
    data = serializer.dump(users)
    return jsonify(data), 200


# Update a user record
@user_bp.route("/user/update", methods=["PUT"])
@token_required
def update_user(current_user):
    data = request.get_json()
    current_user.update(data)

    serializer = UserSchema()
    updated_data = serializer.dump(data)

    return jsonify({"UPDATED": updated_data}), 200


"""
Delete a user record
@params: id"""


@user_bp.route("/user/<int:id>", methods=["DELETE"])
@token_required
def delete_user(current_user, id):
    try:
        user = UserModel.get_by_id(id)
        if current_user.id != user.id:
            return jsonify({"message": "Unauthorized action"})

        user.delete()
        return jsonify({"message": f"Your account has been deleted"}), 200
    except SQLAlchemyError as e:
        error = str(e.__dict__["orig"])
        return jsonify({"Error": error}), 500
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


# update password
@user_bp.route("/user/update/password", methods=["PUT"])
@token_required
def update_password(current_user):
    data = request.get_json()
    if data is None or data == {}:
        return jsonify({"ERROR": "No arguments provided!"}), 400

    if not data.get("old_password") or not data.get("new_password"):
        return jsonify({"ERROR": "No arguments provided!"}), 400

    if current_user.update_password(data.get("old_password"), data.get("new_password")):
        return jsonify({"UPDATED": "Password updated sucessfully"}), 200
    else:
        return jsonify({"ERROR": "Password is incorrect"}), 403
