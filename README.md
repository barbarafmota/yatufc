# **Yet Another Twitter User Timeline Crawler (YATUFC)**
----------

## **Introduction**

This program can crawl a given Twitter user timeline or simply search for a provided term, in order to output found tweets in a CSV file for further analysis. Also, it is possible to set a date range for which you are interested, therefore capturing only tweets in the desired timeslot.

**ATTENTION**: Twitter API is rate limited. The rates per endpoint are described in [here](https://developer.twitter.com/en/docs/basics/rate-limits). If YATUFC hits one of those limits, it'll sleep for 15 minutes after when they're finally reset.

## **Authors**
Read AUTHORS

## **Copyright**
Read LICENSE

## **Install**

 1. pip3 install -r /path/to/requirements.txt
 2. chmod +x yatufc
 3. ./yatufc ...
