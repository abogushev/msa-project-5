#!/bin/bash
set -e

docker build -t data-exporter:latest .

minikube image load data-exporter:latest

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres-init-configmap.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n data-export --timeout=120s
kubectl exec -n data-export deployment/postgres -- psql -U postgres -d transport_db -c "SELECT COUNT(*) FROM shipments;"
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/cronjob.yaml
kubectl get all -n data-export

