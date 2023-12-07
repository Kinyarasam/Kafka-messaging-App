#!/usr/bin/env bash

bin/kafka-topics.sh --create --topic  messaging app --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

