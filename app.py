from flask import Flask, render_template, request, redirect, url_for, flash
import duckdb
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this for production

# Initialize DuckDB database
def init_db():
    conn = duckdb.connect('movies.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            year INTEGER,
            title VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_movie', methods=['POST'])
def add_movie():
    year = request.form.get('year')
    title = request.form.get('title')
    
    if not year or not title:
        flash('Both year and title are required!', 'error')
        return redirect(url_for('index'))
    
    try:
        year = int(year)
    except ValueError:
        flash('Year must be a valid number!', 'error')
        return redirect(url_for('index'))
    
    try:
        conn = duckdb.connect('movies.db')
        # Get the maximum ID to generate a new one
        result = conn.execute('SELECT COALESCE(MAX(id), 0) FROM movies').fetchone()
        new_id = result[0] + 1 if result else 1
        
        conn.execute(
            'INSERT INTO movies (id, year, title) VALUES (?, ?, ?)',
            (new_id, year, title)
        )
        conn.close()
        
        flash('Movie added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding movie: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/show_movies')
def show_movies():
    try:
        conn = duckdb.connect('movies.db')
        movies = conn.execute('SELECT id, year, title, created_at FROM movies ORDER BY created_at DESC').fetchall()
        conn.close()
        
        # Convert to list of dictionaries for easier template handling
        movies_list = []
        for movie in movies:
            movies_list.append({
                'id': movie[0],
                'year': movie[1],
                'title': movie[2],
                'created_at': movie[3]
            })
            
        return render_template('results.html', movies=movies_list)
    except Exception as e:
        flash(f'Error retrieving movies: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)