# app.py
from flask import Flask, render_template

app = Flask(__name__)

# Route principale pour la page d'accueil
@app.route('/')
def accueil():
    return render_template('accueil.html')

if __name__ == '__main__':
    app.run(debug=True)
