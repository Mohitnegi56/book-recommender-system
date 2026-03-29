from flask import Flask, render_template, request
import pickle
import numpy as np

popular_df = pickle.load(open('popular_df.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_score.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    # Clean input
    user_input = user_input.strip()

    # Fuzzy matching (important fix)
    matches = [book for book in pt.index if user_input.lower() in book.lower()]

    if len(matches) == 0:
        return render_template('recommend.html', error="❌ Book not found. Try another name.")

    user_input = matches[0]

    index = np.where(pt.index == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    data = []

    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')

        item = []
        item.extend(list(temp_df['Book-Title'].values))
        item.extend(list(temp_df['Book-Author'].values))
        item.extend(list(temp_df['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html', data=data)


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
