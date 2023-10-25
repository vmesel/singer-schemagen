import json
from datetime import datetime
from singer_sdk import typing as th

json_to_process = """"""

TYPES = {
    "str": "th.StringType",
    "int": "th.IntegerType",
    "float": "th.NumberType",
    "bool": "th.BooleanType",
    "NoneType": "th.StringType",
    "datetime": "th.DateTimeType",
    "date": "th.DateType"
}
DATE_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M%z",
    "%Y-%m-%d",
]


def transform_date(date):
    date_obj = None
    for date_format in DATE_FORMATS:
        try:
            date_obj = datetime.strptime(date, date_format)

        except (ValueError, TypeError):
            pass

    if date_obj:
        return date_obj

    raise ValueError("Invalid date format")

def iterate_through_keys(json_obj):
    keys_and_singer_type = {}
    for key in json_obj.keys():
        if isinstance(json_obj[key], dict):
            keys_and_singer_type[key] = iterate_through_keys(json_obj[key])

        elif isinstance(json_obj[key], list):
            keys_and_singer_type[key] = []
            for item in json_obj[key][:1]:
                keys_and_singer_type[key].append(
                    iterate_through_keys(item)
                )
        elif isinstance(json_obj[key], str):
            try:
                keys_and_singer_type[key] = TYPES[type(transform_date(json_obj[key])).__name__]
            except ValueError:
                keys_and_singer_type[key] = TYPES[type(json_obj[key]).__name__]

        else:
            keys_and_singer_type[key] = TYPES[type(json_obj[key]).__name__]

    return keys_and_singer_type

json_to_process = json.loads(json_to_process)
pre_processed_json = iterate_through_keys(json_to_process)

def generate_schema(json_obj, start_schema = False, level=0):
    if start_schema:
        schema = "th.PropertiesList(\n"
    else:
        schema = ""
    schema += "\t" * level
    for key in json_obj.keys():
        if isinstance(json_obj[key], dict):
            schema += "\t" * (level + 1)
            schema += "th.ObjectType("
            for dict_key, dict_val in json_obj[key].items():
                schema += generate_schema({dict_key: dict_val}, level = level + 2)
            schema += "),\n"

        elif isinstance(json_obj[key], list):
            for item in json_obj[key]:
                schema += f'th.Property("{key}",\n'
                if isinstance(item, dict):
                    schema += f'th.ArrayType(\nth.ObjectType(\n{generate_schema(item)}))),\n'
                else:
                    schema += f'th.ArrayType(\n\n{generate_schema(item)})),\n'
        else:
            schema += "\t" * (level + 1)
            schema += f'th.Property("{key}", {json_obj[key]}),\n'

    if start_schema:
        return schema + "\n)"
    else:
        return schema

print(generate_schema(pre_processed_json, start_schema=True))