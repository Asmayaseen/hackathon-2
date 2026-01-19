# Phase 4: Local Kubernetes Deployment

This phase moves the Todo Chatbot application to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with WSL 2 backend on Windows)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Helm](https://helm.sh/docs/intro/install/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Directory Structure

- `backend/`: FastAPI backend (containerized)
- `frontend/`: Next.js frontend (containerized)
- `helm/`: Helm chart for deployment

## Setup & Deployment

### 1. Start Minikube

```bash
minikube start
```

### 2. Build Docker Images

Point your shell to Minikube's Docker daemon so it can see the images we build:

```bash
eval $(minikube docker-env)
```

Build the images:

```bash
./build_images.sh
# Or manually:
# docker build -t todo-backend:latest ./backend
# docker build -t todo-frontend:latest ./frontend
```

### 3. Deploy with Helm

Create a local values file with your secrets (DO NOT COMMIT THIS FILE):

```bash
# values-local.yaml
secrets:
  DATABASE_URL: "postgresql://user:pass@host:5432/db"
  BETTER_AUTH_SECRET: "your-secret-here"
  OPENAI_API_KEY: "sk-..."
```

Install the chart:

```bash
helm install todo-app ./helm -f values-local.yaml
```

### 4. Access the Application

Get the URL for the frontend service:

```bash
minikube service todo-app-frontend --url
```

Or perform port forwarding:

```bash
kubectl port-forward service/todo-app-frontend 3000:3000
```

Then visit `http://localhost:3000`.

## AI Integration

This phase leveraged AI tools for DevOps:
- **Claude Code**: Generated Dockerfiles and Helm charts from specifications.
- **Gordon (Docker AI)**: Used to optimize Dockerfiles (simulated).
- **kubectl-ai**: Used for generating kubectl commands for debugging.

## Troubleshooting

- **ImagePullBackOff**: Ensure you ran `eval $(minikube docker-env)` before building images.
- **CrashLoopBackOff**: Check logs with `kubectl logs <pod-name>`. Check DB connection strings.

## Submission Checklist

- [ ] Add Demo Video link (max 90s) to `hackathon.md` or submission form.
- [ ] Add WhatsApp number for presentation invitation.
- [ ] Push code to GitHub.
- [ ] Submit via Google Form.

