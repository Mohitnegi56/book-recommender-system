from flask import Flask, render_template, request, jsonify
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


@app.route('/autocomplete')
def autocomplete():
    query = request.args.get('q')

    suggestions = [book for book in pt.index if query.lower() in book.lower()][:10]

    return jsonify(suggestions)


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input').strip()

    matches = [book for book in pt.index if user_input.lower() in book.lower()]

    if len(matches) == 0:
        return render_template('recommend.html', error="Book not found")

    user_input = matches[0]

    index = np.where(pt.index == user_input)[0][0]

    similar_items = list(enumerate(similarity_scores[index]))

    ranked = []
    for i, score in similar_items:
        book_title = pt.index[i]
        temp_df = books[books['Book-Title'] == book_title].drop_duplicates('Book-Title')

        if temp_df.shape[0] == 0:
            continue

        rating = temp_df['Book-Rating'].values[0] if 'Book-Rating' in temp_df else 5
        weighted_score = score * 0.7 + (rating / 10) * 0.3  # hybrid score

        ranked.append((i, weighted_score))

    ranked = sorted(ranked, key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in ranked:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')

        item = []
        item.extend(list(temp_df['Book-Title'].values))
        item.extend(list(temp_df['Book-Author'].values))
        item.extend(list(temp_df['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
