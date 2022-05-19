# Python Environment
1. Create an environment using `python -m venv ./{env_name}` in the root directory.
2. Activate the environment by executing `source ./bin/activate` (`source ./Scrpits/activate` for Windows). Now you should see your environment name prefixed in brackets on your shell.
3. Install the required libraries: `pip install -r requirements.txt`.

# Routes

## Auth

| Description | Method        | Route | Param  | Return 
| -------------| ------------- |:-------------:| -----:| -------------:|
Login to account |POST | `/login` | email, password | JWT Token
Create an account |POST | `/register` | fname, lname, handle, email, password | Registered Email
Logout |POST | `/logout` | None | Message
## Posts

| Description | Method        | Route | Param  | Return 
| -------------| ------------- |:-------------:| -----:| -------------:|
Get a single post |GET | `/post/<int:id>` | Post ID | A single Post Object
Get a list of posts |GET | `/posts` | None | A list of paginated posts
Create a post |POST | `/post` | A Text | Message
Upvote/Downvote a post |POST | `/post/<int:post_id>/upvote` | Post ID | Message
Make a comment on a post |POST | `/post/<int:post_id>/comment` | Post ID | Message
Make a reply on a comment |POST | `/reply/<int:comment_id>` | Comment ID | Message
