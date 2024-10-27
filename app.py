import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'une_cle_secrete'  # Clé secrète pour sécuriser les sessions

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    """
    Fonction pour se connecter à la base de données
    """
    conn = sqlite3.connect('auxilium.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def accueil():
    return render_template('accueil.html')

def init_db():
    """
    Crée la base de données et les tables si elles n'existent pas.
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
            matiere TEXT NOT NULL,
            niveau TEXT NOT NULL,
            image_url TEXT NOT NULL
        );
    ''')

    conn.commit()  
    conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Se connecte à la base de données et connecte l'utilisateurs
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
            print(username, "vient de se connecter")
            return redirect(url_for('home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
            return redirect(url_for('accueil', modal=True))
        conn.close()
    
    return render_template('accueil.html')

@app.route('/home')
def home():
    """
    Affiche la page d'accueil
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
    Inscription d'un nouvel utilisateur
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
        finally:
            conn.close()

    return render_template('inscription.html')

def allowed_file(filename):
    """
    Vérifie si le fichier ne contient rien d'offensant
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/addcard', methods=['GET', 'POST'])
def addcard():
    """
    Ajoute une fiche au site en selectionant une matiere, un niveau, une image
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    if request.method == 'POST':
        matiere = request.form['matiere']
        niveau = request.form['niveau']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            conn=None
            try:
                image.save("static/" + image_path) 
                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute('INSERT INTO fiche (matiere, niveau, image_url) VALUES (?, ?, ?)', 
                               (matiere, niveau, image_path))
                conn.commit()
                flash('Fiche ajoutée avec succès!', 'success')
                username = session['username']
                print(f"{username} vient d'ajouter une fiche ({matiere},{niveau})")
            except Exception as e:
                print(f"Erreur: {str(e)}")
                flash("Erreur: Fiche non ajoutée", 'error')
            finally:
                if conn:
                    conn.close()
        else:
            flash('Type de fichier non autorisé', 'error')
    return render_template('addcard.html')

@app.route('/fiches')
def fiches():
    """
    Affiche les fiches dans une page
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fiche')
    fiches = cursor.fetchall() 

    conn.close()

    return render_template('fiches.html', fiches=fiches)

@app.route('/fiches/<int:fiche_id>')
def fiche_detail(fiche_id):
    """
    Affiche les détails d'une fiche spécifique en fonction de son ID
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fiche WHERE id = ?', (fiche_id,))
    fiche = cursor.fetchone()
    conn.close()

    if fiche is None:
        flash("Fiche non trouvée", 'error')
        return redirect(url_for('fiches'))

    return render_template('fiche.html', fiche=fiche) 

if __name__ == '__main__':
    init_db()
    host_ip = '' #for set an host ip
    if not host_ip == "":
        app.run(host=host_ip, port=5000, debug=True)
    else:
        app.run(debug=True)
