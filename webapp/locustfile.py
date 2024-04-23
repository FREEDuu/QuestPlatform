from locust import HttpUser, task, between
from bs4 import BeautifulSoup

class MyUser(HttpUser):
    wait_time = between(1, 2)
    csrf_token = None

    def on_start(self):
        # login before any task is executed
        self.login()

    def login(self):
        response = self.client.get("/login/")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
            if csrf_input:
                self.csrf_token = csrf_input['value']
            else:
                print("CSRF token not found in login page")
                self.environment.runner.quit()
        else:
            print(f"Failed to get login page: {response.status_code}")
            self.environment.runner.quit()

        # Set CSRF token as a cookie
        self.client.cookies.set('csrftoken', self.csrf_token)

        response = self.client.post("/login/", {
            "username": "carl",
            "password": "pondsama",
        }, headers={
            'X-CSRFToken': self.csrf_token
        })

        # check if login was successful
        if response.status_code != 200:
            print("Login failed!")
            self.environment.runner.quit()
            

    @task
    def test_home(self):
        response = self.client.get("/", headers={ 'X-CSRFToken': self.csrf_token })
        response.raise_for_status()

    @task(weight=2)
    def test_controllo(self):
        data = {"page": "1"}
        response = self.client.post("/controllo", data=data, headers={ 'X-CSRFToken': self.csrf_token })
        response.raise_for_status()

    @task(weight=3)
    def test_statistiche(self):
        response = self.client.get("/statistiche", headers={ 'X-CSRFToken': self.csrf_token })
        response.raise_for_status()