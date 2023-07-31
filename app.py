import os
import operator, functools

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    if request.method == "GET":
        username = db.execute(
            "SELECT username from users WHERE id = ?", session["user_id"]
        )
        id = db.execute("SELECT id from users WHERE id = ?", session["user_id"])
        username = username[0]
        print(username["username"])
        db.execute(
            "DELETE from stocks_owned WHERE username = ? AND shares = 0", username["username"]
        )
        stocks_owned = db.execute(
            "SELECT * from stocks_owned WHERE username = ?", username["username"]
        )
        id = id[0]

        stocks = []
        for stock in stocks_owned:
            stocks.append(stock)

        balance = db.execute(
            "SELECT cash from users WHERE username = ?", username["username"]
        )
        print(stocks)

        return render_template(
            "index.html",
            username=username["username"],
            balance=balance[0],
            stocks=stocks,
        )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    username = db.execute("SELECT username from users WHERE id = ?", session["user_id"])
    username = username[0]["username"]
    if request.method == "POST":
        symbol = request.form.get("symbol")
        amount = request.form.get("shares")
        quote = lookup(symbol)

        if not symbol:
            return render_template("buy.html", error="Enter a symbol")
        elif not amount or not amount.isdigit() or int(amount) <= 0:
            return render_template("buy.html", error="Enter a valid amount")
        quote = lookup(symbol)
        if quote is None:
            return render_template("buy.html", error="Symbol not found")

        price = quote["price"]
        total_cost = int(amount) * price
        cash = db.execute("SELECT cash from users WHERE username = ?", username)
        cash = cash[0]["cash"]

        if cash < total_cost:
            return render_template("buy.html", error="Insufficient balance")

        db.execute(
            "UPDATE users SET cash = cash - ? WHERE id = ?",
            total_cost,
            session["user_id"],
        )

        owned_stocks_names_dict = db.execute(
            "SELECT stock_name from stocks_owned WHERE username = ?", username
        )
        owned_stocks_names = []
        for i in owned_stocks_names_dict:
            owned_stocks_names.append(i["stock_name"])

        if quote['name'] in owned_stocks_names:
            number_of_stocks = db.execute("SELECT shares from stocks_owned WHERE username = ? AND stock_name = ?", username, quote['name'])
            number_of_stocks = int(number_of_stocks[0]["shares"])
            db.execute("UPDATE stocks_owned set shares = ? WHERE username = ? AND stock_name = ?", number_of_stocks + int(amount), username, quote['name'])

        else:
            db.execute("INSERT INTO stocks_owned (username, stock_name, shares, price_per_stock) VALUES (?,?,?,?) ", username, quote['name'], amount, price)


        #Updating history
        transaction_type = "Buy"
        db.execute("INSERT INTO history (username, transaction_type, Company, shares, total_price) VALUES(?,?,?,?,?)", username, transaction_type, symbol, int(amount), total_cost)

        return redirect("/")
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    username = db.execute("SELECT username from users WHERE id = ?", session["user_id"])
    username = username[0]['username']
    history = db.execute("SELECT * from history WHERE username = ?", username)
    return render_template("history.html", history = history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error="Enter the username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="Enter the password")


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", error="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html", error="")

    symbol = request.form.get("symbol")
    quote = lookup(symbol)
    if isinstance(quote, dict) == False:
        return render_template("quote.html", error = "Enter a valid symbol")
    message = "A share of " + quote["name"] +" ("+ quote["symbol"] +") "+ "costs $" +str(quote["price"])+"."
    return render_template("quote.html", quote = quote)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")
        if not username:
            return render_template("register.html", error="Enter a valid username")
        if password1 != password2:
            return render_template("register.html", error="Enter the same password")
        if not password1 or not password2:
            return render_template("register.html", error="Enter a password")

        final_users = []
        usernames = db.execute("SELECT username from users")
        for users in usernames:
            final_users.append(users["username"])
        if username in final_users:
            return render_template("register.html", error="Username already exists")

        hashed = generate_password_hash(password1, method='pbkdf2', salt_length=16)
        db.execute("INSERT INTO users (username, hash) VALUES (?,?)", username, hashed)
        return render_template("login.html")
    return render_template("register.html", error="")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    username = db.execute("SELECT username from users WHERE id = ?", session["user_id"])
    username = username[0]['username']

    if request.method == "GET":

        stocks = db.execute("SELECT * from stocks_owned WHERE username = ?", username)
        stocks_names = []
        for i in stocks:
            stocks_names.append(i)

        return render_template("sell.html", query = stocks_names)


    stocks_owned = db.execute("SELECT * from stocks_owned WHERE username = ?", username)
    owned_stocks_names = []
    for i in stocks_owned:
        owned_stocks_names.append(i["stock_name"])

    symbol = request.form.get("symbol")
    shares_selling = request.form.get("shares")

    if symbol not in owned_stocks_names:
        return render_template("sell.html", error = "You do not own the stock")
    if shares_selling == None:
        return render_template("sell.html", error = "Enter a minimum amount to sell")

    owned_shares = db.execute("SELECT shares from stocks_owned WHERE username = ? AND stock_name = ?", username, symbol)

    if int(shares_selling) > int(owned_shares[0]["shares"]):
        return render_template("sell.html", error = "You do not own enough shares")

    #Updating cash in user
    quote = lookup(symbol)
    price = quote['price']
    amount_added = price * int(shares_selling)
    initial_amount = db.execute("SELECT cash from users WHERE username = ?", username)
    initial_amount = initial_amount[0]['cash']
    final_amount = float(initial_amount) + amount_added
    db.execute("UPDATE users SET cash = ? WHERE username = ?", final_amount, username)

    #Updating shares with user
    shares_owned = db.execute("SELECT shares from stocks_owned WHERE username = ? AND stock_name = ?", username, symbol)
    shares_owned = shares_owned[0]["shares"]
    result_shares = int(shares_owned) - int(shares_selling)
    db.execute("UPDATE stocks_owned SET shares = ? WHERE username = ? AND stock_name = ?", result_shares, username, symbol)

    #Updating history
    transaction_type = "Sell"
    db.execute("INSERT INTO history (username, transaction_type, Company, shares, total_price) VALUES(?,?,?,?,?)", username, transaction_type, symbol, int(shares_selling), amount_added)


    return redirect("/")


@app.route("/addcash", methods=["GET", "POST"])
@login_required
def addcash():
    if request.method == "POST":
        username = db.execute("SELECT username from users WHERE id = ?", session["user_id"])
        username = username[0]['username']
        amount = request.form.get("amount")
        initial_amount = db.execute("SELECT cash from users WHERE username = ?", username)
        initial_amount = initial_amount[0]["cash"]
        final_amount = int(amount) + float(initial_amount)

        db.execute("UPDATE users SET cash = ? WHERE username = ?", final_amount, username)

        return redirect("/")

    return render_template("addcash.html")


@socketio.on('disconnect')
def disconnect_user():
    session.clear()
    return redirect("/")
    