import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy

from constants import *
from search4web import search4letters, log_request

app = Flask(__name__)

# Tells flask-sqlalchemy what database to connect to
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:1234@127.0.0.1/search_log"
# Enter a secret key
app.config["SECRET_KEY"] = "1234"
# Initialize flask-sqlalchemy extension
db = SQLAlchemy()
# LoginManager is needed for our application
# to be able to log in and out users
login_manager = LoginManager()
login_manager.init_app(app)


# Create user model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


# Initialize app with extension
db.init_app(app)
# Create database within app context
with app.app_context():
    db.create_all()


# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


@app.route('/search', methods=['POST'])
def do_search() -> str:
    phrase = request.form['phrase']  # request.args['phrase']
    letters = request.form['letters']  # request.args['letters']
    title = 'Here are your results: '
    result = str(search4letters(phrase, letters))
    log_request(request, result)
    return render_template('results.html', the_phrase=phrase,
                           the_letters=letters,
                           the_results=result,
                           the_title=title)


@app.route('/register', methods=["GET", "POST"])
def register():
    # If the user made a POST request, create a new user
    if request.method == "POST":
        user1 = Users.query.filter_by(username=request.form.get("username")).first()
        print(user1)
        if user1:
            return redirect(url_for("register"))
        else:
            user = Users(username=request.form.get("username"),
            password=request.form.get("password"))
            # Add the user to the database
            db.session.add(user)
            # Commit the changes made
            db.session.commit()
            # Once user account created, redirect them
            # to login route (created later on)
            return redirect(url_for("login"))

    # Renders sign_up template if user made a GET request
    return render_template("sign_up.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # If a post request was made, find the user by filtering for the username
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form.get("username")).first()

    # Check if the password entered is the same as the user's password

        try:
            if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
                login_user(user)
            # Redirect the user back to the home
                return redirect(url_for("home"))
        except:
            return render_template("login.html")
    return render_template("login.html")


@app.route("/")
def home():
    # Render home.html on "/" route
    return render_template("home.html")

@app.route('/entry')
@login_required
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search for letters on the web!')


@app.route('/viewlog')
@login_required
def view_the_log() -> 'str':
    contents = list()

    with open(LOG_FILE_PATH, 'r') as log:
        """for line in log:
            contents.append(list())
            for item in line.split(LOG_FILE_SEPARATOR):
                contents[-1].append(item)
                """
    dbconfig = {'host': '127.0.0.1',
                'user': 'root',
                'password': '1234',
                'database': 'search_log', }

    conn = mysql.connector.connect(**dbconfig)
    cursor = conn.cursor()
    _SQL = """select phrase,letters,IP,browser_string,results from log"""
    cursor.execute(_SQL)
    contents = cursor.fetchall()

    cursor.close()
    conn.close()
    titles = ('Form Data', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=("Phrase", " Letters", " Remote_addr", "User_agent", "Results"),
                           the_data=contents)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
