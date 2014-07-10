# **Yet Another Twitter User Timeline Crawler (YATUFC)**
----------

## **Introduction**

This program can crawl a given Twitter User timeline and output his/her tweets in a CSV file for further analysis. Also, it is possible to set a date range for which you are interested, therefore capturing only tweets in the desired timeslot.

**ATTENTION**: This method can only return up to 3,200 of a user's most recent Tweets, due to Twitter's API limitations. Also, be warned that Twitter imposes a requests per rate limit window of 180/user and 300/app, per timeslot of 15 minutes For more info about the API call in question, see [this](https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline).

## **Authors**
Read AUTHORS

## **Copyright**
Read LICENSE

## **Install**

 1. pip3 install -r /path/to/requirements.txt
 2. chmod +x yatufc
 3. ./yatufc ...


