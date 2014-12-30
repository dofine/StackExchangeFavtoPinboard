# coding=utf-8

from __future__ import print_function
import time
import argparse
import requests

SEAPI = "https://api.stackexchange.com/2.2/users"
PINBOARDAPI = "https://api.pinboard.in/v1/posts/add"
RATE_LIM = 3


def get_sites(account_id):
    """

    Return associated sites of `account_id`.

    """
    resp = requests.get(SEAPI + "/{}".format(account_id) + "/associated")
    return resp


def get_favs(site, user_id):
    """

    Get favs of `user_id` in `site`.

    """
    parameters = {
        "order": "desc",
        "sort": "added",
        "site": site
    }
    resp = requests.get(SEAPI + "/{}".format(user_id) + '/favorites',
                        params=parameters)
    return resp.json()


def add_pinboard(auth_token, url, description, tags):
    parameters = {
        "auth_token": auth_token,
        "url": url,
        "description": description,
        "tags": tags
    }
    posted = False
    resp = requests.get(PINBOARDAPI, params=parameters)
    if resp.status_code == 200 and 'done' in resp.content:
        print("Posted link {}".format(url))
        posted = True
    elif resp.status_code == 200 and 'exists' in resp.content:
        print("Link {} skipped. Already Exists!".format(url))
        posted = True
    elif resp.status_code == 429:
        # 429 too many requests
        RATE_LIM = RATE_LIM * 2
        print("Exceeding Pinboard API rate limit. Increased to {}"
              .format(RATE_LIM))
    time.sleep(RATE_LIM)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='pin se fav to pinboard.')
    parser.add_argument('se_account_id', help='StackExchange Account ID')
    parser.add_argument('pinboard_user_token', help='Pinboard.in User token')
    args = parser.parse_args()
    se_response = get_sites(args.se_account_id)
    for each in se_response.json()['items']:
        favs = get_favs(each['site_url'].replace('http://', '').
                        replace('.stackexchange', '').replace('.com', ''),
                        each['user_id'])
        for fav in favs['items']:
            title = fav['title']
            tags = fav['tags']
            link = fav['link']
            add_pinboard(args.pinboard_user_token, link, title,
                         ','.join(tags) + ', StackExchangeFavs')
