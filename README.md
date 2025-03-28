# Abandoned_S3_Bucket_Takeover
[![Pylint](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/pylint.yml/badge.svg)](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/pylint.yml)  [![CodeQL](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/codeql.yml/badge.svg)](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/codeql.yml)  [![Bandit](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/bandit.yml/badge.svg)](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/bandit.yml)  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/ob1lan/Abandoned_S3_Bucket_Takeover/main/LICENSE)

![image](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/assets/13363451/4baa0f48-7e08-4a89-bd2a-70e7b10c0b48)

## Overview
Solution to hunt for possible subdomain takeover via abandoned Amazon S3 Bucket.

This uses asynchronous requests (aiohttp) to a given list of (sub)domains and search for a pattern matching an abandoned Amazon S3 Bucket (404 page containing the keyword `NoSuchBucket`). 

![output-onlinegiftools (1)](https://user-images.githubusercontent.com/13363451/234264263-36c03a56-b5f8-4f85-8418-04c799956d4f.gif)

## Prerequisites
To obtain the script, download this repo's content from GitHub:
```sh
git clone https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover.git
```
To install the prerequisite modules, use the requirements.txt file as follow:
```sh
pip install -r requirements.txt
```

## Usage
### The domains.txt file
In order to use the script, you need to have a `domains.txt` file, containing 1 domain per line, in the working directory. 
This file can be easily generated with any tool of your liking, such as amas. 

#### Example with amass
```sh
amass enum -active -src -brute -o amass-results.txt -d mydomain.com

# Once amass finished finding all subdomains for the input domain
cat amass-results.txt | awk -F ] '{print $2}' | sed -e 's/  */ /g' -e 's/^ *\(.*\) *$/\1/' > domains.txt
```
### Using the script
This is how you would use the script, given you installed all prerequisites modules and got a `domains.txt` file in the same directory as the script:
```sh
python hunt_abandoned_bucket.py
```
Once the script executed, the following files are created in the same directory:
- __findings.txt__ : lists all records matching the criteria (returns a 404 and the common 'NoSuchBucket' page)
- __errors.txt__ : lists all errors encountered by the script while querying the urls (timeout, TooManyRedirects, etc...)
- __excluded.txt__ : you can use this file to exclude (sub)domains in future runs
## Limiting concurrent requests
The requests are limited with a Semaphore to avoid possible issues, the default value is 50 concurrent requests maximum. This can be changed by modifying the value of the 'sem' variable in the script:
```python
sem = asyncio.Semaphore(50)
```
