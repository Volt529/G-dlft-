from locust import HttpUser, task, between


class GudlftUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Simule la connexion d'un secrétaire"""
        self.client.post("/showSummary", data={
            "email": "john@simplylift.co"
        })

    @task(1)
    def view_index(self):
        """Page d'accueil"""
        self.client.get("/")

    @task(2)
    def view_competitions(self):
        """Page principale après connexion - doit charger en moins de 5s"""
        with self.client.post("/showSummary", data={"email": "john@simplylift.co"}, catch_response=True) as response:
            if response.elapsed.total_seconds() > 5:
                response.failure("Trop lent : plus de 5 secondes")

    @task(1)
    def view_points(self):
        """Page publique des points des clubs"""
        self.client.get("/points")

    @task(3)
    def book_and_purchase(self):
        """Simule une réservation - mise à jour doit prendre moins de 2s"""
        self.client.get("/book/Spring%20Festival/Simply%20Lift")

        with self.client.post("/purchasePlaces", data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "1"
        }, catch_response=True) as response:
            if response.elapsed.total_seconds() > 2:
                response.failure("Mise à jour trop lente : plus de 2 secondes")

    @task(1)
    def logout(self):
        """Déconnexion"""
        self.client.get("/logout")
