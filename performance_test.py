from locust import FastHttpUser, task


class HelloWorldUser(FastHttpUser):
    @task
    def courses(self) -> None:
        self.client.get("/api/v1/courses/")
