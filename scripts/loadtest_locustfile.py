from locust import HttpUser, task, between

class MalwareApiUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def health(self):
        self.client.get("/api/v1/health")

    @task
    def predict(self):
        # Example payload, adjust as needed
        payload = {
            "network_flows": [{"src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "src_port": 1234, "dst_port": 80, "protocol": "TCP"}],
            "app_name": "test_app"
        }
        self.client.post("/api/v1/analysis", json=payload)
