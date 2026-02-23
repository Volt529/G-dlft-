import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from server import app


# ─── FIXTURE ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_data():
    """Remet les données à leur état initial avant chaque test"""
    import server
    server.clubs = json.loads(open(os.path.join(os.path.dirname(__file__), '../../clubs.json')).read())['clubs']
    server.competitions = json.loads(open(os.path.join(os.path.dirname(__file__), '../../competitions.json')).read())['competitions']
    yield

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# ─── ROUTES DE BASE ───────────────────────────────────────────────────────────

def test_page_accueil_accessible(client):
    """La page d'accueil répond avec un code 200"""
    response = client.get('/')
    assert response.status_code == 200

def test_page_accueil_contient_formulaire(client):
    """La page d'accueil contient le formulaire de connexion"""
    response = client.get('/')
    assert b'email' in response.data

def test_logout_redirige(client):
    """Le logout redirige vers l'accueil (code 302)"""
    response = client.get('/logout')
    assert response.status_code == 302

def test_page_points_accessible(client):
    """La page des points est accessible sans connexion"""
    response = client.get('/points')
    assert response.status_code == 200

def test_page_points_affiche_tous_les_clubs(client):
    """La page des points affiche bien tous les clubs"""
    response = client.get('/points')
    assert b'Simply Lift' in response.data
    assert b'Iron Temple' in response.data
    assert b'She Lifts' in response.data


# ─── BUG 1 : Email invalide ───────────────────────────────────────────────────

def test_login_email_valide(client):
    """Un email valide affiche la page de bienvenue"""
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b'Welcome' in response.data

def test_login_email_invalide_affiche_erreur(client):
    """Un email inconnu affiche un message d'erreur sur la page d'accueil"""
    response = client.post('/showSummary', data={'email': 'faux@email.com'})
    assert response.status_code == 200
    assert "existe pas" in response.data.decode('utf-8')

def test_login_email_invalide_reste_sur_index(client):
    """Un email inconnu reste sur la page index"""
    response = client.post('/showSummary', data={'email': 'faux@email.com'})
    assert b'Registration' in response.data


# ─── BUG 2 : Places disponibles ───────────────────────────────────────────────

def test_reservation_plus_que_places_disponibles(client):
    # On utilise un club fictif avec beaucoup de points
    # En réalité le bug 4 bloque avant. On teste directement la logique.
    # Pour déclencher bug 2 : il faut places <= 12 mais > numberOfPlaces
    # Donc on change numberOfPlaces à 1 dans le test
    import server
    server.competitions[0]['numberOfPlaces'] = '1'
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '5'
    })
    assert 'pas assez de places' in response.data.decode('utf-8')

def test_reservation_places_exactement_disponibles(client):
    """On peut réserver exactement le nombre de places disponibles (si <= 12)"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Fall Classic',
        'club': 'Iron Temple',
        'places': '2'
    })
    assert 'Réservation effectuée' in response.data.decode('utf-8')


# ─── BUG 3 : Points insuffisants ──────────────────────────────────────────────

def test_reservation_sans_assez_de_points(client):
    import server
    server.clubs[2]['points'] = '1'  # She Lifts n'a plus qu'1 point
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'She Lifts',
        'places': '5'
    })
    assert 'points' in response.data.decode('utf-8')

def test_reservation_avec_assez_de_points(client):
    """Réserver avec assez de points fonctionne"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '2'
    })
    assert 'Réservation effectuée' in response.data.decode('utf-8')


# ─── BUG 4 : Maximum 12 places ────────────────────────────────────────────────

def test_reservation_plus_de_12_places(client):
    """Réserver plus de 12 places affiche une erreur"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '13'
    })
    assert '12' in response.data.decode('utf-8')

def test_reservation_exactement_12_places(client):
    """Réserver exactement 12 places est autorisé"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '12'
    })
    assert 'Réservation effectuée' in response.data.decode('utf-8')

def test_reservation_0_place(client):
    """Réserver 0 place ne devrait pas déduire de points"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '0'
    })
    assert response.status_code == 200


# ─── PAGE BOOKING ─────────────────────────────────────────────────────────────

def test_book_club_et_competition_valides(client):
    """Accès à la page booking avec des données valides"""
    response = client.get('/book/Spring%20Festival/Simply%20Lift')
    assert response.status_code == 200

def test_book_club_inexistant(client):
    """Accès à la page booking avec un club inexistant redirige"""
    response = client.get('/book/Spring%20Festival/ClubInexistant')
    assert response.status_code == 302

def test_book_competition_inexistante(client):
    """Accès à la page booking avec une compétition inexistante redirige"""
    response = client.get('/book/CompetitionInexistante/Simply%20Lift')
    assert response.status_code == 302

def test_purchase_club_inexistant(client):
    """Achat avec club inexistant redirige vers l'accueil"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'ClubInexistant',
        'places': '1'
    })
    assert response.status_code == 302
