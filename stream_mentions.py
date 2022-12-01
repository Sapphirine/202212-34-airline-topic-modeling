import requests
import os
import json

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")
bearer_token = "AAAAAAAAAAAAAAAAAAAAAElqjwEAAAAA8PRQduIf5nDumMCOqlgqpkL9QHo%3D7d4vdi0UEJNMs9SmNH8nEQf9acD08THiUvzkJq3VfQzQJ4SSEf"

# Create rules to run filtered stream

# Create list of airlines to filter out from airline-specific mention-tweets
popular_us_airline_twitter_handles = [
    "@JetBlue", "@SouthwestAir", "@AmericanAir", "@Delta",
    "@VirginAmerica", "@united", "@AlaskaAir", "@HawaiianAir",
    "@SpiritAirlines"
]


def build_airline_rule(handle):
    handle_wo_punc = handle[1:]
    airline_rule = f"({handle} lang:en -from:{handle_wo_punc})"
    # airline_rule = f"({handle} has:geo lang:en -from:{handle_wo_punc})"
    # lst_airlines_exclude_curr_handle = [airline_hdl for airline_hdl in popular_us_airline_twitter_handles if airline_hdl != handle]
    # for airline_hdl in lst_airlines_exclude_curr_handle:
    #     airline_rule += f" -{airline_hdl}"

    return airline_rule


airline_rules = []
airlines_to_query = [
    "@united",
    # "@SpiritAirlines"
]

for arln_hdl in airlines_to_query:
    arln_rule = build_airline_rule(arln_hdl)
    airline_rules.append({'value': arln_rule, 'tag': arln_hdl[1:]})


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    # sample_rules = [
    #     {"value": "@united has:geo lang:en - from:united", "tag": "United"},
    #     {"value": "@SpiritAirlines has:geo lang:en - from:SpiritAirlines", "tag": "Spirit"}
    #     # {"value": "dog has:images", "tag": "dog pictures"},
    #     # {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    # ]
    # sample_rules = airline_rules
    # payload = {"add": sample_rules}
    payload = {"add": airline_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for i, response_line in enumerate(response.iter_lines()):
        if response_line:
            json_response = json.loads(response_line)
            print(json.dumps(json_response, indent=4, sort_keys=True))

            airline_tag = json_response['matching_rules'][0]['tag']
            if not os.path.isdir(airline_tag):
                os.mkdir(airline_tag)
            with open(f'{airline_tag}/tweet_{i}.json', 'a') as outfile:
                json.dump(json_response, outfile)


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    r_set = set_rules(delete)
    get_stream(r_set)


if __name__ == "__main__":
    main()
