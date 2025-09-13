#!/bin/bash

kubectl delete -f k8s/cronjob.yaml --ignore-not-found
kubectl delete -f k8s/pvc.yaml --ignore-not-found
kubectl delete -f k8s/configmap.yaml --ignore-not-found
kubectl delete -f k8s/secrets.yaml --ignore-not-found
kubectl delete -f k8s/postgres-deployment.yaml --ignore-not-found
kubectl delete -f k8s/postgres-init-configmap.yaml --ignore-not-found
kubectl delete -f k8s/namespace.yaml --ignore-not-found

kubectl delete jobs -n data-export --all --ignore-not-found
