import time
from locust import HttpUser, task, between

class LoadUser(HttpUser):
    wait_time = between(0, 1)

    @task
    def index(self):
        print(self.client.get("/").text)