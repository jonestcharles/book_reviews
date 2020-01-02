# book_reviews
A Flask-powered book web app allowing reviews with a Goodreads API. Built for Flask and DB/SQL practice

a basic web app that uses a database of books
(containing title, author, publicaiton year, and isbn) to allow users to search
books, vew information, leave reviews, and querywith a basic API. The app aslo
employs the Goodreads API to include some basic informaiton from that site.

Users must register and login to use the site search, view book information, or
leave a review. They do not have to login to call to the API.

In order to create Hawt Reads, the following steps were taken:

1. Configure site database: Three table were created using the PostgreSQL commands
that follow:

a. Table books with columns id (serial), isbn (variable length string), title 
(variable length string), author (variable length string), and year (integer).

CREATE TABLE books(id SERIAL PRIMARY KEY, isbn VARCHAR UNIQUE NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INT NOT NULL);

b. Table users with columns id (serail), username (variable length string), and
password (variable length string).

CREATE TABLE users(id SERIAL PRIMARY KEY, username VARCHAR UNIQUE NOT NULL, password VARCHAR NOT NULL);

c. Table reviews with columns id (serial), review (variable length string), 
user_id (integer referencing users), and book_id (integer referencing books).

CREATE TABLE reviews(id SERIAL PRIMARY KEY, review VARCHAR NOT NULL, user_id INT NOT NULL REFERENCES users, book_id INT NOT NULL REFERENCES books);

These tables are intended to hold a list of books, users on the site, and reviews
submitted by users for the books in question.

2. Configure the Flask app:

Python and PIP were installed in order to run and configure Flask. PIP installs
dependencies from requirements.txt with the following command:

pip3 install -r requirements.txt

The only addition to the provided requirements doc was the Python requests library,
used during API calls to Goodreads.

The following environment variables were set in order to set the Flask app path,
and the database URL:

export FLASK_APP=application.py
export DATABASE_URL= <your database url>

3. Populate database with initial books list by running import.py

import.py opens a csv file containing a list of books that are then raed into
the database for Hawt Reads. import.py assume the format isbn, title, author,
publicaiton year for each row in the file. It also assumes that line 1 contains
column headers. These are not used, as the database tables was built before
running this app. See the project README.md for details.

Hawt Reads contians the following site pages:

1. Registration Page

Simple page with a registration form. POST request ensures no duplicate username
exists before creating a new entry in users data table. If it does not, the new user
is created and redircted to the login page.

GET request to the registration page redirect to the home page if the user is
already logged in.

2. Login Page

Simple page with a login form. Users who are already logged in are redirected to
the home page. Users who exist in the database are logged in and sent to the home
page with a success message. Those who do not exists are given an invalid un/pw
error.

3. Home Page

The home page contains a search from where a user can search for a book in the
database by titel, author, or isbn. Upon successful search, the page loads and
displays search results (search parameters passed as query string parameters).

If no results are found, a message communicating this result is displayed. Users
must be logged in toview this page.

4. Book Page

The book page displays information from the site database (title, author, isbn,
and publicaiton year) as well as basic Godreads data (average rating and number
of ratings). The Goodreads data is gathered with an API call based on the book's
isbn.

The user is allowed to sumit a review for the book, but cannot submit more than
1 review per book - this results in a failed submission and an error message.

The page also displays basic instructions for using the API (see below).

5. API

Calls to the API returns data from the site database upon success. This is based
off a book's isbn. If an isbn match is not found in the database, the API returns
an error and a 404 code.
