# src/app.py
import datetime
from flask import Flask, jsonify
from models.UserModel import UserModel
from models.BlackListTokensModel import BlackListTokensModel
from models.PostModel import PostModel
from config import app_config
from models import db, bcrypt


def create_app(env_name):
    # app initiliazation
    app = Flask(__name__)

    app.config.from_object(app_config[env_name])

    # initializing bcrypt
    bcrypt.init_app(app)  # add this line
    db.init_app(app)  # add this line

    return app


def fill_tables():
    # create test users
    users = [
        {
            "fname": "Shehan",
            "lname": "Jude",
            "email": "shehan@ysjcs.net",
            "password": "123",
        },
        {
            "fname": "Keshanth",
            "lname": "Jude",
            "email": "keshan@ysjcs.net",
            "password": "123",
        },
        {
            "fname": "Jathusa",
            "lname": "Thiruchelvam",
            "email": "jathu@ysjcs.net",
            "password": "123",
        },
        {
            "fname": "Sharaf",
            "lname": "Mohamed",
            "email": "sharaf@ysjcs.net",
            "password": "123",
        },
        {
            "fname": "Shavin",
            "lname": "Supramanium",
            "email": "shavin@ysjcs.net",
            "password": "123",
        },
        {
            "fname": "Shopikar",
            "lname": "Supramanium",
            "email": "shopi@ysjcs.net",
            "password": "123",
        },
    ]

    for user in users:
        try:
            user = UserModel(
                fname=user["fname"],
                lname=user["lname"],
                email=user["email"],
                password=user["password"],
                modified_at=datetime.datetime.utcnow(),
            )
            user.password = user.generate_hash(user.password)
            user.save()
        except Exception as e:
            print("ERROR: ", e)
            break

    print("CREATED TEST DATA: Users")

    # create test posts
    post = {
        "text": "This is a test post",
        "user_id": 1
    }

    n = True
    for _ in range(1,31):
        try:
            p = PostModel(
                text=post["text"],
                user_id=post["user_id"],
                contains_profanity=n
            )
            p.add()
            n = not n
        except Exception as e:
            print("ERROR: ", e)
            break

    print("CREATED TEST DATA: Posts")

if __name__ == "__main__":
    app = create_app("development")
    with app.app_context():
        try:
            print("Droping all tables")
            db.drop_all()
            db.create_all()
            print("Database tables created")
            fill_tables()  # create dummy data
        except AttributeError as e:
            print(f"Error: {e}")
            exit()
