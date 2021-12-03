def delete_keys_from_dict(dictionary, keys):
    keys_set = set(keys)

    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, dict):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            elif isinstance(value, list):
                for i in value:
                    modified_dict[key] = delete_keys_from_dict(i, keys_set)
            else:
                modified_dict[key] = value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
    return modified_dict


def get_query_from_storage(search_dict, query_id) -> dict:
    for key, value in search_dict.items():

        if key == "query_id" and value == query_id:
            return search_dict

        elif isinstance(value, dict):
            result = get_query_from_storage(value, query_id)
            if result:
                return result

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = get_query_from_storage(item, query_id)
                    if result:
                        return result
