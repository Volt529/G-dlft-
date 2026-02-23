import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']

    # Vérifier si le mail existe
    club = next((c for c in clubs if c['email'] == email), None)

    if club is None:
        flash("❌ Cette adresse e-mail n'existe pas dans la base de données.")
        return render_template("index.html")

    return render_template("welcome.html", club=club, competitions=competitions)

@app.route('/book/<competition>/<club>')
def book(competition, club):
    # On sécurise la récupération
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)

    # Si un des deux est introuvable -> erreur propre
    if foundClub is None or foundCompetition is None:
        flash("❌ Club ou compétition introuvable.")
        return redirect(url_for('index'))

    # Sinon on affiche bien la page booking
    return render_template('booking.html', club=foundClub, competition=foundCompetition)

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if competition is None or club is None:
        flash("Erreur interne.")
        return redirect(url_for('index'))

    placesRequired = int(request.form['places'])

    # BUG 4 — Max 12 places
    if placesRequired > 12:
        flash("Erreur : vous ne pouvez pas réserver plus de 12 places.")
        return render_template('booking.html', club=club, competition=competition)

    # BUG 2 — pas plus que les places restantes
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Erreur : pas assez de places disponibles.")
        return render_template('booking.html', club=club, competition=competition)

    # BUG 3 — vérifier les points du club
    if placesRequired > int(club['points']):
        flash("Erreur : vous n'avez pas assez de points.")
        return render_template('booking.html', club=club, competition=competition)

    # Si tout est OK → mise à jour des places
    competition['numberOfPlaces'] = str(int(competition['numberOfPlaces']) - placesRequired)
    club['points'] = str(int(club['points']) - placesRequired)

    flash("Réservation effectuée avec succès !")
    return render_template('welcome.html', club=club, competitions=competitions)

@app.route('/points')
def points():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))