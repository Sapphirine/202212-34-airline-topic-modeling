import requests
import os
import json
import datetime as dt
from dateutil import parser
import sys

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")
bearer_token = "AAAAAAAAAAAAAAAAAAAAAElqjwEAAAAA8PRQduIf5nDumMCOqlgqpkL9QHo" \
               "%3D7d4vdi0UEJNMs9SmNH8nEQf9acD08THiUvzkJq3VfQzQJ4SSEf "

airline_user_id_config = {
    "@united": 260907612,
    "@AmericanAir": 22536055,
    "@SpiritAirlines": 21964954,
    "@Delta": 5920532
}

place_fields = [
    'full_name', 'id', 'country', 'country_code',
    'name', 'place_type'
]

tweet_fields = [
    'id', 'text', 'author_id', 'context_annotations',
    'conversation_id', 'created_at', 'entities',
    'in_reply_to_user_id', 'lang', 'public_metrics',
    'source', 'withheld'
]

user_fields = [
    'verified'
]

expansions = ['geo.place_id']


def create_mentions_url(handle):
    """Creates URL to query user mentions based on user_id config above. """
    user_id = airline_user_id_config.get(handle)
    # user_id = 783214
    if user_id:
        print(user_id)
        return "https://api.twitter.com/2/users/{}/mentions".format(user_id)
    return "Not a valid Twitter handle for project scope."


def get_params_v2(until_id="None"):
    """Instead of using the start_time/end_time parameters (which is not properly controlling the results... when
    passing in start_time and end_time together, it simply returns an empty 200 response) not working as
    expected...), we can use the last tweet ID from each request response to input that into the next request as its
    `until_id`. """

    params = {
        "max_results": 100,
        # 'start_time': start_time,
        # 'end_time': end_time,
        'expansions': ",".join(expansions),
        'tweet.fields': ",".join(tweet_fields),
        'user.fields': ",".join(user_fields),
        'place.fields': ",".join(place_fields)
    }

    if until_id != "None":
        params["until_id"] = until_id

    return params


# def get_params(start_time, end_time, next_token=None):
#
#     # params = {
#     #     "max_results": 100,
#     #     'start_time': start_time,
#     #     'end_time': end_time,
#     #     #'expansions': ",".join(expansions),
#     #     'tweet.fields': ",".join(tweet_fields),
#     #     #'user.fields': ",".join(user_fields),
#     #     #'place.fields': ",".join(place_fields)
#     # }
#
#     # params = {"tweet.fields": "id,text,author_id,context_annotations,conversation_id,created_at",
#     #         "max_results": 5}
#
#     params = {"tweet.fields": ",".join(tweet_fields),
#               'start_time': start_time,
#               'until_id': "1597810339177201664",
#               #'end_time': end_time,
#               "max_results": 5}
#
#     if next_token:
#         params['pagination_token'] = next_token
#
#     return params


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserMentionsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def get_json_path_to_save(handle, page_counter, until_id):
    # user_id = airline_user_id_config.get(handle)

    date_fmt = "%b-%d-%Y"
    run_time_str = dt.datetime.today().strftime(date_fmt)
    # start_time_str = parser.parse(start_time).strftime(date_fmt)
    # end_time_str = parser.parse(end_time).strftime(date_fmt)

    directory_name = f"run_{run_time_str}_{handle[1:]}"
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)

    path_to_save = f"{directory_name}/{handle[1:]}_{page_counter}_oldest_id_{until_id}.json"
    return path_to_save


def save_json_to_dir(json_response, path_to_save_json):
    with open(path_to_save_json, 'w') as outfile:
        json.dump(json_response, outfile)


def main_delta():
    # Test for a single day's worth of tweets: October 31st, 2022

    handle = "@Delta"
    # start_time = "2021-11-01T00:00:00Z"  # sep 01 2022
    # end_time = "2022-11-28T00:00:00Z"  # nov 10 2022
    url = create_mentions_url(handle)

    page_counter = 101  # TODO: Adjust manually for the time being!!!!

    until_id = "1596641451760570368"  # TODO: Take "oldest_id" from your most recent response json
    # until_id = "None"  # TODO: Take "oldest_id" from your most recent response json
    params = get_params_v2(until_id)
    json_response = connect_to_endpoint(url, params)

    try:
        oldest_id = json_response['meta']['oldest_id']
        path_to_save_json = get_json_path_to_save(handle, page_counter, oldest_id)
        save_json_to_dir(json_response, path_to_save_json)
    except KeyError:
        print(json.dumps(json_response, indent=4, sort_keys=True))
        sys.exit(0)

    # print(json.dumps(json_response, indent=4, sort_keys=True))
    # next_tok = json_response['meta'].get('next_token')

    max_counter = 200  # TODO: Adjust manually for the time being!!!!
    while page_counter < max_counter:
        page_counter += 1

        until_id = oldest_id
        params = get_params_v2(until_id)
        json_response = connect_to_endpoint(url, params)

        try:
            oldest_id = json_response['meta']['oldest_id']
            path_to_save_json = get_json_path_to_save(handle, page_counter, oldest_id)
            save_json_to_dir(json_response, path_to_save_json)
        except KeyError:
            print(json.dumps(json_response, indent=4, sort_keys=True))
            page_counter = max_counter + 1


def main_united():
    # Test for a single day's worth of tweets: October 31st, 2022

    handle = "@united"
    # start_time = "2021-11-01T00:00:00Z"  # sep 01 2022
    # end_time = "2022-11-28T00:00:00Z"  # nov 10 2022
    url = create_mentions_url(handle)

    page_counter = 27  # TODO: Adjust manually for the time being!!!!

    until_id = "1597255094835511296"  # TODO: Take "oldest_id" from your most recent response json
    # until_id = "None"
    params = get_params_v2(until_id)
    json_response = connect_to_endpoint(url, params)

    try:
        oldest_id = json_response['meta']['oldest_id']
        path_to_save_json = get_json_path_to_save(handle, page_counter, oldest_id)
        save_json_to_dir(json_response, path_to_save_json)
    except KeyError:
        print(json.dumps(json_response, indent=4, sort_keys=True))
        sys.exit(0)

    # print(json.dumps(json_response, indent=4, sort_keys=True))
    # next_tok = json_response['meta'].get('next_token')

    max_counter = 100  # TODO: Adjust manually for the time being!!!!
    while page_counter < max_counter:
        page_counter += 1

        until_id = oldest_id
        params = get_params_v2(until_id)
        json_response = connect_to_endpoint(url, params)

        try:
            oldest_id = json_response['meta']['oldest_id']
            path_to_save_json = get_json_path_to_save(handle, page_counter, oldest_id)
            save_json_to_dir(json_response, path_to_save_json)
        except KeyError:
            print(json.dumps(json_response, indent=4, sort_keys=True))
            page_counter = max_counter + 1

    # while next_tok:
    #     page_counter += 1
    #     params = get_params(start_time, end_time, next_token=next_tok)

    #     # Send request for next page of results
    #     json_response = connect_to_endpoint(url, params)
    #     path_to_save_json = get_json_path_to_save(handle, start_time, end_time, page_counter)
    #     save_json_to_dir(json_response, path_to_save_json)
    #     next_tok = json_response['meta'].get('next_token')

    # url = create_mentions_url()
    # params = get_params()
    # json_response = connect_to_endpoint(url, params)
    # print(json.dumps(json_response, indent=4, sort_keys=True))


# def main():
#     # Test for a single day's worth of tweets: October 31st, 2022
#
#     handle = "@united"
#     start_time = "2021-11-01T00:00:00Z"  # sep 01 2022
#     end_time = "2022-11-28T00:00:00Z"  # nov 10 2022
#     url = create_mentions_url(handle)
#
#     page_counter = 0
#
#     params = get_params(start_time, end_time)
#     json_response = connect_to_endpoint(url, params)
#     path_to_save_json = get_json_path_to_save(handle, start_time, end_time, page_counter)
#     save_json_to_dir(json_response, path_to_save_json)
#
#     next_tok = json_response['meta'].get('next_token')
#
#     # while next_tok:
#     #     page_counter += 1
#     #     params = get_params(start_time, end_time, next_token=next_tok)
#
#     #     # Send request for next page of results
#     #     json_response = connect_to_endpoint(url, params)
#     #     path_to_save_json = get_json_path_to_save(handle, start_time, end_time, page_counter)
#     #     save_json_to_dir(json_response, path_to_save_json)
#     #     next_tok = json_response['meta'].get('next_token')
#
#
#     # url = create_mentions_url()
#     # params = get_params()
#     # json_response = connect_to_endpoint(url, params)
#     # print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main_united()
    #main_delta()
