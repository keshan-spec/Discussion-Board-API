# Introduction
This is an API for a Discussion Board which works quite similar to Stackoverflow or Github Issues, on a smaller scale. 
It allows user authentication, updating user records, making posts (opening discussion topics), close said topics and implements authorization to prevent user data from being manipulated or modified by other users. Posts can also be paginated avoiding longer loading times. 
The highlight of this API is the comments/responsding feature. This feature allows users to make replies in deep threads, similar to Reddit's comment system. 

# Tools and Technologies used
The API was built using Python's ``Flask`` module. Flask is a lightweight module which is highly recommened when building web applications or APIs. 
For the frontend, ``ReactJS`` was used. ReactJS is a popular JavaScript framework developed by Facebook. React is a stateful framework, which made data fetching and storing very efficient.


# Getting Setup
1. Create an environment using `python -m venv ./{env_name}` in the root directory.
2. Activate the environment by executing `source ./bin/activate`. For Windows, `source ./Scrpits/activate`. Now you should see your environment name prefixed in brackets on your shell.
3. Install the required libraries: `pip install -r requirements.txt`.
4. When running the application, you will need to create a `.env` file (a sample file is available) with your credentials and secrets. Make sure to change the mode from `development` to `production` in `app.py` and `run.py`.

# Routes

## Auth

| Description | Method        | Route | Param  | Return 
| -------------| ------------- |:-------------:| -----:| -------------:|
Login to account |POST | `/login` | email, password | JWT Token
Create an account |POST | `/register` | fname, lname, handle, email, password | Registered Email
Logout |POST | `/logout` | None | Message
Verify user's password | POST | `/verify` | User password | 200 if valid, 403 if invalid
## Posts

| Description | Method        | Route | Param  | Return 
| -------------| ------------- |:-------------:| -----:| -------------:|
Get a single post |GET | `/post/<int:id>` | Post ID | A single Post Object
All posts created by the logged in user |GET | `/posts/me` | None | Post Object
Get a list of posts | GET | `/posts` | None | A list of paginated posts
Create a post |POST | `/post` | A Text and Title | Message
Close a post | PUT | `/post/<int:id>/close` | Post ID | Message
Delete a post | DELETE | `/post/<int:id>/` | Post ID | Message
Upvote/Downvote a post |POST | `/post/<int:post_id>/upvote` | Post ID | Message
Make a comment on a post |POST | `/post/<int:post_id>/comment` | Post ID | Message
Delete a comment |DELETE | `/comment/remove/<int:comment_id>` | Comment ID | Message
Make a reply on a comment |POST | `/reply/<int:comment_id>` | Comment ID | Message
Upvote/Downvote a comment |POST | `/comment/<int:comment_id>/upvote` | Comment ID | Message


## User

| Description | Method        | Route | Param  | Return 
| -------------| ------------- |:-------------:| -----:| -------------:|
Get all user records | GET | `/users` | None | An Object of Users
Get user by ID | GET | `/user/<int:id>` | None | A User Object
Query for a user by any field | POST | `/users/find` | Any User attribute | User Object
Update user records | PUT | `/user/update` | Any user attribute | Updated User Object
Delete a user account | DELETE | `/user/<int:id>` | User ID | Message
Update account password | PUT | `/user/update/password` | Old and new password | Message

