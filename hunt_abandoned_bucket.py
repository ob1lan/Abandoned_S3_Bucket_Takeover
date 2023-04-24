#!/usr/bin/env python3
"""Search for possible subdomain takeover via abandoned Amazon S3 bucket.
Requires an existing domains.txt file in the working directory containing 1 domain per line.
This can be generated by amass, or any other tool of your liking.

Usage:
    ./hunt_abandoned_bucket.py

Author:
    Ob1lan - 22-APRIL-2023
"""

import os.path
import time
import sys
from tqdm import tqdm
import asyncio
import aiohttp
import dns.resolver
from aioretry import (
    retry,
    # Tuple[bool, Union[int, float]]
    RetryPolicyStrategy,
    RetryInfo
)


# Defines the retry policy used by aioretry
def retry_policy(info: RetryInfo) -> RetryPolicyStrategy:
    """
    - It will always retry until succeeded
    - If fails for the first time, it will retry immediately,
    - If it fails again,
      aioretry will perform a 100ms delay before the second retry,
      200ms delay before the 3rd retry,
      the 4th retry immediately,
      100ms delay before the 5th retry,
      etc...
    """
    return False, (info.fails - 1) % 3 * 0.1


# Check if the domains.txt file is present in the working directory, if not, exit
if not os.path.exists("domains.txt"):
    print("No domain.txt file detected.")
    sys.exit(1)

# Check if the errors.txt, excluded.txt and findings.txt files are present, if not, create them
if not os.path.exists("errors.txt"):
    open("errors.txt", 'w', encoding="utf-8").close()

if not os.path.exists("excluded.txt"):
    open("excluded.txt", 'w', encoding="utf-8").close()

if not os.path.exists("findings.txt"):
    open("findings.txt", 'w', encoding="utf-8").close()

# Count the number of lines in domains.txt. Variable 'count' will be used in progress bar
with open(r"domains.txt", 'r', encoding="utf-8") as file:
    COUNT = 0
    for line in file:
        if line != "\n":
            COUNT += 1
file.close()

# This Semaphore declaration limits the number of concurent requests, and prevents some errors
sem = asyncio.Semaphore(50)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

with open("excluded.txt", 'r', encoding="utf-8") as exclusions:
    excluded = exclusions.read()
exclusions.close()

errorfile = open("errors.txt", "a", encoding="utf-8")


@retry(retry_policy)
async def get(domain, session):
    """Function that formats domains into URL and queries them async to hunt for 404 responses.
    Once a 404 response code is found, the function search for the NoSuchBucket keyword to determine
    whether it could be an abandoned Amazon S3 Bucket or not.
    """
    if domain.strip() not in excluded:
        try:
            url = "http://" + domain.strip()
            async with sem:
                async with session.get(url=url, timeout=10) as response:
                    resp = await response.read()
                    if response.status == 404:
                        text = await response.text()
                        if "NoSuchBucket" in text:
                            print("Might be an Abandoned Amazon S3 Bucket: ", url)
                            answer: \
                                dns.resolver.Answer = dns.resolver.resolve(domain.strip(), 'CNAME')
                            for rdata in answer:
                                print(" -> ", rdata)
                            fidingsfile = open("findings.txt", "a", encoding="utf-8")
                            fidingsfile.write(url + "\n")
                            fidingsfile.close()
        except aiohttp.client_exceptions.ClientConnectorError:
            errorfile.write("ClientConnectorError: " + domain.strip() + "\n")
        except asyncio.exceptions.TimeoutError:
            errorfile.write("TimeoutError: " + domain.strip() + "\n")
        except aiohttp.client_exceptions.ClientOSError:
            errorfile.write("ClientOSError: " + domain.strip() + "\n")
        except aiohttp.client_exceptions.TooManyRedirects:
            errorfile.write("TooManyRedirects: " + domain.strip() + "\n")
        except aiohttp.client_exceptions.ServerDisconnectedError:
            errorfile.write("ServerDisconnectedError: " + domain.strip() + "\n")
        except Exception as expt:
            print(f'Unable to get url {domain.strip()} due to {expt.__class__}')
            errorfile.write("Error: " + domain.strip() + "\n")
            pass
    else:
        print("Excluded:", domain.strip())


async def main(domains):
    """The main function that calls the get and log progress in a tqdm progress bar."""
    async with aiohttp.ClientSession(headers=headers) as session:
        ret = [get(domain, session) for domain in domains]
        responses = [await f for f in tqdm(asyncio.as_completed(ret),
                                           total=len(ret),
                                           desc="Progress",
                                           unit=" domains")]


# Start the process and log the time it takes to complete it.
with open(r"domains.txt", 'r', encoding="utf-8") as file:
    domains = file
    start = time.time()
    # In case the script is executed on a Windows machine, this is needed.
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception as e:
        pass
    asyncio.run(main(domains))
    end = time.time()

print(f'It took {end - start} seconds to query {COUNT} domains.')
file.close()
errorfile.close()
