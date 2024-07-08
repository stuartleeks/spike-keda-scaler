# Sample for KEDA scaling based on HTTP response codes

> **NOTE**: This is a work in progress and may not be fully functional!

This sample demonstrates how to use KEDA to scale a Kubernetes deployment based on HTTP response codes. In this example, we create a simple HTTP server that sends a 200 OK response every 10 seconds and a 429 Too Many Requests response under certain conditions. We then use Prometheus to scrape metrics from the application and KEDA to scale the deployment based on the HTTP response codes.

## tl;dr

To use the Makefile for simplified operations, run:

```bash
make
```

This will:

- Install KEDA in your Kubernetes cluster
- Build the Docker image locally with the tags defined in the Makefile
- Deploy the sample application to your Kubernetes cluster
- Install Prometheus in your Kubernetes cluster
- Configure Prometheus to scrape metrics from your application
- Create a KEDA ScaledObject to scale the deployment based on the HTTP response codes


## 1. Prerequisites

- Kubernetes Cluster: Make sure you have a running Kubernetes cluster
- kubectl: Ensure you have kubectl configured to interact with your cluster
- Helm: Install Helm for deploying KEDA

## 2. Install KEDA

- First, install KEDA in your Kubernetes cluster using Helm:

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install keda kedacore/keda
```

## 3. Create a Sample Application

Create a simple HTTP server that sends a 200 OK response every 10 seconds and a 429 Too Many Requests response under certain conditions.

### Dockerfile

Create a Dockerfile for your application:

```Dockerfile
# Use a lightweight base image
FROM python:3.8-slim

# Install Flask
RUN pip install Flask

# Copy the application code
COPY app.py /app.py

# Set the working directory
WORKDIR /

# Expose the port the application will run on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
```

### app.py

Create a simple Flask application that sends a 200 OK response every 10 seconds and a 429 Too Many Requests response under certain conditions:

```python
from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route('/')
def index():
    # If the current hour is even, return a 200 OK response
    if time.localtime().tm_hour % 2 == 0:
        return jsonify({"message": "OK"}), 200
    else:
        return jsonify({"message": "Too Many Requests"}), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

>IMPORTANT: Change the logic here to define your test behavior. In this example, the application returns a 200 OK response every even hour and a 429 Too Many Requests response every odd hour.

## 4. Build and Push the Docker Image

Build the Docker image and optionally push it to a container registry:

```bash
# Build the Docker image
docker build -t <your-docker-username>/http-scaler:latest .

# Push the Docker image
docker push <your-docker-username>/http-scaler:latest
```

## 5. Deploy the Sample Application

Create a Kubernetes deployment and service for your application.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: http-scaler
spec:
  replicas: 1
  selector:
    matchLabels:
      app: http-scaler
  template:
    metadata:
      labels:
        app: http-scaler
    spec:
      containers:
      - name: http-scaler
        image: <your-docker-username>/http-scaler:latest
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: http-scaler
spec:
  selector:
    app: http-scaler
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```

Apply the deployment and service:

```bash
kubectl apply -f deployment.yaml
```

<!-- TODO: Check if Prometheus section is valid -->

## 6. Configure Prometheus 

Install Prometheus in your Kubernetes cluster to scrape metrics from your application.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/prometheus
```

Get the current ConfigMap for Prometheus:

```bash
kubectl apply -f prometheus/prometheus.yaml 
```

You can now access the Prometheus dashboard to view the metrics scraped from your application.

```bash
kubectl port-forward svc/prometheus-server 9090:80
```

Open your browser and navigate to `http://localhost:9090` to access the Prometheus dashboard.

### 1. Check Targets

Open the Prometheus dashboard and navigate to Status -> Targets. Ensure that your application (http-scaler) is listed and being scraped.

### 2. Query Metrics

In the Prometheus dashboard, you can query the metrics exposed by your application. For example, you can run:

```promql
rate(http_requests_total[1m])
```

## 7. Create a KEDA ScaledObject

Create a KEDA ScaledObject to scale the deployment based on the HTTP response codes.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: http-scaler
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: http-scaler
  pollingInterval: 5  # Check every 5 seconds
  cooldownPeriod:  30 # Period to wait before scaling down
  minReplicaCount: 1
  maxReplicaCount: 10
  triggers:
  - type: prometheus
    metadata:
      serverAddress: http://prometheus-server.default.svc.cluster.local:9090
      metricName: http_requests_total
      threshold: "1"  # Set a threshold based on your metric and scale-down condition
      query: |
        sum(rate(http_requests_total{group="http-scaler", status_code="429"}[2m])) 
    authenticationRef:
      name: prometheus-auth
```

Apply the scaled object:

```bash
kubectl apply -f scaledobject.yaml
```

## 8. Verify the Setup

Ensure your application is running correctly and accessible.

- Verify that Prometheus is scraping metrics from your application.
- Check the KEDA logs to ensure it is scaling the application as expected.

With this setup, KEDA will check the HTTP response codes every 5 seconds and scale the application to zero replicas if it detects a 429 Too Many Requests response.
