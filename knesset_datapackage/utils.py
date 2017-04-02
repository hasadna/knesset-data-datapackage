import logging, sys, os
from shutil import rmtree
import json
import datetime
import jsontableschema


def setup_logging(debug=False):
    logLevel = logging.DEBUG if debug else logging.INFO
    [logging.root.removeHandler(handler) for handler in tuple(logging.root.handlers)]
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("%(name)s:%(lineno)d\t%(levelname)s\t%(message)s"))
    stdout_handler.setLevel(logLevel)
    logging.root.addHandler(stdout_handler)
    logging.root.setLevel(logLevel)


def setup_datapath(path=None, delete=False):
    if not path:
        path = os.path.abspath(os.path.join(os.getcwd(), "data"))
    if os.path.exists(path) and delete:
        rmtree(path)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def merge_table_schemas(*schemas):
    merged_schema = {"fields": []}
    for schema in schemas:
        if schema.keys() == ["fields"]:
            for field in schema["fields"]:
                if field["name"] in [f["name"] for f in merged_schema["fields"]]:
                    raise Exception("field {} appears in more then 1 merged schema".format(field["name"]))
                else:
                    merged_schema["fields"].append(field)
        else:
            raise Exception("merge_table_schemas only supports fields attribute in merged schemas")
    return merged_schema


def uncast_value(value, schema):
    if schema["type"] == "integer" and isinstance(value, int):
        return str(value).encode("utf-8")
    elif schema["type"] == "string":
        if isinstance(value, str):
            return value.decode("utf-8")
        elif isinstance(value, unicode):
            return value
        elif isinstance(value, (datetime.datetime, datetime.date)):
            # this is a very common case where people use string type but value is actually a date/time
            # usually we don't want to have this kind of behavior - but for this case it's what the people want
            return value.isoformat()
        else:
            return json.dumps(value) if value is not None else u""
    elif schema["type"] in ("date", "datetime") and isinstance(value, (datetime.datetime, datetime.date)):
        if "format" in schema:
            if schema["format"].startswith("fmt:"):
                return value.strftime(schema["format"][4:])
            else:
                raise Exception("I don't know how to parse {} format {}".format(schema["type"], schema["format"]))
        else:
            return value.isoformat()
    elif schema["type"] == "array" and isinstance(value, (list, tuple)):
        return json.dumps(value)
    elif value is None:
        return u""
    else:
        raise Exception("sorry, I don't know how to uncast field_schema {} for value '{}'".format(schema, value))


def cast_value(value, schema):
    return jsontableschema.Field(schema).cast_value(value)
