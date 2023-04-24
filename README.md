# Abandoned_S3_Bucket_Takeover
[![Pylint](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/pylint.yml/badge.svg)](https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover/actions/workflows/pylint.yml)
Solution to hunt for possible subdomain takeover via abandoned Amazon S3 Bucket.

This uses asynchronous requests (aiohttp) to a given list of (sub)domains to search for a pattern matching an abandoned Amazon S3 Bucket (404 page containing the keyword `NoSuchBucket`). 

![output-onlinegiftools](https://user-images.githubusercontent.com/13363451/233985879-ee726263-139e-4258-8d10-b3c22df05d80.gif)

## Prerequisites
To install the prerequisite modules, use the requirements.txt file as follow:
```sh
pip install -r requirements.txt
```
To obtain the script, download this repo's content from GitHub:
```sh
git clone https://github.com/ob1lan/Abandoned_S3_Bucket_Takeover.git
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
### Using the Hunt-Abandoned-Bucket script
This is how you would use the script, given you installed all prerequisites modules and got a `domains.txt` file in the same directory as the script:
```sh
python Hunt-Abandoned-Bucket.py
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
## To Do
- Improve the script and have it peer-reviewed
- Take args to display help and set the location of the domains.txt, along with the Semaphore value
- Verify the retry decoration actually work (doubts)
- Containerize along with amass
