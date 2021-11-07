import requests


def search_request(query):
    response = requests.get("https://cre-api-v2.kufar.by/items-search/v1/engine/v1/search/rendered-paginated",
                            params={'rgn': "7", 'ot': "1", 'query': query, 'size': "42", 'lang': "ru"}
                            )
    json_ads_ = response.json()['ads']
    return json_ads_['ad_link']

