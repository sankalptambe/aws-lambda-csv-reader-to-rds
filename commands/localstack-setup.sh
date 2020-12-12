#!/bin/bash
echo "Preparing the localstack environment..."

# Create a localstack s3 bucket and add a file.
# This needs to be done as localstack is inMemory and data is lost when docker is stopped.

# 01: start localstack
docker-compose -f docker-compose-localstack.yml up

# 02: create a s3 bucket
aws --endpoint-url=http://localhost:4566 s3 mb s3://csv-reader-localstack
# output -> make_bucket: csv-reader-localstack

# 03: copy a csv file to the bucket.
aws --endpoint-url=http://localhost:4566 s3 cp ../cities.csv s3://csv-reader-localstack/
# output -> upload: ./cities.csv to s3://csv-reader-localstack/cities.csv


######### SQL Queries ##############
# Create table cities (ID int NOT NULL IDENTITY PRIMARY KEY,LatD varchar(255),LatM  varchar(255),LatS varchar(255), NS varchar(255), LonD varchar(255),LonM varchar(255), LonS varchar(255), EW varchar(255), City varchar(255), State varchar(255));
