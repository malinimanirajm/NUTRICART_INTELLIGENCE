"""memory/utils.py"""

"""
memory/utils.py


"""

import json
from dataclasses import asdict


def to_dict(obj):

    return asdict(obj)


def to_json(obj):

    return json.dumps(
        to_dict(obj),
        default=str,
    )


def from_json(text):

    return json.loads(text)