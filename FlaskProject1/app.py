from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configuration for the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Create the Movies model
class Movies(db.Model):
    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    cast = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    release_date = db.Column(db.DateTime)
    rating = db.Column(db.Float)
    duration = db.Column(db.Float)
    listed_in = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(120), nullable=False)

class SignIn(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(1000), nullable=False)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    card_number = db.Column(db.String(1000), nullable=False)
    expiry_date = db.Column(db.String(100), nullable=False)
    cvv = db.Column(db.String(100), nullable=False)

# Create all database tables if they don't exist
with app.app_context():
    db.create_all()

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search_movies', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').strip()
    movies = []

    if query:
        # Search for movies in the database using a case-insensitive match
        movies = Movies.query.filter(Movies.title.ilike(f"%{query}%")).all()

    return render_template('index.html', movies=movies)

@app.route('/addmovies')
def movies():
    movies_list = Movies.query.all()
    return render_template('addmovies.html', movies=movies_list)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        type = request.form['type']
        title = request.form['title']
        director = request.form['director']
        cast = request.form['cast']
        country = request.form['country']
        release_date = datetime.strptime(request.form['release_date'], '%Y-%m-%d') if request.form['release_date'] else None
        rating = float(request.form['rating']) if request.form['rating'] else None
        duration = float(request.form['duration']) if request.form['duration'] else None
        listed_in = bool(request.form.get('listed_in'))
        description = request.form['description']

        # Create a new movie instance
        new_movie = Movies(
            type=type, title=title, director=director,
            cast=cast, country=country, release_date=release_date, rating=rating,
            duration=duration, listed_in=listed_in, description=description
        )

        db.session.add(new_movie)
        db.session.commit()

        flash("Movie added successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding movie: {e}", "error")

    return redirect(url_for('movies'))

@app.route('/update/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.get_json()
    movie = Movies.query.get(movie_id)

    if movie:
        movie.type = data['type']
        movie.title = data['title']
        movie.director = data['director']
        movie.cast = data['cast']
        movie.country = data['country']
        movie.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d') if data['release_date'] else None
        movie.rating = data['rating']
        movie.duration = data['duration']
        movie.description = data['description']

        db.session.commit()
        return jsonify({"message": "Movie updated successfully!"}), 200
    else:
        return jsonify({"message": "Movie not found!"}), 404

@app.route('/delete/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    movie = Movies.query.get(movie_id)

    if movie:
        db.session.delete(movie)
        db.session.commit()
        return jsonify({"message": "Movie deleted successfully!"}), 200
    else:
        return jsonify({"message": "Movie not found!"}), 404

@app.route('/movies', methods=['GET'])
def list_movies():
    movies_list = Movies.query.all()
    return render_template('movies.html', movies=movies_list)

@app.route('/account')
def account():
    return render_template('account.html')

# SignIn Route to handle login
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        signin_id = request.form.get('signin_id')

        if signin_id:
            # Update an existing signin
            signin = SignIn.query.get(signin_id)
            if signin:
                signin.email = email
                signin.password = password
                db.session.commit()
        else:
            # Create a new signin
            new_signin = SignIn(email=email, password=password)
            db.session.add(new_signin)
            db.session.commit()

        return redirect(url_for('signin'))

    # Display all sign-ins
    signins = SignIn.query.all()
    return render_template('signin.html', signins=signins)

# Route for deleting a signin
@app.route('/delete_signin/<int:id>', methods=['GET'])
def delete_signin(id):
    signin = SignIn.query.get(id)
    if signin:
        db.session.delete(signin)
        db.session.commit()
    return redirect(url_for('signin'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route to store subscription data
@app.route('/subscription')
def subscription():
    return render_template('subscription.html')
@app.route('/subscription', methods=['POST'])
def create_subscription():
    # Fetch form data
    name = request.form['name']
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']

    # Validate the fields
    if not all([name, card_number, expiry_date, cvv]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Save the subscription data to the database
        new_subscription = Subscription(
            name=name,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv
        )
        db.session.add(new_subscription)
        db.session.commit()

        # Redirect the user to the home page after successful submission
        return redirect(url_for('home'))  # Redirecting to the home page

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
