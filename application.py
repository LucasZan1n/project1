import os
import requests
from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["JSON_SORT_KEYS"] = False
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["POST", "GET"])
def index():
	if request.method == "GET":
		if "username" in session:
			return render_template("index(logged_in).html", username=session["username"])
		else:
			return render_template("index(logged_out).html")

@app.route("/booksearch", methods=["POST"])
def book_search():
	search = request.form.get("search")
	isbn = db.execute(f"SELECT * FROM books WHERE isbn LIKE '%{search}%'")
	title = db.execute(f"SELECT * from books WHERE LOWER(title) LIKE LOWER('%{search}%')")
	author = db.execute(f"SELECT * from books WHERE LOWER(author) LIKE LOWER('%{search}%')")
	# Checks if user is logged in
	if "username" in session:
		if isbn.rowcount == 0 and title.rowcount == 0 and author.rowcount == 0:
				return render_template("error(logged_in).html", message="No books found")
		# Looks what query matched what column
		elif isbn.rowcount != 0:
			isbn = isbn.fetchall()
			return render_template("books(logged_in).html", search=isbn, username=session["username"])
		elif title.rowcount != 0:
			title = title.fetchall()
			return render_template("books(logged_in).html", search=title, username=session["username"])
		elif author.rowcount != 0:
			author = author.fetchall()
			return render_template("books(logged_in).html", search=author, username=session["username"])
		elif year.rowcount != 0:
			year = year.fetchall()
			return render_template("books(logged_in).html", search=year, username=session["username"])
	# If query is an integer the year will be checked
	else:
		if isbn.rowcount == 0 and title.rowcount == 0 and author.rowcount == 0:
			return render_template("error(logged_out).html", message="No books found")
		elif isbn.rowcount != 0:
			isbn = isbn.fetchall()
			return render_template("books(logged_out).html", search=isbn)
		elif title.rowcount != 0:
			title = title.fetchall()
			return render_template("books(logged_out).html", search=title)
		elif author.rowcount != 0:
			author = author.fetchall()
			return render_template("books(logged_out).html", search=author)	

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register(logged_out).html")
	
	username = request.form.get("username")
	email = request.form.get("email")
	password = request.form.get("password")
	
	if request.method == "POST":
		check_existence = db.execute("SELECT * FROM users WHERE username=:username", {"username": username})
		if check_existence.rowcount != 0:
			return render_template("error(logged_out).html", message="Username already exists")
		else:
			db.execute("INSERT INTO users (username, password, email) VALUES (:username, :password, :email)", {"username": username, "password": password, "email": email})
			db.commit()
			session["username"] = username
			return redirect("/")

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		if db.execute("SELECT * FROM users WHERE username=:username AND password=:password", {"username": username, "password": password}).rowcount != 0:
			session["username"] = username
			return redirect("/")
		else:
			return render_template("error(logged_out).html", message="Wrong username/password")
		
	if request.method == "GET":
		return render_template("login(logged_out).html")

@app.route("/logout")
def logout():
	session.pop("username", None)
	return redirect("/")

@app.route("/book/<int:book_id>", methods=["POST", "GET"])
def book(book_id):
	if "username" in session:
		book = db.execute("SELECT * FROM books WHERE id=:id", {"id": book_id}).fetchone()
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "l4MMvnUu4zYVIB63mLqy5A", "isbns": book.isbn})
		review_goodreads = res.json()
		average_rating = review_goodreads["books"][0]["average_rating"]
		num_ratings = review_goodreads["books"][0]["work_ratings_count"]
		reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id", {"book_id": book_id})
		users = db.execute("SELECT * FROM users").fetchall()
		if reviews.rowcount == 0:
			reviews = None
		else:
			reviews = reviews.fetchall()
		return render_template("book(logged_in).html", book=book, average_rating=average_rating, num_ratings=num_ratings, reviews=reviews, users=users, username=session["username"])

	else:
		book = db.execute("SELECT * FROM books WHERE id=:id", {"id": book_id}).fetchone()
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "l4MMvnUu4zYVIB63mLqy5A", "isbns": book.isbn})
		review_goodreads = res.json()
		average_rating = review_goodreads["books"][0]["average_rating"]
		num_ratings = review_goodreads["books"][0]["work_ratings_count"]
		reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id", {"book_id": book_id})
		users = db.execute("SELECT * FROM users").fetchall()
		if reviews.rowcount == 0:
			reviews = None
		else:
			reviews = reviews.fetchall()
		return render_template("book(logged_out).html", book=book, average_rating=average_rating, num_ratings=num_ratings, reviews=reviews, users=users)		

@app.route("/book/<int:book_id>/review", methods=["POST"])
def review(book_id):
	title = request.form.get("title")
	content = request.form.get("content")
	rating = request.form.get("rating")
	user = db.execute("SELECT * FROM users WHERE username=:username", {"username": session["username"]}).fetchone()
	user_id = user.id
	reviews_given = db.execute("SELECT * FROM reviews WHERE book_id=:book_id AND user_id=:user_id", {"book_id": book_id, "user_id": user_id}).rowcount
	if reviews_given != 0:
		return render_template("error(logged_in).html", message="You already wrote a review for this book", username=session["username"])
	else:
		db.execute("INSERT INTO reviews (title, content, book_id, user_id, rating) VALUES (:title, :content, :book_id, :user_id, :rating)", {"title": title, "content": content, "book_id": book_id, "user_id": user_id, "rating": rating})
		db.commit()
		return render_template("success(logged_in).html", book_id=book_id, username=session["username"])

@app.route("/api/<isbn>")
def api(isbn):
	if db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).rowcount == 0:
		return jsonify({"error": "Book not found"}), 422
	else:
		book = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn}).fetchone()
		title = book.title
		author = book.author
		year = book.year
		isbn = book.isbn
		num_reviews = db.execute("SELECT * FROM reviews WHERE book_id=:book_id", {"book_id": book.id}).rowcount
		average_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id=:book_id", {"book_id": book.id}).scalar()
		if num_reviews == 0:
			average_rating = None
		return jsonify(
				{
				"title": title,
				"author": author,
				"year": year,
				"isbn": isbn,
				"review_count": num_reviews,
				"average_score": str(average_rating)[:3]
				}
			)