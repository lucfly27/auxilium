import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
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
        CREATE TABLE IF NOT EXISTS fiche (
            id_fiche INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur INT NOT NULL,
            id_niveau INT NOT NULL,
            id_matiere INT NOT NULL,
            img_url TEXT UNIQUE NOT NULL,
            img_check INTEGER NOT NULL 
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS niveau (
            id_niveau INTEGER PRIMARY KEY AUTOINCREMENT,
            abreviation TEXT NOT NULL,
            nom TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matiere (
            id_matiere INTEGER PRIMARY KEY AUTOINCREMENT,
            id_niveau INT NOT NULL,
            abreviation TEXT NOT NULL,
            nom TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signalement (
            id_signalement INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur INT NOT NULL,
            id_fiche INT NOT NULL,
            message TEXT NOT NULL  
        );
    ''')

    cursor.execute('SELECT COUNT(*) FROM utilisateurs WHERE id_utilisateur = ? AND username = ?', ('1', 'admin'))
    exist = cursor.fetchone()[0]

    if not exist:
        admin_password = 'scrypt:32768:8:1$hok6AfH4DTJQWwAm$4c4b7cbd977b84a9ce09489fde5c7249c92a7736c1c8e8b5bbefc1c157ba1c407f50c81d484965b68659da75773cc418f3d454f73bb2af67328e09c20c25daa9'
        cursor.execute('INSERT INTO utilisateurs (username, email, password) VALUES (?, ?, ?)', ('admin', 'luccas3684@gmail.com', admin_password))


    cursor.execute('SELECT COUNT(*) FROM niveau WHERE abreviation = ? AND nom = ?', ('2nd', 'seconde'))
    exist = cursor.fetchone()[0]

    if not exist:
        cursor.execute('INSERT INTO niveau (abreviation, nom) VALUES (?, ?)', ('2nd', 'seconde'))
        cursor.execute('INSERT INTO niveau (abreviation, nom) VALUES (?, ?)', ('1ere', 'premiere'))
        cursor.execute('INSERT INTO niveau (abreviation, nom) VALUES (?, ?)', ('Tle', 'terminale'))

    matieres = [
        ('1', 'Fr', 'Français'),
        ('2', 'Fr', 'Français'),
        ('1', 'Ma', 'Maths'),
        ('1', 'HG', 'Histoire Géographie'),
        ('2', 'HG', 'Histoire Géographie'),
        ('3', 'HG', 'Histoire Géographie'),
        ('1', 'EMC', 'Enseignement Moral et Civique'),
        ('2', 'EMC', 'Enseignement Moral et Civique'),
        ('3', 'EMC', 'Enseignement Moral et Civique'),
        ('1', 'En', 'Anglais'),
        ('2', 'En', 'Anglais'),
        ('3', 'En', 'Anglais'),
        ('1', 'Es', 'Espagnol'),
        ('2', 'Es', 'Espagnol'),
        ('3', 'Es', 'Espagnol'),
        ('1', 'It', 'Italien'),
        ('2', 'It', 'Italien'),
        ('3', 'It', 'Italien'),
        ('1', 'All', 'Allemand'),
        ('2', 'All', 'Allemand'),
        ('3', 'All', 'Allemand'),
        ('1', 'PC', 'Physique Chimie'),
        ('1', 'SVT', 'Sciences et Vie de la Terre'),
        ('1', 'SNI', 'Sciences Numériques et Informatiques'),
        ('2', 'ES', 'Enseignement Scientifique'),
        ('3', 'ES', 'Enseignement Scientifique'),
        ('1', 'EURO', 'Sections Européennes Anglais'),
        ('2', 'EURO', 'Sections Européennes Anglais'),
        ('3', 'EURO', 'Sections Européennes Anglais'),
        ('1', 'DNL', 'Sections Européennes DNL'),
        ('2', 'DNL', 'Sections Européennes DNL'),
        ('3', 'DNL', 'Sections Européennes DNL'),
        ('1', 'SES', 'Sciences Economiques et Sociales'),
        ('2', 'SES', 'Sciences Economiques et Sociales'),
        ('3', 'SES', 'Sciences Economiques et Sociales'),
        ('1', 'AP', 'Arts Plastiques'),
        ('2', 'AP', 'Arts Plastiques'),
        ('3', 'AP', 'Arts Plastiques'),
        ('2', 'SM', 'Spécialités Maths'),
        ('3', 'SM', 'Spécialités Maths'),
        ('2', 'SPC', 'Spécialités Physique Chimie'),
        ('3', 'SPC', 'Spécialités Physique Chimie'),
        ('2', 'SSVT', 'Spécialités Sciences et Vie de la Terre'),
        ('3', 'SSVT', 'Spécialités Sciences et Vie de la Terre'),
        ('2', 'NSI', 'Numérique Sciences Informatiques'),
        ('3', 'NSI', 'Numérique Sciences Informatiques'),
        ('2', 'HLP', 'Humanité Littérature et Philosophie'),
        ('3', 'HLP', 'Humanité Littérature et Philosophie'),
        ('2', 'HGGSP', 'Histoire Géographie Géopolitique et Sciences Politiques'),
        ('3', 'HGGSP', 'Histoire Géographie Géopolitique et Sciences Politiques'),
        ('2', 'LLCE', 'Langues Littérature et Civilisations Etrangères'),
        ('3', 'LLCE', 'Langues Littérature et Civilisations Etrangères')
    ]

    for niveau, abreviation, nom in matieres:
        cursor.execute('SELECT COUNT(*) FROM matiere WHERE id_niveau = ? AND abreviation = ? AND nom = ?', (niveau, abreviation, nom))
        exist = cursor.fetchone()[0]

        if not exist:
            cursor.execute('INSERT INTO matiere (id_niveau, abreviation, nom) VALUES (?, ?, ?)', (niveau, abreviation, nom))

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
    
    return redirect(url_for('accueil', modal=True))

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
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            flash('Cet utilisateur ou cet email existe déjà', 'error')
        finally:
            conn.close()

    return render_template('inscription.html')

@app.route('/get-matieres')
def get_matieres():
    niveau_id = request.args.get('niveau_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_matiere, nom FROM matiere WHERE id_niveau = ?', (niveau_id,))
    matieres = cursor.fetchall()
    conn.close()
    return jsonify({'matieres': [{'id_matiere': matiere['id_matiere'], 'nom': matiere['nom']} for matiere in matieres]})

def allowed_file(filename):
    """
    Vérifie si le fichier ne contient rien d'offensant
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/addcard', methods=['GET', 'POST'])
def addcard():
    """
    Ajoute une fiche au site en sélectionnant une matière, un niveau, une image.
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    if request.method == 'POST':
        username = session['username']
        matiere = request.form['matiere']
        niveau = request.form['niveau']
        image = request.files['image']
        if image and allowed_file(image.filename):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT abreviation FROM matiere WHERE id_matiere = ?", (matiere,))
            nom_matiere = cursor.fetchone()
            nom_matiere = nom_matiere['abreviation']
            cursor.execute("SELECT abreviation FROM niveau WHERE id_niveau = ?", (niveau,))
            nom_niveau = cursor.fetchone()
            nom_niveau = nom_niveau['abreviation']
            filename = f"fiche_auxilium_{nom_matiere}_{nom_niveau}"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                image.save("static/" + image_path) 
                cursor.execute('SELECT * FROM utilisateurs WHERE username = ?', (username,))
                id_user = cursor.fetchone()
                id_user = id_user['id_utilisateur']
                cursor.execute(
                    'INSERT INTO fiche (id_utilisateur, id_matiere, id_niveau, img_url, img_check) VALUES (?, ?, ?, ?, ?)', 
                    (id_user, matiere, niveau, image_path, '0')
                )
                conn.commit()
                flash('Fiche ajoutée avec succès!', 'success')
                username = session['username']
                print(f"{username} vient de demander à ajouter une fiche (Matière: {matiere}, Niveau: {niveau})")
            except Exception as e:
                print(f"Erreur: {str(e)}")
                flash("Erreur: Fiche non ajoutée", 'error')
            finally:
                if conn:
                    conn.close()
        else:
            flash('Type de fichier non autorisé', 'error')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_niveau, abreviation FROM niveau')
    niveaux = cursor.fetchall()
    conn.close()
    return render_template('addcard.html', niveaux=niveaux)

@app.route('/checkfiche')
def checkfiche():
    """
    Affiche les fiches pas encore traiter
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not session['username'] == 'admin':
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fiche.id_fiche, matiere.nom, niveau.abreviation, fiche.img_url FROM fiche
        JOIN matiere on matiere.id_matiere = fiche.id_matiere
        JOIN niveau on niveau.id_niveau = fiche.id_niveau
        WHERE fiche.img_check = 0;
    ''')
    fiches = cursor.fetchall() 
    conn.close()

    return render_template('checkfiches.html', fiches=fiches)

@app.route('/accepterfiche/<int:id_fiche>')
def accepterfiche(id_fiche):
    """
    Accepte la publication d'une fiche avec son id
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not session['username'] == 'admin':
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE fiche
            SET img_check = 1
            WHERE id_fiche = ?
        ''', (id_fiche,))

        conn.commit()
        fiches = cursor.fetchall() 
        conn.close()

        return redirect(url_for('checkfiche'))

@app.route('/supprimerfiche/<int:id_fiche>')
def supprimerfiche(id_fiche):
    """
    Supprime une fiche avec son id et remet a jour tout les id
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not session['username'] == 'admin':
        return redirect(url_for('fiches'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fiche WHERE id_fiche = ?', (id_fiche,))
        conn.commit()

        cursor.execute('''
            UPDATE fiche
            SET id_fiche = id_fiche - 1
            WHERE id_fiche > ?;
        ''', (id_fiche,))
        conn.commit()

        # Reintialiser l'auto incrementation de la table fiche
        cursor.execute('''DELETE FROM sqlite_sequence WHERE name='fiche';''')
        conn.commit()

        fiches = cursor.fetchall() 
        conn.close()

        return redirect(url_for('checkfiche'))

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
    cursor.execute('''
        SELECT fiche.id_fiche, matiere.nom, niveau.abreviation, fiche.img_url FROM fiche
        JOIN matiere on matiere.id_matiere = fiche.id_matiere
        JOIN niveau on niveau.id_niveau = fiche.id_niveau
        WHERE fiche.img_check = 1;
    ''')
    fiches = cursor.fetchall() 
    conn.close()

    return render_template('fiches.html', fiches=fiches)

@app.route('/fiches/<int:id_fiche>')
def fiche_detail(id_fiche):
    """
    Affiche les détails d'une fiche spécifique en fonction de son ID
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fiche.id_fiche, matiere.nom, niveau.abreviation, fiche.img_url FROM fiche
        JOIN matiere on matiere.id_matiere = fiche.id_matiere
        JOIN niveau on niveau.id_niveau = fiche.id_niveau
        WHERE img_check = 1 AND id_fiche = ?
    ''', (id_fiche,))
    fiche = cursor.fetchone()
    conn.close()

    if fiche is None:
        flash("Fiche non trouvée", 'error')
        return redirect(url_for('fiches'))

    return render_template('fiche.html', fiche=fiche) 

@app.route('/fiches/<string:matiere>')
def fiche_tri_matiere(matiere):
    """
    Affiche les fiches d'une certaine matière.
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    
    matiere = matiere[0].upper() + matiere[1:]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM fiche WHERE matiere = ? LIMIT 1', (matiere,))
    matiere_exist = cursor.fetchone()

    if not matiere_exist:
        flash('Matière non trouvée', 'error')
        conn.close()
        return redirect(url_for('fiches'))  

    cursor.execute('SELECT * FROM fiche WHERE matiere = ?', (matiere,))
    fiches = cursor.fetchall()

    conn.close()

    return render_template('fiches.html', fiches=fiches)

@app.route('/signaler', methods=['GET', 'POST'])
def signaler():
    """
    Signaler une fiche ce qui l'envoie dans la page fiche signaler.
    """
    

if __name__ == '__main__':
    init_db()
    host_ip = '' #for set an host ip
    if not host_ip == "":
        app.run(host=host_ip, port=5000, debug=True)
    else:
        app.run(debug=True)
