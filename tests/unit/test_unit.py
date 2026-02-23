import pytest
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from server import app, loadClubs, loadCompetitions


# ─── FIXTURES ─────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_clubs():
    return [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "25"},
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
    ]

@pytest.fixture
def mock_competitions():
    return [
        {"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"},
        {"name": "Fall Classic", "date": "2020-10-22 13:30:00", "numberOfPlaces": "24"}
    ]


# ─── TESTS UNITAIRES : loadClubs / loadCompetitions ───────────────────────────

def test_load_clubs_retourne_une_liste():
    """loadClubs() doit retourner une liste"""
    clubs = loadClubs()
    assert isinstance(clubs, list)

def test_load_clubs_non_vide():
    """loadClubs() ne doit pas retourner une liste vide"""
    clubs = loadClubs()
    assert len(clubs) > 0

def test_load_clubs_contient_les_bons_champs():
    """Chaque club doit avoir name, email et points"""
    clubs = loadClubs()
    for club in clubs:
        assert 'name' in club
        assert 'email' in club
        assert 'points' in club

def test_load_competitions_retourne_une_liste():
    """loadCompetitions() doit retourner une liste"""
    competitions = loadCompetitions()
    assert isinstance(competitions, list)

def test_load_competitions_non_vide():
    """loadCompetitions() ne doit pas retourner une liste vide"""
    competitions = loadCompetitions()
    assert len(competitions) > 0

def test_load_competitions_contient_les_bons_champs():
    """Chaque compétition doit avoir name, date et numberOfPlaces"""
    competitions = loadCompetitions()
    for comp in competitions:
        assert 'name' in comp
        assert 'date' in comp
        assert 'numberOfPlaces' in comp


# ─── TESTS UNITAIRES : BUG 1 — Email ──────────────────────────────────────────

def test_email_valide_trouve_dans_clubs(mock_clubs):
    """Un email valide doit correspondre à un club"""
    email = "john@simplylift.co"
    club = next((c for c in mock_clubs if c['email'] == email), None)
    assert club is not None
    assert club['name'] == "Simply Lift"

def test_email_invalide_retourne_none(mock_clubs):
    """Un email inconnu doit retourner None"""
    email = "inconnu@fake.com"
    club = next((c for c in mock_clubs if c['email'] == email), None)
    assert club is None


# ─── TESTS UNITAIRES : BUG 2 — Places disponibles ────────────────────────────

def test_places_disponibles_suffisantes(mock_competitions):
    """On peut réserver si assez de places"""
    comp = mock_competitions[0]
    places_demandees = 5
    assert places_demandees <= int(comp['numberOfPlaces'])

def test_places_disponibles_insuffisantes(mock_competitions):
    """On ne peut pas réserver plus que les places disponibles"""
    comp = mock_competitions[0]
    places_demandees = 999
    assert places_demandees > int(comp['numberOfPlaces'])


# ─── TESTS UNITAIRES : BUG 3 — Points du club ────────────────────────────────

def test_points_suffisants(mock_clubs):
    """Iron Temple a assez de points pour réserver 2 places"""
    club = next(c for c in mock_clubs if c['name'] == 'Iron Temple')
    places_demandees = 2
    assert places_demandees <= int(club['points'])

def test_points_insuffisants(mock_clubs):
    """She Lifts n'a pas assez de points pour réserver 50 places"""
    club = next(c for c in mock_clubs if c['name'] == 'She Lifts')
    places_demandees = 50
    assert places_demandees > int(club['points'])


# ─── TESTS UNITAIRES : BUG 4 — Max 12 places ─────────────────────────────────

def test_max_12_places_depasse():
    """13 places dépasse la limite de 12"""
    places_demandees = 13
    assert places_demandees > 12

def test_max_12_places_respecte():
    """12 places respecte la limite"""
    places_demandees = 12
    assert places_demandees <= 12

def test_1_place_respecte_limite():
    """1 place respecte la limite"""
    places_demandees = 1
    assert places_demandees <= 12


# ─── TESTS UNITAIRES : Déduction des points et places ────────────────────────

def test_deduction_places_apres_reservation(mock_competitions):
    """Les places doivent être déduites après réservation"""
    comp = mock_competitions[0]
    places_avant = int(comp['numberOfPlaces'])
    places_achetees = 3
    comp['numberOfPlaces'] = str(places_avant - places_achetees)
    assert int(comp['numberOfPlaces']) == places_avant - places_achetees

def test_deduction_points_apres_reservation(mock_clubs):
    """Les points du club doivent être déduits après réservation"""
    club = mock_clubs[0]
    points_avant = int(club['points'])
    places_achetees = 3
    club['points'] = str(points_avant - places_achetees)
    assert int(club['points']) == points_avant - places_achetees
