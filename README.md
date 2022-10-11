<p align="center">
  <img src="https://user-images.githubusercontent.com/80271709/195068761-ceba3b0f-fa3a-43b1-aa63-3a775fbe1ed6.png" width="700" height="250" />
</p>

# Deloton Exercise Bikes

## Overview

This repository contains data pipelines and applications for the Deloton Exercise Bikes company. The applications we have built allow Deloton to clean their raw unstructured data so that is useful for analysis.
The online applications and pipelines are hosted with AWS services and Docker containers.

Raw unstructured data is fed from a Kafka cluster on GCP, which is cleaned and loaded through our pipelines.

## Deliverables

The applications we have produced are:

- Heart Rate Alerts
- Live Dashboard
- Daily Executive Reports
- Public API
- Tableau Integrations

## Heart Rate Alerts

Users currently on the bike will have their heart rates checked in real time for abnormalities. If their heart rate is detected to be too low or high, then they will receive an email detailing appropriate action. This is done by running the script on EC2 to ingest Kafka data and using SES to the send the email to the user.

## Live Dashboard

A live dashboard is available for business stakeholders, containing information on the current ride as well as recent rides with the last 12 hours.

The current ride section shows information about the user as well as their performance on the bike, such as their heart rate, resistance and power output.

The recent rides section contains visualisations of the data, such as the gender and age range as well as the total and average power output of users.

The dashboard is deployed on EC2 and is available online at:

## Daily Executive Reports

Through an automated report generator, the CEO of Deloton Exercise Bikes will receive a daily report email. This contains visualisations of data from users for the entire day, including the gender, age ranges and total and average power output.

The report generator is deployed on an AWS Lambda function, which is scheduled to run everyday to deliver an email and PDF with insights generated from the day.

## Public API

An API is available for Deloton Staff members to inspect the data stored for all users and rides. The API is designed around REST principles and queries up-to-date information of all data. Users can retrieve all rides, specific rides and users by their respective ids, all rides on a certain id, or send a delete request for any ride or user.

The API is hosted using EC2 and is available online at: http://18.170.223.8:5001

## Tableau Integrations

Tableau is a data visualisation tool that gives data analysts more options in handling data. We have connected our Aurora PostgreSQL instance to Tableau, which gives access to all of the data within the database for analysis. We have generated our own insights and shared them via Tableau Server, which can be securely accessed by other analysts.

The Tableau visualisations can be accessed via

https://prod-uk-a.online.tableau.com/#/site/zookeeperstableau/workbooks/221509?:origin=card_share_link

(Tableau Cloud account required)
