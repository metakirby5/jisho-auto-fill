# -*- coding: utf-8 -*-
"""
Utils for parsing results from Jisho.
"""

import json
from typing import Any, Dict, Optional, Sequence
from urllib.parse import quote
from urllib.request import urlopen

from anki.notes import Note
from aqt.utils import showInfo, showCritical

from . import config

JISHO_SEARCH = 'https://jisho.org/api/v1/search/words?keyword={0}'


def fetch(search: str) -> Optional[Dict[str, Any]]:
    url = JISHO_SEARCH.format(quote(search.encode('utf8')))

    try:
        response = urlopen(url).read()
        data = json.loads(response)
    except IOError:
        showCritical('Cannot reach Jisho.')
        return

    try:
        return data['data'][0]
    except (IndexError, KeyError):
        showInfo('No results from Jisho.')
        return


def set_note_data(note, data):
    jp = data['japanese'][0]
    word = try_get_data(jp, 'word', 'reading')
    try_set_field(note, config.word_field, word)
    reading = try_get_data(jp, 'reading')
    try_set_field(note, config.reading_field, reading)
    senses = try_get_data(data, 'senses')
    try_set_field(note, config.meaning_field, get_meaning(senses))


def get_meaning(senses: Optional[Sequence[Dict[str, Sequence[str]]]]) \
        -> Optional[str]:
    if not senses:
        return None

    return f'''<dl>{''.join(
        f'<dt>{get_parts_of_speech(sense)}</dt>'
        f'<dd>{get_definition(sense)}</dd>'
        for sense in senses
    )}</dl>'''


def get_parts_of_speech(sense: Dict[str, Sequence[str]]) -> str:
    return ', '.join(sense['parts_of_speech'])


def get_definition(sense: Dict[str, Sequence[str]]) -> str:
    return '; '.join(sense['english_definitions'])


def try_get_data(data: Dict[str, str], *keys: str) -> Optional[Any]:
    for key in keys:
        try:
            return data[key]
        except KeyError:
            pass
    return None


def try_set_field(note: Note, key: str, value: Any):
    if not (key and value):
        return

    try:
        note[key] = value
    except KeyError:
        pass
