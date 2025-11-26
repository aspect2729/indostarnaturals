# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying IndoStar Naturals to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (EKS, GKE, AKS, or self-managed)
- kubectl configured to access your cluster
- Docker images built and pushed to a container registry
- PostgreSQL database (RDS or managed service)
- Redis cluster (ElastiCache or managed service)
- S3 bucket with CloudFront CDN
- Domain names configured in Route 53 or your DNS provider

## Deployment Steps

### 1. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 3. Create Secrets

**Option A: From environment file**
```bash
kubectl create secret generic indostar-secrets \
  --from-env-file=../backend/.env.prod \
  -n indostar-naturals
```

**Option B: From YAML (not recommended for production)**
```bash
# Copy secrets.yaml.example to secrets.yaml and fill in values
cp secrets.yaml.example secrets.yaml
# Edit secrets.yaml with actual values
kubectl apply -f secrets.yaml
```

### 4. Deploy Backend

```bash
kubectl apply -f backend-deployment.yaml
```

### 5. Deploy Celery Workers

```bash
kubectl apply -f celery-worker-deployment.yaml
```

### 6. Deploy Frontend

```bash
kubectl apply -f frontend-deployment.yaml
```

### 7. Configure Ingress

First, install cert-manager for automatic SSL certificates:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

Then apply the ingress configuration:

```bash
kubectl apply -f ingress.yaml
```

## Verify Deployment

Check pod status:
```bash
kubectl get pods -n indostar-naturals
```

Check services:
```bash
kubectl get services -n indostar-naturals
```

Check ingress:
```bash
kubectl get ingress -n indostar-naturals
```

View logs:
```bash
# Backend logs
kubectl logs -f deployment/backend -n indostar-naturals

# Celery worker logs
kubectl logs -f deployment/celery-worker -n indostar-naturals

# Frontend logs
kubectl logs -f deployment/frontend -n indostar-naturals
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n indostar-naturals

# Scale celery workers
kubectl scale deployment celery-worker --replicas=4 -n indostar-naturals
```

### Auto-scaling

The backend deployment includes a HorizontalPodAutoscaler that automatically scales based on CPU and memory usage.

View HPA status:
```bash
kubectl get hpa -n indostar-naturals
```

## Database Migrations

Run migrations as a Kubernetes Job:

```bash
kubectl run migration --image=indostar-naturals/backend:latest \
  --restart=Never \
  --env-from=configmap/indostar-config \
  --env-from=secret/indostar-secrets \
  --command -- alembic upgrade head \
  -n indostar-naturals
```

## Rollback

```bash
# View deployment history
kubectl rollout history deployment/backend -n indostar-naturals

# Rollback to previous version
kubectl rollout undo deployment/backend -n indostar-naturals

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n indostar-naturals
```

## Cleanup

```bash
kubectl delete namespace indostar-naturals
```

## Monitoring

Set up monitoring with Prometheus and Grafana:

```bash
# Install Prometheus Operator
kubectl apply -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Create ServiceMonitor for backend
kubectl apply -f monitoring/service-monitor.yaml
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name> -n indostar-naturals
kubectl logs <pod-name> -n indostar-naturals
```

### Database connection issues

Verify secrets are correctly set:
```bash
kubectl get secret indostar-secrets -n indostar-naturals -o yaml
```

### Ingress not working

Check ingress controller logs:
```bash
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

Verify DNS records point to the load balancer:
```bash
kubectl get ingress indostar-ingress -n indostar-naturals
```
