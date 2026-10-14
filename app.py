from pathlib import Path

from flask import Flask, render_template, request
import pickle
import numpy as np

BASE_DIR = Path(__file__).resolve().parent


def load_pickle(filename):
    with (BASE_DIR / filename).open('rb') as file:
        return pickle.load(file)


popular_df = load_pickle('popular.pkl')
pt = load_pickle('pt.pkl')
books = load_pickle('books.pkl')
similarity_scores = load_pickle('similarity_scores.pkl')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        'index.html',
        popular_books=popular_df.to_dict(orient='records'),
    )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html', book_titles=pt.index.tolist())

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = (request.form.get('user_input') or '').strip()

    if not user_input or user_input not in pt.index:
        return render_template(
            'recommend.html',
            book_titles=pt.index.tolist(),
            query=user_input,
            error='Choose a title from the suggestions so we can find its closest matches.',
        )

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        book = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title').iloc[0]
        data.append({
            'title': book['Book-Title'],
            'author': book['Book-Author'],
            'image': book['Image-URL-M'],
        })

    return render_template(
        'recommend.html',
        book_titles=pt.index.tolist(),
        data=data,
        query=user_input,
    )

if __name__ == '__main__':
    app.run(debug=True)
