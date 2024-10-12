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

def init_db():
    """
    Crée la base de données et la table utilisateurs si elles n'existent pas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiche (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere TEXT UNIQUE NOT NULL,
            niveau TEXT NOT NULL
        );
    ''')

    conn.commit()  # Sauvegarde les modifications
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Se connecte à la base de données, recherche l'utilisateur et le stocke dans la session
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
            return redirect(url_for('home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
            return redirect(url_for('accueil', modal=True))
        conn.close()
    return render_template('accueil.html')



@app.route('/home')
def home():
    """
    Affiche la page d'accueil avec le nom d'utilisateur
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    
    username = session['username']
    return render_template('home.html', username=username)

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        session.pop('username', None)
        print(username, "vient de se deconnecter")
    return redirect(url_for('accueil'))

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """
    Se connecte a la bdd, insere les données et les sauvegardes 
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password']) 

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO utilisateurs (username, email, password) VALUES (?, ?, ?)', 
                           (username, email, password))
            conn.commit()  
            print(f'Compte créé avec succès pour {username}!')
            return redirect(url_for('accueil'))
        except sqlite3.IntegrityError:
            flash('Cet utilisateur ou cet email existe déjà', 'error')
        conn.close()

    return render_template('inscription.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
