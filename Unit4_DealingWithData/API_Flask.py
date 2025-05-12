from flask import Flask, jsonify, abort, request
import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='sakila'
)

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'

@app.get('/actors')
def actors():
    query = 'SELECT actor_id, first_name, last_name FROM actor'
    results = get_results(query)
    return results

@app.get('/actors/<int:actor_id>')
def actor(actor_id):
    query = 'SELECT * FROM actor WHERE actor_id = %s'
    result = get_one_result(query, (actor_id,))
    return result

@app.get('/films')
def get_films_by_rating():
    ratings = request.args['rating'].split(',')
    query_placeholders = ','.join(['%s'] * len(ratings))
    query = (
        'SELECT film_id, description, release_year, length, rental_rate, rating '
        'FROM film '
        'WHERE rating IN (%s)' % query_placeholders
    )
    results = get_results(query, ratings)
    return results


def get_results(query, *args):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, *args)
    results = cursor.fetchall()
    cursor.close()
    return jsonify(results) if results else abort(404)

def get_one_result(query, *args):
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, *args)
    result = cursor.fetchone()
    cursor.close()
    return jsonify(result) if result else abort(404)

if __name__ == '__main__':
    app.run(debug=True)
