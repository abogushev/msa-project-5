#!/bin/bash

set -e
JOB_NAME="test-run-$(date +%Y%m%d-%H%M%S)"
kubectl create job --from=cronjob/data-exporter $JOB_NAME -n data-export

kubectl wait --for=condition=complete job/$JOB_NAME -n data-export --timeout=120s

POD_NAME=$(kubectl get pods -n data-export -l job-name=$JOB_NAME -o jsonpath='{.items[0].metadata.name}')

kubectl logs -n data-export $POD_NAME

kubectl exec -n data-export $POD_NAME -- ls -la /data/exports/

kubectl exec -n data-export $POD_NAME -- cat /data/exports/$(kubectl exec -n data-export $POD_NAME -- ls /data/exports/ | grep csv | head -1) | head -5
