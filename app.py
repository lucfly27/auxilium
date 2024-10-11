import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'ta_cle_secrete'  # Clé secrète pour sécuriser les sessions


def get_db_connection():
    """
    Fonction pour se connecter à la base de données
    """
    conn = sqlite3.connect('utilisateurs.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def accueil():
    return render_template('accueil.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Se connecte à la base de données, recherche l'utilisateur et le stock dans la session
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM utilisateurs WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash(f'Bienvenue {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')  

        conn.close()

    return render_template('accueil.html')


@app.route('/home')
def home():
    """
    Affiche la page d'accueil avec le nom d'utilisateur
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login'))
    
    username = session['username']
    return render_template('home.html', username=username)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('accueil'))

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """
    Se connecte a la bdd, insere les données et les sauvegardes 
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hash(request.form['password']) 

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO utilisateurs (username, email, password) VALUES (?, ?, ?)', 
                           (username, email, password))
            conn.commit()  # Sauvegarde des modifications
            flash(f'Compte créé avec succès pour {username}!', 'success')
            return redirect(url_for('accueil'))
        except sqlite3.IntegrityError:
            flash('Cet utilisateur ou cet email existe déjà', 'error')
        conn.close()

    return render_template('inscription.html')

if __name__ == '__main__':
    app.run(debug=True)
