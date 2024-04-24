from flask import render_template, request, redirect, url_for
import requests
from app import app, db
from app.models import Review
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np

OMDB_API_KEY = '373f7443'

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def softmax(vec):
    exponential = np.exp(vec)
    probabilities = exponential / np.sum(exponential)
    return probabilities

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        movie_title = request.form['movie_title']
        movie_list = fetch_movie_list(movie_title)
        if movie_list:
            return render_template('search.html', movie_list=movie_list)
        else:
            return render_template('search.html', error="No movies found. Please try again.")
    return render_template('search.html')

def fetch_movie_list(movie_title):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={movie_title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('Response') == 'True':
            movie_list = []
            for movie in data.get('Search', []):
                movie_info = {
                    'title': movie.get('Title'),
                    'year': movie.get('Year'),
                    'poster': movie.get('Poster'),
                    'imdb_id': movie.get('imdbID')
                }
                movie_list.append(movie_info)
            return movie_list
    return None



@app.route('/review/<imdb_id>', methods=['GET', 'POST'])
def review(imdb_id):
    if request.method == 'POST':
        review_text = request.form['review_text']
        user_rating = float(request.form['user_rating'])

        review_text = preprocess(review_text)
        encoded_input = tokenizer(review_text, return_tensors='pt')
        output = model(**encoded_input)
        scores = output.logits[0].detach().numpy()
        scores = softmax(scores)


        overall_rating = calculate_overall_rating(scores)


        movie_info = fetch_movie_info(imdb_id)
        if movie_info:
            movie_title = movie_info['title']
        else:
            movie_title = 'Unknown'

        
        new_review = Review(imdb_id=imdb_id, movie_title=movie_title, review_text=review_text, overall_rating=overall_rating)
        db.session.add(new_review)
        db.session.commit()

        return render_template('rating.html', overall_rating=overall_rating)

    
    movie_info = fetch_movie_info(imdb_id)
    if movie_info:
        movie_title = movie_info['title']
    else:
        movie_title = 'Unknown'
    return render_template('review.html', movie_title=movie_title, imdb_id=imdb_id)

def fetch_movie_info(imdb_id):
    url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('Response') == 'True':
            movie_info = {
                'title': data.get('Title'),
                'year': data.get('Year'),
                'poster': data.get('Poster'),
                'imdb_id': data.get('imdbID')
            }
            return movie_info
    return None


def calculate_overall_rating(scores):
    ps = scores[2]
    ns = scores[0]
    nes = scores[1]

    # rating = (ps - ns + 1) *2.5

    if(ps>ns and ps>nes):
        rating = 5 - 4*ns - 2*nes 
    elif(ns>nes and ns>ps):
        rating = 4*ps + 2*nes
    else:
        rating = 2.5 + 3*ps -3*ns        
    rating = round(rating, 2)

    return rating

@app.route('/rating/<overall_rating>')
def rating(overall_rating):
    return render_template('rating.html', overall_rating=overall_rating)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/reviews')
def reviews():
    reviews = Review.query.all()
    return render_template('reviews.html', reviews=reviews)



# from flask import render_template, request, redirect, url_for
# import requests
# from app import app, db
# from app.models import Review
# # from transformers import pipeline

# from transformers import AutoModelForSequenceClassification
# from transformers import TFAutoModelForSequenceClassification
# from transformers import AutoTokenizer, AutoConfig
# import numpy as np
# # from scipy.special import softmax

# OMDB_API_KEY = '373f7443'

# # model_path = "cardiffnlp/twitter-roberta-base-sentiment-latest"
# # sentiment_task = pipeline("sentiment-analysis", model=model_path, tokenizer=model_path)
# MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
# tokenizer = AutoTokenizer.from_pretrained(MODEL)
# config = AutoConfig.from_pretrained(MODEL)
# model = AutoModelForSequenceClassification.from_pretrained(MODEL)
# #model.save_pretrained(MODEL)

# def preprocess(text):
#     new_text = []
#     for t in text.split(" "):
#         t = '@user' if t.startswith('@') and len(t) > 1 else t
#         t = 'http' if t.startswith('http') else t
#         new_text.append(t)
#     return " ".join(new_text)

# def softmax(vec):
#   exponential = np.exp(vec)
#   probabilities = exponential / np.sum(exponential)
#   return probabilities

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/search', methods=['GET', 'POST'])
# def search():
#     if request.method == 'POST':
#         movie_title = request.form['movie_title']
#         movie_info = fetch_movie_info(movie_title)
#         if movie_info:
#             return redirect(url_for('review', movie_title=movie_title))
#         else:
#             return render_template('search.html', error="Movie not found. Please try again.")
#     return render_template('search.html')



# def fetch_movie_info(movie_title):
#     url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         data = response.json()
#         if data.get('Response') == 'True':
#             movie_info = {
#                 'title': data.get('Title'),
#                 'year': data.get('Year'),
#                 'director': data.get('Director'),
#                 'duration': data.get('Runtime'),
#                 'genre': data.get('Genre')
#             }
#             return movie_info
#     return None


# @app.route('/review', methods=['GET', 'POST'])
# def review():
#     if request.method == 'POST':
#         movie_title = request.form['movie_title']
#         review_text = request.form['review_text']
#         user_rating = request.form['user_rating']

#         # Perform sentiment analysis
#         review_text = preprocess(review_text)
#         encoded_input = tokenizer(review_text, return_tensors='pt')
#         output = model(**encoded_input)
#         scores = output[0][0].detach().numpy()
#         scores = softmax(scores)
#         # sentiment = sentiment_task(review_text)

#         # Calculate overall rating (replace this with your logic)
#         overall_rating = calculate_overall_rating(scores)

#         # Store the review data and sentiment in the database (or perform any other actions)
#         new_review = Review(movie_title=movie_title, review_text=review_text, overall_rating=overall_rating)
#         db.session.add(new_review)
#         db.session.commit()

#         # Render the rating.html template with the sentiment, user rating, and overall rating
#         return render_template('rating.html', overall_rating=overall_rating)

#     # If it's a GET request, render the review.html template
#     movie_title = request.args.get('movie_title')
#     return render_template('review.html', movie_title=movie_title)

# def calculate_overall_rating(scores):
#     rating = (scores[2] - scores[0])/2
#     return rating  # Example overall rating


# @app.route('/thanks')
# def thanks():
#     return render_template('thanks.html')
