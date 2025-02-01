import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
import unicodedata

app = Flask(__name__)
app.secret_key = 'une_cle_secrete'  # cle secrete

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

niveaux = [
        ('2nd', 'seconde'),
        ('1ere', 'premiere'),
        ('Tle', 'terminale')
    ]

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
def homepage():
    return render_template('homepage.html')

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
            password TEXT NOT NULL,
            admin_perm INT NOT NULL
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favoris (
            id_favori INTEGER PRIMARY KEY AUTOINCREMENT,
            id_utilisateur INT NOT NULL,
            id_fiche INT NOT NULL
        );
    ''')


    cursor.execute('SELECT COUNT(*) FROM niveau WHERE abreviation = ? AND nom = ?', ('2nd', 'seconde'))
    exist = cursor.fetchone()[0]

    for abreviation, nom in niveaux:
        cursor.execute('SELECT COUNT(*) FROM niveau WHERE abreviation = ? AND nom = ?', (abreviation, nom))
        exist = cursor.fetchone()[0]
    
        if not exist:
                cursor.execute('INSERT INTO niveau (abreviation, nom) VALUES (?, ?)', (abreviation, nom))


    for niveau, abreviation, nom in matieres:
        cursor.execute('SELECT COUNT(*) FROM matiere WHERE id_niveau = ? AND abreviation = ? AND nom = ?', (niveau, abreviation, nom))
        exist = cursor.fetchone()[0]

        if not exist:
            cursor.execute('INSERT INTO matiere (id_niveau, abreviation, nom) VALUES (?, ?, ?)', (niveau, abreviation, nom))

    conn.commit()  
    conn.close()

def check_admin(username):
    """
    Renvoi un booleen pour savoir si l'utilisateurs est admin ou pas
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT admin_perm FROM utilisateurs WHERE username = ?', (username,))
    admin_perm = cursor.fetchone()
    conn.close()

    if admin_perm and admin_perm[0] == 1:  
        return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Se connecte à la base de données et connecte l'utilisateurs
    """
    if request.method == 'POST':
        username = " "
        for c in request.form['username']:
            if c != ' ':
                username += c
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM utilisateurs WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            print(username, "vient de se connecter")
            return redirect(url_for('accueil'))
        elif user:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
            return redirect(url_for('homepage', modal=True))
        else:
            flash('Nom d\'utilisateur non existant', 'error')
            return redirect(url_for('homepage', modal=True))
        conn.close()
    
    return redirect(url_for('homepage', modal=True))

@app.route('/accueil')
def accueil():
    """
    Affiche la page d'accueil
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    
    return render_template('accueil.html', username=session['username'], perm=check_admin(session['username']))

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        session.pop('username', None)
        print(username, "vient de se deconnecter")
    return redirect(url_for('homepage'))

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    """
    Inscription d'un nouvel utilisateur
    """
    if request.method == 'POST':
        username = " "
        for c in request.form['username']:
            if c != ' ':
                username += c
        email = request.form['email']
        password = generate_password_hash(request.form['password']) 

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO utilisateurs (username, email, password, admin_perm) VALUES (?, ?, ?, ?)', 
                           (username, email, password, 0))
            conn.commit()  
            print(f'Compte créé avec succès pour {username}!')
            return redirect(url_for('accueil'))
        except sqlite3.IntegrityError:
            flash('Cet utilisateur ou cet email existe déjà', 'error')
        finally:
            conn.close()

    return render_template('inscription.html')

@app.route('/supprimerutilisateur/<int:id_user>')
def supprimerutilisateur(id_user):
    """
    Supprime un utilisateurs avec son id et remet à jour tous les id
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
        return redirect(url_for('accueil'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM utilisateurs WHERE id_utilisateur = ?', (id_user,))
        exist = cursor.fetchall()

        if exist:
            cursor.execute('DELETE FROM utilisateurs WHERE id_utilisateur = ?', (id_user,))
            cursor.execute('''
                UPDATE utilisateurs
                SET id_utilisateur = id_utilisateur - 1
                WHERE id_utilisateur > ?;
            ''', (id_user,))
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='utilisateurs';")
            flash('Utilisateur supprimée avec succés !', 'succes')
            print(f'Utilisateur id={id_user} supprimée')
        else:
            flash('Utilisateur introuvable', 'error')


        conn.commit()
        conn.close()

        return redirect(url_for('listuser'))

@app.route('/get-matieres')
def get_matieres():
    """
    Permet d'envoyer au front les matieres selon le niveau selectionner lors de l'ajout de fiches
    """
    niveau_id = request.args.get('niveau_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_matiere, nom FROM matiere WHERE id_niveau = ?', (niveau_id,))
    matieres = cursor.fetchall()
    conn.close()
    return jsonify({'matieres': [{'id_matiere': matiere['id_matiere'], 'nom': matiere['nom']} for matiere in matieres]})

def allowed_file(filename):
    """
    Vérifie si le fichier est au bon format pour etre une image
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/addcard', methods=['GET', 'POST'])
def addcard():
    """
    Ajoute une fiche au site en sélectionnant une matière, un niveau, une image
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
    return render_template('addcard.html', niveaux=niveaux, username=session['username'], perm=check_admin(session['username']))

@app.route('/checkrequest')
def checkrequest():
    """
    Affiche les fiches pas encore traiter
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
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

    return render_template('checkrequest.html', fiches=fiches, username=session['username'], perm=check_admin(session['username']))

@app.route('/accepterfiche/<int:id_fiche>')
def accepterfiche(id_fiche):
    """
    Accepte la publication d'une fiche avec son id
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
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
    Supprime une fiche avec son id et remet à jour tous les id
    Supprime également l'image associée du dossier des uploads
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
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

        return redirect(url_for('accueil'))

@app.route('/othertag/<int:id_fiche>', methods=['GET', 'POST'])
def other_tags(id_fiche):
    '''
    Accepte la publication d'une fiche avec son id mais avec d'autre tag que ceux mis par l'utilisateurs 
    '''
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
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

def infavoris():
    """
    Permet d'avoir une liste des fiches qu'un utilisateurs a deja mis en favoris
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_utilisateur FROM utilisateurs WHERE username = ?', (session['username'],))
    id_user = cursor.fetchone()[0]
    cursor.execute('SELECT id_fiche FROM favoris WHERE id_utilisateur = ?', (id_user,))
    favoris = [fav[0] for fav in cursor.fetchall()]
    conn.close()
    return favoris

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

    cursor.execute('SELECT id_niveau, abreviation FROM niveau')
    niveaux = cursor.fetchall()

    conn.close()
    return render_template('fiches.html', fiches=fiches, favoris=infavoris(), niveaux=niveaux, username=session['username'], perm=check_admin(session['username']))

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

    return render_template('fiche.html', fiche=fiche, username=session['username'], perm=check_admin(session['username'])) 

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

    return redirect(url_for('fiches', id_fiche = id_fiche, username=session['username'], perm=check_admin(session['username'])))

@app.route('/checkreport')
def checkreport():
    """
    Affiche les signalements non traités
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
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

    return render_template('checkreport.html', signalements=signalements, username=session['username'], perm=check_admin(session['username']))

@app.route('/skipreport/<int:id_signalement>')
def ignorer_signalement(id_signalement):
    """
    Pour ignorer un signalement
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
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
    Rechercher une fiche par niveaux, matieres et tags
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    search = request.args.get('search')
    search = transformer_chaine(search)
    if not search:
        return redirect(url_for('accueil'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    for abreviation, nom in niveaux:
        if abreviation == search or nom == search:
            if abreviation == search:
                cursor.execute('SELECT id_niveau FROM niveau WHERE abreviation = ?', (search,))
            elif nom == search:
                cursor.execute('SELECT id_niveau FROM niveau WHERE nom = ?', (search,))
            id_niveau = cursor.fetchone()
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
                    AND fiche.id_niveau = ?
                GROUP BY 
                    fiche.id_fiche;
            ''', (id_niveau[0],))

            fiches = cursor.fetchall()
            conn.close()

            return render_template('fiches.html', fiches=fiches, favoris=infavoris(), reset=1, username=session['username'], perm=check_admin(session['username']))

    for niveau, abreviation, nom in matieres:
        abv_init = abreviation
        nom_init = nom
        abreviation = transformer_chaine(abreviation)
        nom = transformer_chaine(nom)
        if abreviation == search or nom == search:
            if abreviation == search:
                cursor.execute('SELECT id_matiere FROM matiere WHERE abreviation = ?', (abv_init,))
            elif nom == search:
                cursor.execute('SELECT id_matiere FROM matiere WHERE nom = ?', (nom_init,))
            id_matieres = cursor.fetchall()
            fiches = []
            for id_m in id_matieres:
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
                        AND fiche.id_matiere = ?
                    GROUP BY 
                        fiche.id_fiche;
                ''', (id_m[0],))

                fiches += cursor.fetchall()
            
            conn.close()

            return render_template('fiches.html', fiches=fiches, favoris=infavoris(), reset=1, username=session['username'], perm=check_admin(session['username']))

    cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (search,))
    id_tag = cursor.fetchone()
    if not id_tag:
        search = "#" + search
        cursor.execute('SELECT id_tag FROM tag WHERE nom_tag = ?', (search,))
        id_tag = cursor.fetchone()
        if not id_tag:
            flash('Aucun résultat trouvé pour cette recherche.', 'info')
            conn.close()
            return redirect(url_for('accueil'))

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

    return render_template('fiches.html', fiches=fiches, favoris=infavoris(), reset=1, username=session['username'], perm=check_admin(session['username']))

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

    return render_template('userrequest.html', fiches=fiches, username=session['username'], perm=check_admin(session['username']))

@app.route('/userreport')
def userreport():
    """
    Affiche les signalements fais par un utilisateur
    """
    if "username" not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))

    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_utilisateur FROM utilisateurs WHERE username  = ?', (username,))
    id_utilisateur = cursor.fetchone()[0]
    cursor.execute('''
        SELECT 
            signalements.id_signalement, 
            utilisateurs.username, 
            signalements.message, 
            fiche.id_fiche, 
            fiche.img_url  
        FROM 
            signalements
        JOIN utilisateurs ON utilisateurs.id_utilisateur = signalements.id_utilisateur
        JOIN fiche ON fiche.id_fiche = signalements.id_fiche
        WHERE 
            utilisateurs.id_utilisateur = ?;
    ''', (id_utilisateur,))
    signalements = cursor.fetchall()
    conn.close()

    return render_template('userreport.html', signalements=signalements, username=session['username'], perm=check_admin(session['username']))

@app.route('/listuser')
def listuser():
    """
    Affiche les comptes inscrit sur le site; leur username, leur mail
    Permet de donner les perm admin
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            id_utilisateur,
            username,
            email,
            admin_perm
        FROM 
            utilisateurs;
    ''')
    utilisateurs = cursor.fetchall() 
    cursor.execute('SELECT COUNT(*) FROM utilisateurs;')
    nb_user = cursor.fetchone()[0]
    conn.close()

    return render_template('listuser.html', utilisateurs=utilisateurs, nb_user=nb_user, username=session['username'], perm=check_admin(session['username']))   

@app.route('/addadmin/<int:id_utilisateur>')
def addadmin(id_utilisateur):
    """
    Permet de donner les droits admin
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            admin_perm 
        FROM 
            utilisateurs 
        WHERE 
            id_utilisateur = ?;
    ''', (id_utilisateur,))
    perm = cursor.fetchone()[0]
    if perm == 0:
        cursor.execute('''
            UPDATE utilisateurs
            SET admin_perm = 1
            WHERE id_utilisateur = ?;
        ''', (id_utilisateur,))
        conn.commit()
        flash("Permission administrateur ajoutée")
        print(f"Utilisateurs id={id_utilisateur}, username={session['username']} est maintenant admin")
    else:
        flash("Cette utilisateur est deja admin")
    conn.close()
    return redirect(url_for('listuser'))

@app.route('/removeadmin/<int:id_utilisateur>')
def removeadmin(id_utilisateur):
    """
    Permet de retirer les droits admin
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    elif not check_admin(session['username']):
        flash("Vous ne pouvez pas accéder à ceci", 'error')
        return redirect(url_for('fiches'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            admin_perm 
        FROM 
            utilisateurs 
        WHERE 
            id_utilisateur = ?;
    ''', (id_utilisateur,))
    perm = cursor.fetchone()[0]
    if perm == 1:
        cursor.execute('''
            UPDATE utilisateurs
            SET admin_perm = 0
            WHERE id_utilisateur = ?;
        ''', (id_utilisateur,))
        conn.commit()
        flash("Permission administrateur retirée")
        print(f"Utilisateurs id={id_utilisateur}, username={session['username']} n'est maintenant plus admin")
    else:
        flash("Cette utilisateur est pas admin")
    conn.close()
    return redirect(url_for('listuser'))

@app.route('/sort', methods=['GET', 'POST'])
def sort():
    """
    Permet de trier les fiches a l'aide d'un bouton dans la page de présentation des fiches
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    if request.method == 'POST':
        niveau = request.form['niveau']
        matiere = request.form['matiere']
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
                niveau.id_niveau = ?
            AND
                matiere.id_matiere = ?
            GROUP BY 
                fiche.id_fiche;
        ''', (niveau, matiere))
        fiches = cursor.fetchall()

        conn.close()
        return render_template('fiches.html', fiches=fiches, favoris=infavoris(), reset=1, username=session['username'], perm=check_admin(session['username']))

@app.route('/addfavorite/<int:id_fiche>')
def addfavorite(id_fiche):
    '''
    Permet d'ajouter une fiche au favori
    '''
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM fiche WHERE id_fiche = ?;', (id_fiche,))
    exist = cursor.fetchone()
    if not exist:
        conn.close()
        flash('Aucune fiche avec cette id')
        return redirect(url_for('fiches'))
    username = session['username']
    cursor.execute('SELECT id_utilisateur FROM utilisateurs WHERE username = ?;', (username,))
    id_user = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM favoris WHERE id_fiche = ? AND id_utilisateur = ?;', (id_fiche, id_user,))
    exist = cursor.fetchone()
    if exist:
        conn.close()
        flash('Fiche déja en favoris')
        return redirect(url_for('fiches'))
    cursor.execute(
        'INSERT INTO favoris (id_utilisateur, id_fiche) VALUES (?, ?)',
        (id_user, id_fiche,)
    )
    conn.commit()
    conn.close()
    flash('Fiche ajoutée au favori !')
    print(f"Utilisateur id={id_user}, username={username} à maintenant la fiche id={id_fiche} en favori")
    return redirect(url_for('fiches'))

@app.route('/removefavorite/<int:id_fiche>')
def removefavorite(id_fiche):
    '''
    Permet de retirer une fiche de ses favoris
    '''
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    conn = get_db_connection()
    cursor = conn.cursor()
    username = session['username']
    cursor.execute('SELECT id_utilisateur FROM utilisateurs WHERE username = ?;', (username,))
    id_user = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM favoris WHERE id_fiche = ? AND id_utilisateur = ?;', (id_fiche, id_user,))
    exist = cursor.fetchone()
    if not exist:
        conn.close()
        flash('Vos favoris ne contienne pas cette fiche')
        return redirect(url_for('fiches'))
    cursor.execute('''
    SELECT 
        id_favori 
    FROM 
        favoris 
    WHERE 
        id_utilisateur = ?
    AND 
        id_fiche = ?
    ''', (id_user, id_fiche,))
    try:
        id_favori = cursor.fetchone()[0]
    except TypeError:
        flash("Vos favoris ne contiennent pas cette fiches")
        return redirect(url_for('fiches'))
    cursor.execute('DELETE FROM favoris WHERE id_favori = ?', (id_favori,))
    cursor.execute('''
        UPDATE favoris
        SET id_favori = id_favori - 1
        WHERE id_favori > ?;
    ''', (id_favori,))
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='favoris';")
    conn.commit()
    conn.close()
    flash('Fiche retirée des favoris !')
    print(f"Utilisateur id={id_user}, username={username} à enlevée la fiche id={id_fiche} de ses favoris")
    return redirect(url_for('fiches'))

@app.route('/favorite')
def favorite():
    """
    Permet de voir ses favoris
    """
    if 'username' not in session:
        flash('Veuillez vous connecter d\'abord', 'error')
        return redirect(url_for('login', modal=True))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_utilisateur FROM utilisateurs WHERE username = ?', (session['username'],))
    id_user = cursor.fetchone()[0]
    cursor.execute('''
        SELECT 
            fiche.id_fiche, 
            matiere.nom, 
            niveau.abreviation, 
            fiche.img_url, 
            GROUP_CONCAT(tag.nom_tag, ', ') AS tags 
        FROM 
            favoris
        JOIN fiche ON fiche.id_fiche = favoris.id_fiche
        JOIN matiere ON matiere.id_matiere = fiche.id_matiere
        JOIN niveau ON niveau.id_niveau = fiche.id_niveau
        LEFT JOIN fiche_tag ON fiche_tag.id_fiche = fiche.id_fiche
        LEFT JOIN tag ON fiche_tag.id_tag = tag.id_tag
        WHERE 
            favoris.id_utilisateur = ?
        GROUP BY 
            favoris.id_favori;
    ''', (id_user,))
    fiches = cursor.fetchall() 

    conn.close()
    return render_template('favorite.html', fiches=fiches, niveaux=niveaux, username=session['username'], perm=check_admin(session['username']))

if __name__ == '__main__':
    init_db()
    host_ip = '' #for set an host ip
    if not host_ip == "":
        app.run(host=host_ip, port=5000, debug=True)
    else:
        app.run(debug=True)
