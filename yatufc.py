#!/usr/bin/env python3

import os

import twython as tw
import pandas as pd

from datetime import datetime, date
from argparse import ArgumentParser

def create_date(string):
    '''Return a date instance.'''
    return datetime.strptime(string, '%Y-%m-%d').date()

def create_twython(app_key, app_secret, oauth_token, oauth_token_secret):
    '''Return a twython instance.'''
    return tw.Twython(app_key, app_secret, oauth_token, oauth_token_secret)

def parse_arguments():
    '''Return command line arguments.'''
    parser = ArgumentParser(
        prog='YATUFC',
        description='Yet Another Twitter User Timeline Crawler (YATUFC) can '
        'crawl a given Twitter user timeline and output his/her tweets to a '
        'CSV file for further analysis.',
        epilog='ATTENTION: This program can only return up to 3,200 of a '
        'user\'s most recent Tweets, due to Twitter\'s API limitations. '
        'Also, be warned that Twitter imposes a requests per rate limit '
        'window of 180/user and 300/app, per timeslot of 15 minutes For more '
        'info about the API call in question, see '
        'https://dev.twitter.com/docs/api/1.1/get/statuses/user_timeline.')
    parser.add_argument(
        '-s', '--since', type=create_date, required=False,
        default='0001-1-1', metavar='YEAR-MONTH-DAY',
        help='a date in the format YEAR-MONTH-DAY (default: no limit)')
    parser.add_argument(
        '-u', '--upTo', type=create_date, required=False,
        default=date.today().isoformat(), metavar='YEAR-MONTH-DAY',
        help='a date in the format YEAR-MONTH-DAY (default: now)')
    parser.add_argument(
        '-o', '--outputFilePath', type=str, required=False,
        metavar='outputFilePath', default='output.csv',
        help='a path to save the output data (default: output.csv)')
    parser.add_argument('profileName', metavar='the profile name to crawl.')
    return parser.parse_args()

def generate_tweets_table(twitter, profile_name, since, up_to):
    '''Return a dataframe filled with the crawled tweets.'''
    tweets = pd.DataFrame(
        columns=['creationDate', 'creationTime', 'profileName',
                 'totalOfRetweets', 'totalOfFavourites', 'tweet'])
    tweets.set_index(['creationDate', 'creationTime'], inplace=True)

    max_id = None
    date_format = '%a %b %d %H:%M:%S +0000 %Y'

    while True:
        try:
            results = twitter.get_user_timeline(screen_name=profile_name,
                                                max_id=max_id,
                                                count=200)
        except tw.TwythonRateLimitError as ex:
            msg, *_ = ex.args
            raise Exception('ERROR: ' + msg + '. Try again after 15 minutes.')
        except (tw.TwythonAuthError, tw.TwythonError) as ex:
            msg, *_ = ex.args
            raise Exception('ERROR: ' + msg + '.')

        if not results:
            print('>>> Limit of 3200 tweets reached.')
            break

        for tweet in results:
            created_date = datetime.strptime(tweet['created_at'],
                                             date_format).date()
            created_time = datetime.strptime(tweet['created_at'],
                                             date_format).time()

            if created_date < since:
                return tweets

            max_id = tweet['id']

            if created_date >= since and created_date <= up_to:
                row = {'creationDate':created_date.isoformat(),
                       'creationTime':created_time.isoformat(),
                       'profileName':profile_name,
                       'totalOfRetweets':tweet['retweet_count'],
                       'totalOfFavourites':tweet['favorite_count'],
                       'tweet':tweet['text']}
                tweets = tweets.append(row, ignore_index=True)

        max_id -= 1

    return tweets

def main():
    '''Main function.'''
    arguments = parse_arguments()

    if arguments.since > arguments.upTo:
        raise Exception('ERROR: You cannot set since\'s date after upTo.')
    elif arguments.upTo > date.today():
        raise Exception('ERROR: Thou shalt not crawl tweets from the future.')

    auth_files = ['app_key', 'app_secret', 'oauth_token', 'oauth_token_secret']
    credentials = {}

    for file_name in auth_files:
        if not os.path.isfile(file_name) or not os.access(file_name, os.R_OK):
            raise Exception('Either file \"' + file_name + '\" is missing or '
                            'is not readable. It is required for '
                            'authentication, so please register your Twitter '
                            'APP first and save the respective credential in a '
                            'file at the same folder of this executable.')
        else:
            with open(file_name, 'r') as file:
                credentials[file_name] = file.readline()[:-1]

    twython_instance = create_twython(**credentials) # pylint: disable=star-args

    print('Yet Another Twitter User Timeline Crawler (YATUFC)')
    print('*** Started crawling!!!')
    tweets = generate_tweets_table(twython_instance,
                                   arguments.profileName,
                                   arguments.since,
                                   arguments.upTo)
    print('*** Finished crawling!!!')
    print('*** Total of Tweets: ' + str(len(tweets)))
    print('*** Output was saved in ' + arguments.outputFilePath)

    tweets.to_csv(arguments.outputFilePath)

if __name__ == "__main__":
    main()
