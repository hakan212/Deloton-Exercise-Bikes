# Deloton Exercise Bikes

## Overview

This repository contains data pipelines and applications for the Deloton Exercise Bikes company. The applications we have built allow Deloton to collect information about their users and rides.
The online applications and pipelines are hosted with AWS services.

Raw unstructured data is fed from a Kafka cluster on GCP, which is cleaned and loaded through our pipelines.

## Deliverables

The applications we have produced are:

- Heart Rate Alerts
- Live Dashboard
- Daily Executive Reports
- Public API
- Tableau Integrations

## Heart Rate Alerts

Deloton's bikes report heart rates of the user every 0.5 seconds. We have created a script that will send an email alert to a user if their heart rate is detected be abnormal based on their age. This is done by running the script on EC2 to ingest Kafka data and sending an email to the user via SES.

## Live Dashboard

## Daily Executive Reports

## Public API

## Tableau Integrations

Tableau is a data visualisation tool that gives data analysts more options in handling data. We have connected our Aurora PostgreSQL instance to Tableau, which gives access to all of the data within the database for analysis. We have shared the Tableau via Tableau Server, allowing analysts to share their findings in a secure way.
