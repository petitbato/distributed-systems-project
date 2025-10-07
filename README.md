# Distributed Systems Project – Milestone 1 (8 October 2025)

## Objective

This project is part of the *Distributed Systems* course.  
The objective of this first milestone is to deploy a simple web application in a Kubernetes cluster, replicated, and accessible through an **Ingress Controller**.
No database or persistent storage is required at this stage.

## 1. Application Overview

The application is a minimal Flask web server exposing a single route:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Kubernetes"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

It simply returns a text message to confirm that the container and cluster setup are functioning correctly.

## 2. Technologies Used

| Component | Tool |
|------------|------|
| Language | Python 3.11 |
| Web Framework | Flask |
| Containerization | Docker |
| Cluster | Minikube (Kubernetes) |
| Service Exposure | Ingress Controller or Nginx reverse proxy |
| OS Environment | Windows with WSL2 (Ubuntu) |

## 3. Repository Structure

```
distributed-systems-project/
│
├── app.py
├── requirements.txt
├── Dockerfile
│
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml     (optional)
│
└── README.md
```

## 4. Deployment Steps

### 4.1 Local build

```bash
docker build -t scalable-app:latest .
docker run -p 5000:5000 scalable-app
```

Accessible at:  
http://localhost:5000

### 4.2 Start Minikube

```bash
minikube start --driver=docker
```

### 4.3 Deploy on Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check that the pods and services are running:

```bash
kubectl get pods
kubectl get svc
```

### 4.4 Access the application

#### Using an Ingress Controller

1. Enable the Minikube ingress addon:
   ```bash
   minikube addons enable ingress
   ```
2. Apply the Ingress configuration:
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```
3. Add the following line to your Windows hosts file:
   ```
   127.0.0.1 scalable.local
   ```
4. Run:
   ```bash
   minikube tunnel
   ```
5. Access the app at:
   ```
   http://scalable.local
   ```

## 5. Verification Checklist

| Requirement | Status |
|--------------|--------|
| Application containerized | ✅ |
| Kubernetes deployment created | ✅ |
| Replication enabled (2 pods) | ✅ |
| Service exposed via NodePort or Ingress | ✅ |
| Accessible from a browser | ✅ |
| Code hosted on GitHub | ✅ |

## 6. Next Steps

The next milestone will introduce:
- a database (PostgreSQL),
- a CI/CD pipeline (build, scan, deploy),
- security and monitoring components (Trivy, Grafana, etc.).

This README documents the base working setup required for the first milestone (8 October 2025).
