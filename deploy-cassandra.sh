#!/bin/bash

kubectl apply -f configs/cassandra-service.yml

kubectl apply -f configs/cassandra-statefulset.yml