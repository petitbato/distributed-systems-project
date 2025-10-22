# Distributed Systems Project

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

-----

##  7. Local Development Environment (Hot-Reloading)

This document outlines the setup for a high-speed local development environment. The goal is to achieve **hot-reloading**, where changes made to the local Python source code are reflected instantly in the application running inside Kubernetes, bypassing the standard `git push` $\rightarrow$ CI/CD $\rightarrow$ Docker build $\rightarrow$ `kubectl apply` cycle.

-----

### 7.1 What: The Goal

The primary objective is to create a development feedback loop that is measured in seconds, not minutes. This setup allows you-the developer-to run the application within a realistic Kubernetes (Minikube) environment while still using your local code editor, with changes automatically reloaded by the server inside the pod.

This environment is **completely isolated** from the `test` and `prod` environments. It uses a dedicated deployment and direct port-forwarding, ensuring your development work does not interfere with other environments sharing the same cluster.

-----

### 7.2 Why: The Mechanism

This workflow functions by creating a "bridge" between your local filesystem and the container running inside the `minikube` pod. It relies on three core components:

1.  **`minikube mount`**: This command establishes a persistent connection between a directory on your host machine (your PC) and a directory inside the Minikube virtual machine's filesystem (the "node"). This makes your source code "visible" to the Kubernetes node.

2.  **`deployment-dev.yaml`**: This is a *dedicated* Kubernetes `Deployment` manifest. It differs from a standard `deployment.yaml` in crucial ways:

      * **`hostPath` Volume:** It instructs Kubernetes to mount the directory *from the Minikube VM* (e.g., `/data/my-project`), which `minikube mount` is synced to, directly into the container's filesystem at `/app`. This **shadows** (hides) the original code that was baked into the Docker image, replacing it with your live local code.
      * **Flask Debug Mode:** It overrides the container's `env` and `command` to force Flask into debug mode (`FLASK_DEBUG=1`). In this mode, Flask continuously monitors the filesystem for changes. When it detects a change in the mounted `/app` directory (your local file), it automatically restarts the server.
      * **Unique Label (`app: scalable-app-dev`):** This label ensures that the standard `Service` (like the `LoadBalancer` for `test` or `prod`) ignores this pod. This prevents test/prod traffic from being routed to your development instance.

3.  **`kubectl port-forward`**: This command creates a direct, private network tunnel from your local machine's `localhost:8080` to the specific `scalable-app-dev` pod's port `5000`. This bypasses all Kubernetes service discovery and networking (like `Service` or `Ingress`), giving you direct access to the debug pod.

-----

### 7.3 How: Step-by-Step Workflow

Follow these steps to run the hot-reloading development environment.

#### 1\. Key Components (The "What to Make")

Ensure you have a dedicated "dev" deployment manifest. Create this file at `k8s/dev/deployment-dev.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scalable-app-dev
  namespace: test # Deployed to the 'test' namespace
  labels:
    app: scalable-app-dev # <-- 1. Unique label
spec:
  replicas: 1
  selector:
    matchLabels:
      app: scalable-app-dev
  template:
    metadata:
      labels:
        app: scalable-app-dev # <-- 1. Must match selector
    spec:
      containers:
      - name: scalable-app
        # Use any existing build; it will be shadowed
        image: najsv98/scalable-app:build-12 
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_DEBUG # <-- 2. Enable hot-reload
          value: "1"
        command: ["flask", "run", "--host=0.0.0.0", "--port=5000"] # <-- 2. Run debug server
        volumeMounts:
        - name: dev-code
          mountPath: /app # <-- 3. Path to code *inside* the container
      volumes:
      - name: dev-code
        hostPath:
          path: /data/my-project # <-- 3. Path *inside* the Minikube VM
          type: Directory
```

#### 2\. Start the File Sync (Terminal 1)

Open your first terminal. Run `minikube mount` to connect your local project directory to the `hostPath` specified in the YAML file.

**Note:** The target path (`/data/my-project`) **must** match `volumes.hostPath.path` in your `deployment-dev.yaml`.

```bash
# Example for Windows. Adjust your source path accordingly.
# This command must be left running.
minikube mount .:/data/my-project
```

#### 3\. Run the Dev Pod & Port-Forward (Terminal 2)

Open a second terminal to manage the Kubernetes resources.

1.  **Apply the `dev` deployment:**

    ```bash
    kubectl apply -f k8s/dev/deployment-dev.yaml
    ```

2.  **Start the port-forward:**
    This command connects your local `8080` to the pod's `5000`.

    ```bash
    # This command must also be left running.
    kubectl port-forward deployment/scalable-app-dev 8080:5000 -n test
    ```

#### 4\. Develop

You are now set up:

  * Access your application at **`http://localhost:8080`**.
  * Open your project (e.g., `C:\..._local\distributed-systems-project`) in your code editor.
  * Modify any `.py` file and save it.
  * The Flask server in the pod (streaming logs in Terminal 2, if `port-forward` is verbose) will detect the change and restart.
  * Refresh your browser. Your code changes will be live.