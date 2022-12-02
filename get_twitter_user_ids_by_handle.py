bearer_token = "AAAAAAAAAAAAAAAAAAAAAElqjwEAAAAA8PRQduIf5nDumMCOqlgqpkL9QHo%3D7d4vdi0UEJNMs9SmNH8nEQf9acD08THiUvzkJq3VfQzQJ4SSEf"

# Get twitter user ID by handle

import requests
import os
import json


def create_url(user_handle_lst):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    # usernames = "usernames=TwitterDev,TwitterAPI"
    usernames = "usernames=" + ",".join([usr_hndl[1:] for usr_hndl in user_handle_lst])
    user_fields = "user.fields=id"
    url = "https://api.twitter.com/2/users/by?{}&{}".format(usernames, user_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth, )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


if __name__ == "__main__":
    with open("bookmarks_twitter_airlines.txt", "r") as myfile:
        bookmarks = myfile.read().splitlines()
    twitter_airline_handles = [bkmk.split("(")[1].split(")")[0] for bkmk in bookmarks]
    url = create_url(twitter_airline_handles)
    json_response = connect_to_endpoint(url)
    with open("airline_account_handles_and_ids.json", 'w') as outfile:
        json.dump(json_response, outfile)
