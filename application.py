'''
Hawt Reads

The Hawt Reads applicaiton is a basic web app that uses a database of books
(containing title, author, publicaiton year, and isbn) to allow users to search
books, vew information, leave reviews, and querywith a basic API. The app aslo
employs the Goodreads API to include some basic informaiton from that site.

Users must register and login to use the site search, view book information, or
leave a review. They do not have to login to call to the API.
'''
import os
import requests

from flask import Flask, session, render_template, request, url_for, redirect, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Goodreads API key
goodreads_key = "wDwix2wGyGv8ugmp8coRTg"

'''
Registration Page

Simple page with a registration form. POST request ensures no duplicate username
exists before creating a new entry in users data table. If it does not, the new user
is created and redircted to the login page.

GET request to the registration page redirect to the home page if the user is
already logged in.
'''
@app.route("/register", methods=["GET", "POST"])
def register():
    # no logged in users
    if "user_id" in session:
        flash("You are already logged in!")
        return redirect(url_for('index'))

    error = None

    # GET renders template
    if request.method == "GET":
        return render_template("register.html", error=error)
    
    credentials = [request.form.get("un"), request.form.get("pw")]

    user_id = db.execute("SELECT id FROM users WHERE username=:username",
                             {"username": credentials[0]}).fetchone()
    
    # Duplicate form entries trigger an error
    if user_id != None:
        error = "User is already registered!"
        return render_template("register.html", error=error)

    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
        {"username": credentials[0], "password": credentials[1]})
    db.commit()
    flash("You are now registered for Hawt Reads!")

    return redirect(url_for('login'))
'''
Login Page

Simple page with a login form. Users who are already logged in are redirected to
the home page. Users who exist in the database are logged in and sent to the home
page with a success message. Those who do not exists are given an invalid un/pw 
error.
'''
@app.route("/login", methods=["GET", "POST"])
def login():
    # No logged in users
    if "user_id" in session:
        flash("You are already logged in!")
        return redirect(url_for('index'))

    error = None

    if request.method == "POST":
        un = request.form.get("un")
        pw = request.form.get("pw")

        user_id = db.execute("SELECT id FROM users WHERE username=:username AND password=:password",
                                 {"username": un, "password": pw}).fetchone()
        db.commit()

        # Error messgae if user does not exist
        if user_id is None:
            error = "invalid username or password"

        else:
            session["user_id"] = user_id.id
            flash("You were successfully logged in!")
            return redirect(url_for('index'))

    return render_template("login.html", error=error)

'''
Home Page

The home page contains a search from where a user can search for a book in the
database by titel, author, or isbn. Upon successful search, the page loads and
displays search results (search parameters passed as query string parameters).

If no results are found, a message communicating this result is displayed. Users
must be logged in toview this page.
'''
@app.route("/", methods=["GET", "POST"])
def index():
    # Logout button
    if request.method == "POST":
        session.pop("user_id", None)
        flash("successfully logged out")
        return redirect(url_for('login'))

    # no logged out users
    if "user_id" not in session:
        flash("please log in or register")
        return redirect(url_for('login'))

    book_results = []
    args = request.args
    search_flag = False
    error = None

    # this block runs if search terms are passed in GET request
    if "query" in args and "search_type" in args:
        search_flag = True
        query = args.get("query")
        query = '%' + query.lower() + '%'

        search_type = args.get("search_type")
        
        if search_type == "title":
            book_results = db.execute("SELECT * FROM books WHERE lower(title) LIKE :query",
                {"query": query}).fetchall()

        elif search_type == "isbn":
            book_results = db.execute("SELECT * FROM books WHERE isbn LIKE :query",
                {"query": query}).fetchall()

        elif search_type == "author":
            book_results = db.execute("SELECT * FROM books WHERE lower(author) LIKE :query",
                {"query": query}).fetchall()
        
        db.commit()
    # if there was a search, but no results, populate error
    if search_flag == True and not book_results:
        error = "no results for that search!"
        
    return render_template("index.html", books=book_results, error=error)

'''
Book Page

The book page displays information from the site database (title, author, isbn,
and publicaiton year) as well as basic Godreads data (average rating and number
of ratings). The Goodreads data is gathered with an API call based on the book's
isbn.

The user is allowed to sumit a review for the book, but cannot submit more than
1 review per book - this results in a failed submission and an error message.

The page also displays basic instructions for using the API (see below)
'''
@app.route("/books/<string:book_id>", methods=["GET", "POST"])
def book(book_id):
    # no logged out users
    if "user_id" not in session:
        flash("please log in or register")
        return redirect(url_for('login'))

    error = None
    
    # get book info
    book = db.execute("SELECT * FROM books WHERE id=:book_id",
        {"book_id": int(book_id)}).fetchone()
    
    # get and parse Goodreads API data
    res = requests.get("https://www.goodreads.com/book/review_counts.json", 
        params={"key": goodreads_key, "isbns": book.isbn})
    values = res.json()
    avg_rating = values["books"][0]["average_rating"]
    num_ratings = values["books"][0]["work_ratings_count"]

    if request.method == "POST":
        form_id = request.form.get("btn")

        # if form is logout, log user out
        if form_id == "logout":
            session.pop("user_id", None)
            flash("successfully logged out")
            return redirect(url_for('login'))

        else:
            check_prev_reviewed = db.execute("SELECT id FROM reviews WHERE user_id=:user_id AND book_id=:book_id",
                {"user_id": session.get("user_id"), "book_id": int(book_id)}).fetchone()
            
            # add new review
            if check_prev_reviewed is None:
                review = request.form.get("commentbox")
                db.execute("INSERT INTO reviews (user_id, book_id, review) VALUES (:user_id, :book_id, :review)",
                    {"user_id": session.get("user_id"), "book_id": int(book_id), "review": review})

            # error if user has reviewd book
            else:
                error = "you've already reviewed this book"
    
    # get all reviews for the book
    reviews = db.execute("SELECT * FROM reviews JOIN users ON users.id=reviews.user_id WHERE book_id=:book_id",
        {"book_id": int(book_id)}).fetchall()

    db.commit()
    
    return render_template("book.html", book=book, reviews=reviews, avg_rating=avg_rating, num_ratings=num_ratings, error=error)

'''
API

Calls to the API returns data from the site database upon success. This is based
off a book's isbn. If an isbn match is not found in the database, the API returns
an error and a 404 code.
'''
@app.route("/api/<string:isbn_req>")
def api_req(isbn_req):
    isbn = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn_req}).fetchone()

    if isbn is None:
        return jsonify({"error": "ISBN not found"}), 404

    review_count = db.execute("SELECT COUNT(review) FROM reviews WHERE book_id=:book_id",
        {"book_id": isbn.id}).fetchall()
    db.commit()
    print(review_count)
    return jsonify({
        "title": isbn.title,
        "author": isbn.author,
        "year": isbn.year,
        "isbn": isbn.isbn,
        "review_count": review_count[0][0]
    })
