#!/usr/bin/env python3

import os

import twython as tw
import pandas as pd

from time import sleep
from datetime import datetime, date
from argparse import ArgumentParser

DATE_FORMAT = '%a %b %d %H:%M:%S +0000 %Y'


def _create_date(string):
    return datetime.strptime(string, '%Y-%m-%d').date()


def _create_twython(app_key, app_secret, oauth_token, oauth_token_secret):
    return tw.Twython(app_key, app_secret, oauth_token, oauth_token_secret)


def _parse_arguments():
    parser = ArgumentParser(
        prog='YATUFC',
        description='This program can crawl a given Twitter user timeline '
        'or simply search for a provided term, in order to output found tweets '
        'in a CSV file for further analysis. Also, it is possible to set a date '
        'range for which you are interested, therefore capturing only tweets in '
        'the desired timeslot.',
        epilog='ATTENTION: Twitter API is rate limited. The rates per endpoint '
        'are described in https://developer.twitter.com/en/docs/basics/rate-limits. '
        'If YATUFC hits one of those limits, it\'ll sleep for 15 minutes after when '
        'they\'re finally reset.')
    parser.add_argument(
        '-s', '--since', type=_create_date, required=False,
        default='0001-1-1', metavar='YEAR-MONTH-DAY',
        help='a date in the format YEAR-MONTH-DAY (default: no limit)')
    parser.add_argument(
        '-u', '--upTo', type=_create_date, required=False,
        default=date.today().isoformat(), metavar='YEAR-MONTH-DAY',
        help='a date in the format YEAR-MONTH-DAY (default: now)')
    parser.add_argument(
        '-o', '--outputFilePath', type=str, required=False,
        metavar='outputFilePath', default='output.csv',
        help='a path to save the output data (default: output.csv)')

    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    parser_profile = subparsers.add_parser('profile')
    parser_profile.add_argument('profileName', metavar='the profile name to crawl.')

    parser_search = subparsers.add_parser('search')
    parser_search.add_argument('searchTerm', metavar='the search term to crawl.')

    return parser.parse_args()


def _fetch_from_profile(twitter_session, term, max_id):
    results = twitter_session.get_user_timeline(screen_name=term,
                                                max_id=max_id,
                                                count=200)

    return results


def _fetch_from_search(twitter_session, term, max_id):
    results = twitter_session.search(q=term,
                                     max_id=max_id,
                                     count=200)

    return results['statuses'] if 'statuses' in results else []


def _generate_profile_dataframe(fetch_tweets, term, since, up_to):
    '''Return a dataframe filled with the crawled tweets.'''
    tweets_df = pd.DataFrame(
        columns=['creationDate', 'creationTime', 'profileName', 'profileFollowersCount',
                 'profileFriendsCount', 'profileListsInCount', 'profileFavoritesCount',
                 'profileTweetsCount', 'retweetsCount', 'favoritesCount', 'tweet'])
    tweets_df.set_index(['creationDate', 'creationTime'], inplace=True)

    max_id = None

    while True:
        try:
            twitter_session = _get_twitter_session()
            results = fetch_tweets(twitter_session, term, max_id)
        except tw.TwythonRateLimitError as ex:
            msg, *_ = ex.args
            # Sleep for 15 minutes and try again, as recommended by the docs.
            print('WARNING: Twitter API returned a 429 (Too Many Requests), Rate limit exceeded. '
                  'This program will sleep for 15 minutes after when the limits are finally reset.')
            sleep((15 * 60) + 1)
            continue
        except (tw.TwythonAuthError, tw.TwythonError) as ex:
            msg, *_ = ex.args
            raise RuntimeError('ERROR: ' + msg + '.')

        if not results:
            print('>>> Either no more data available or time range/rate limits were hit.')
            break

        for tweet in results:
            created_date = datetime.strptime(tweet['created_at'],
                                             DATE_FORMAT).date()
            created_time = datetime.strptime(tweet['created_at'],
                                             DATE_FORMAT).time()

            if created_date < since:
                return tweets_df

            max_id = tweet['id']

            if created_date >= since and created_date <= up_to:
                row = {'creationDate': created_date.isoformat(),
                       'creationTime': created_time.isoformat(),
                       'profileName': tweet['user']['screen_name'],
                       'profileFollowersCount': tweet['user']['followers_count'],
                       'profileFriendsCount': tweet['user']['friends_count'],
                       'profileListsInCount': tweet['user']['listed_count'],
                       'profileFavoritesCount': tweet['user']['favourites_count'],
                       'profileTweetsCount': tweet['user']['statuses_count'],
                       'retweetsCount': tweet['retweet_count'],
                       'favoritesCount': tweet['favorite_count'],
                       'tweet': tweet['text']}
                tweets_df = tweets_df.append(row, ignore_index=True)

        max_id -= 1

    return tweets_df

def _get_twitter_session():
    auth_files = ['app_key', 'app_secret', 'oauth_token', 'oauth_token_secret']
    credentials = {}

    for file_name in auth_files:
        if not os.path.isfile(file_name) or not os.access(file_name, os.R_OK):
            raise IOError('Either file \"{}\" is missing or '
                          'is not readable. It is required for '
                          'authentication, so please register your Twitter '
                          'APP first and save the respective credential in a '
                          'file at the same folder of this executable.'.format(file_name))
        else:
            with open(file_name, 'r') as file:
                credentials[file_name] = file.readline()[:-1]

    return _create_twython(**credentials) # pylint: disable=star-args

def main():
    '''Main function.'''
    arguments = _parse_arguments()

    if arguments.since > arguments.upTo:
        raise ValueError('ERROR: You cannot set since\'s date after upTo.')
    elif arguments.upTo > date.today():
        raise ValueError('ERROR: Thou shalt not crawl tweets from the future.')

    print('Yet Another Twitter User Timeline Crawler (YATUFC)')
    print('*** Started crawling!!!')

    fetch_tweets = None
    term = None

    if arguments.command == 'profile':
        fetch_tweets = _fetch_from_profile
        term = arguments.profileName
    elif arguments.command == 'search':
        fetch_tweets = _fetch_from_search
        term = arguments.searchTerm
    else:
        raise ValueError('ERROR: Unknown sub-command.')

    tweets = _generate_profile_dataframe(fetch_tweets,
                                         term,
                                         arguments.since,
                                         arguments.upTo)
    print('*** Finished crawling!!!')
    print('*** Total of Tweets: ' + str(len(tweets)))
    print('*** Output was saved in ' + arguments.outputFilePath)

    tweets.to_csv(arguments.outputFilePath)

if __name__ == "__main__":
    main()
