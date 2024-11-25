import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import unicodedata

app = Flask(__name__)
app.secret_key = 'une_cle_secrete'  # Clé secrète pour sécuriser les sessions

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def transformer_chaine(chaine):
    """
    Prend une chaine de caractere remplace les espaces par des _, enleve les accents et met tout en minuscule
    """
    chaine = chaine.replace(" ", "_")
    chaine = unicodedata.normalize('NFD', chaine)
    chaine = ''.join(c for c in chaine if unicodedata.category(c) != 'Mn')
    chaine = chaine.lower()
    return chaine

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
        CREATE TABLE IF NOT EXISTS signalements (
            id_signalement INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur INT NOT NULL,
            id_fiche INT NOT NULL,
            message TEXT NOT NULL  
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tag (
            id_tag INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_tag TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiche_tag (
            id_fiche INT NOT NULL,
            id_tag INT NOT NULL
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
        tags = request.form['tags']
        nv_tag = False
        tag = ''
        liste_tags = []
        for caractere in tags:
            if caractere == '#':
                if nv_tag == True:
                    liste_tags.append(tag)
                    tag = ''
                    tag += caractere
                elif nv_tag == False:
                    nv_tag = True
                    tag += caractere
            else:
                tag += caractere
        if not tag == '':
            liste_tags.append(tag)
                            
        if image and allowed_file(image.filename):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT abreviation FROM matiere WHERE id_matiere = ?", (matiere,))
            nom_matiere = cursor.fetchone()
            nom_matiere = nom_matiere['abreviation']
            cursor.execute("SELECT abreviation FROM niveau WHERE id_niveau = ?", (niveau,))
            nom_niveau = cursor.fetchone()
            nom_niveau = nom_niveau['abreviation']
            filename = f"{nom_matiere}_{nom_niveau}_{str(uuid.uuid4())}"
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
                if len(liste_tags) > 0: 
                    liste_tags = [tag.strip() for tag in liste_tags if type(tag) == str]
                    for tag in liste_tags:
                        tag = transformer_chaine(tag)
                        cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (tag,))
                        existing_tag = cursor.fetchone()
                        if not existing_tag:
                            cursor.execute('INSERT INTO tag (nom_tag) VALUES (?)', (tag,))
                            cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (tag,))
                            existing_tag = cursor.fetchone()
                        cursor.execute('SELECT id_fiche FROM fiche WHERE img_url = ?', (image_path,))
                        id_fiche = cursor.fetchone()
                        cursor.execute('INSERT INTO fiche_tag (id_fiche, id_tag) VALUES (?, ?)', (id_fiche[0], existing_tag[0],))
                conn.commit()
                flash('Fiche ajoutée avec succès!', 'success')
                username = session['username']
                print(f"{username} vient de demander à ajouter une fiche (Matière: {matiere}, Niveau: {niveau}, avec les tags {liste_tags})")
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

@app.route('/checkrequest')
def checkrequest():
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
        SELECT 
            fiche.id_fiche, 
            matiere.nom, 
            niveau.abreviation, 
            fiche.img_url,
            GROUP_CONCAT(tag.nom_tag, ', ') AS tags 
        FROM 
            fiche
        JOIN matiere ON matiere.id_matiere = fiche.id_matiere
        JOIN niveau ON niveau.id_niveau = fiche.id_niveau
        LEFT JOIN fiche_tag ON fiche_tag.id_fiche = fiche.id_fiche
        LEFT JOIN tag ON fiche_tag.id_tag = tag.id_tag
        WHERE 
            fiche.img_check = 0
        GROUP BY
            fiche.id_fiche;
    ''')
    fiches = cursor.fetchall()
    conn.close()

    return render_template('checkrequest.html', fiches=fiches)

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

        return redirect(url_for('checkrequest'))

@app.route('/supprimerfiche/<int:id_fiche>')
def supprimerfiche(id_fiche):
    """
    Supprime une fiche avec son id et remet à jour tous les id.
    Supprime également l'image associée du dossier des uploads.
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif session['username'] != 'admin':
        return redirect(url_for('fiches'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT img_url FROM fiche WHERE id_fiche = ?', (id_fiche,))
        fiche = cursor.fetchone()
        
        if fiche:
            image_path = fiche['img_url']
            cursor.execute('DELETE FROM fiche WHERE id_fiche = ?', (id_fiche,))
            cursor.execute('DELETE FROM fiche_tag WHERE id_fiche = ?', (id_fiche,))
            conn.commit()

            cursor.execute('''
                UPDATE fiche
                SET id_fiche = id_fiche - 1
                WHERE id_fiche > ?;
            ''', (id_fiche,))
            conn.commit()

            cursor.execute("DELETE FROM sqlite_sequence WHERE name='fiche';")
            conn.commit()

            full_image_path = os.path.join('static', image_path)
            if os.path.exists(full_image_path):
                try:
                    os.remove(full_image_path)
                    flash('Fiche et image supprimées avec succès!', 'success')
                    print(f'fiche id:{id_fiche} supprimée')
                except Exception as e:
                    flash(f"Erreur lors de la suppression de l'image: {str(e)}", 'error')
            else:
                flash('Image associée introuvable, mais fiche supprimée.', 'error')
                print(f'fiche id:{id_fiche} supprimée de la bdd mais image non trouvée')
        else:
            flash('Fiche introuvable.', 'error')

        conn.close()

        return redirect(url_for('home'))

@app.route('/othertag/<int:id_fiche>', methods=['GET', 'POST'])
def other_tags(id_fiche):
    '''
    Accepte la publication d'une fiche avec son id mais avec d'autre tag que ceux mis par l'utilisateurs 
    '''
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not session['username'] == 'admin':
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))

    if request.method == 'POST':
        tags = request.form['tags']
        nv_tag = False
        tag = ''
        liste_tags = []
        for caractere in tags:
            if caractere == '#':
                if nv_tag == True:
                    liste_tags.append(tag)
                    tag = ''
                    tag += caractere
                elif nv_tag == False:
                    nv_tag = True
                    tag += caractere
            elif caractere == ' ':
                liste_tags.append(tag)
                tag= ''
                nv_tag = False
            else:
                tag += caractere
        if not tag == '':
            liste_tags.append(tag)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM fiche_tag WHERE id_fiche = ?', (id_fiche,))
        if len(liste_tags) > 0: 
                    liste_tags = [tag.strip() for tag in liste_tags if type(tag) == str]
                    for tag in liste_tags:
                        tag = transformer_chaine(tag)
                        cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (tag,))
                        existing_tag = cursor.fetchone()
                        if not existing_tag:
                            cursor.execute('INSERT INTO tag (nom_tag) VALUES (?)', (tag,))
                            cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (tag,))
                            existing_tag = cursor.fetchone()
                        cursor.execute('INSERT INTO fiche_tag (id_fiche, id_tag) VALUES (?, ?)', (id_fiche, existing_tag[0],))
        cursor.execute('''
            UPDATE fiche
            SET img_check = 1
            WHERE id_fiche = ?
        ''', (id_fiche,))
        conn.commit()
        fiches = cursor.fetchall() 
        conn.close()

        return redirect(url_for('checkrequest'))

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
        SELECT 
            fiche.id_fiche, 
            matiere.nom, 
            niveau.abreviation, 
            fiche.img_url, 
            GROUP_CONCAT(tag.nom_tag, ', ') AS tags 
        FROM 
            fiche
        JOIN matiere ON matiere.id_matiere = fiche.id_matiere
        JOIN niveau ON niveau.id_niveau = fiche.id_niveau
        LEFT JOIN fiche_tag ON fiche_tag.id_fiche = fiche.id_fiche
        LEFT JOIN tag ON fiche_tag.id_tag = tag.id_tag
        WHERE 
            fiche.img_check = 1
        GROUP BY 
            fiche.id_fiche;
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
        SELECT 
            fiche.id_fiche, 
            matiere.nom, 
            niveau.abreviation, 
            fiche.img_url, 
            GROUP_CONCAT(tag.nom_tag, ', ') AS tags 
        FROM 
            fiche
        JOIN matiere ON matiere.id_matiere = fiche.id_matiere
        JOIN niveau ON niveau.id_niveau = fiche.id_niveau
        LEFT JOIN fiche_tag ON fiche_tag.id_fiche = fiche.id_fiche
        LEFT JOIN tag ON fiche_tag.id_tag = tag.id_tag
        WHERE 
            fiche.img_check = 1 AND fiche.id_fiche = ?
        GROUP BY 
            fiche.id_fiche;
    ''', (id_fiche,))
    fiche = cursor.fetchone()
    conn.close()

    if fiche is None:
        flash("Fiche non trouvée", 'error')
        return redirect(url_for('fiches'))

    return render_template('fiche.html', fiche=fiche) 

@app.route('/signaler', methods=['GET', 'POST'])
def signaler():
    """
    Signaler une fiche ce qui l'envoie dans la page fiche signaler.
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    if request.method == "POST":
        username = session['username']
        message = request.form['content']
        id_fiche = request.form['id_fiche']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM utilisateurs WHERE username = ?', (username,))
            id_user = cursor.fetchone()
            id_user = id_user['id_utilisateur']
            cursor.execute(
                'INSERT INTO signalements (id_utilisateur, id_fiche, message) VALUES (?, ?, ?)', 
                (id_user, id_fiche, message)
            )
            conn.commit()
            flash("Fiche bien signaler, on vous remercie de participer au bon fonctionnement du site !")
        except Exception as e:
            print(f"Erreur: {str(e)}")
            flash("Erreur: Fiche non signalée", 'error')
        finally:
            if conn:
                conn.close()

    username = session['username']
    print(f"{username} vient de signaler une fiche")

    return redirect(url_for('fiches', id_fiche = id_fiche))

@app.route('/checkreport')
def checkreport():
    """
    Affiche les signalements non traités
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif session['username'] != 'admin':
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT signalements.id_signalement, utilisateurs.username, signalements.message, fiche.id_fiche, fiche.img_url  
        FROM signalements
        JOIN utilisateurs ON utilisateurs.id_utilisateur = signalements.id_utilisateur
        JOIN fiche ON fiche.id_fiche = signalements.id_fiche;
    ''')
    signalements = cursor.fetchall()
    conn.close()

    return render_template('checkreport.html', signalements=signalements)

@app.route('/skipreport/<int:id_signalement>')
def ignorer_signalement(id_signalement):
    """
    Pour ignorer un signalement
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif session['username'] != 'admin':
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))
    try: 
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM signalements WHERE id_signalement = ?', (id_signalement,))
        conn.commit()
    except Exception as e:
        print(f"Erreur: {str(e)}")
        flash("Erreur: Fiche non signalée", 'error')
    finally:
        if conn:
            conn.close()        
    return redirect(url_for('checkreport'))

@app.route('/search')
def search():
    """
    Rechercher une fiche avec un tag
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    tag = request.args.get('tag')
    tag = transformer_chaine(tag)
    if not tag:
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (tag,))
    id_tag = cursor.fetchone()
    if not id_tag:
        tag = "#" + tag
        cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (tag,))
        id_tag = cursor.fetchone()
        if not id_tag:
            flash('Aucun résultat trouvé pour ce tag.', 'info')
            conn.close()
            return redirect(url_for('home'))

    cursor.execute('''
        SELECT 
            fiche.id_fiche, 
            matiere.nom, 
            niveau.abreviation, 
            fiche.img_url, 
            GROUP_CONCAT(tag.nom_tag, ', ') AS tags 
        FROM 
            fiche
        JOIN matiere ON matiere.id_matiere = fiche.id_matiere
        JOIN niveau ON niveau.id_niveau = fiche.id_niveau
        LEFT JOIN fiche_tag ON fiche_tag.id_fiche = fiche.id_fiche
        LEFT JOIN tag ON fiche_tag.id_tag = tag.id_tag
        WHERE 
            fiche.img_check = 1
            AND fiche_tag.id_tag = ?
        GROUP BY 
            fiche.id_fiche;
    ''', (id_tag[0],))
    fiches = cursor.fetchall()
    conn.close()

    return render_template('fiches.html', fiches=fiches)

@app.route('/userrequest')
def userrequest():
    """
    Permet a un utilisateurs de voir les fiches qu'il a ajouter et/ou demander a ajouter
    """
    if "username" not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_utilisateur FROM utilisateurs WHERE username  = ?', (username,))
    id_utilisateur = cursor.fetchone()
    cursor.execute('''
        SELECT 
            fiche.id_fiche, 
            matiere.nom, 
            niveau.abreviation, 
            fiche.img_url,
            fiche.img_check,
            GROUP_CONCAT(tag.nom_tag, ', ') AS tags 
        FROM 
            fiche
        JOIN matiere ON matiere.id_matiere = fiche.id_matiere
        JOIN niveau ON niveau.id_niveau = fiche.id_niveau
        LEFT JOIN fiche_tag ON fiche_tag.id_fiche = fiche.id_fiche
        LEFT JOIN tag ON fiche_tag.id_tag = tag.id_tag
        WHERE 
            fiche.id_utilisateur = ?
        GROUP BY
            fiche.id_fiche;
    ''', id_utilisateur)
    fiches = cursor.fetchall()
    conn.close()

    return render_template('userrequest.html', fiches=fiches)


if __name__ == '__main__':
    init_db()
    host_ip = '' #for set an host ip
    if not host_ip == "":
        app.run(host=host_ip, port=5000, debug=True)
    else:
        app.run(debug=True)
