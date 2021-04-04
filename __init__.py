# -*- coding: utf-8 -*-
"""
Adds a menu item to auto-fill word, reading, and meaning from jisho.org.
Globally bound to Ctrl+Shift+J.
"""

import json
from typing import Optional, Any, Dict, Sequence
from urllib.parse import quote
from urllib.request import urlopen

import aqt.qt as qt
from PyQt5 import QtCore
from anki.notes import Note
from aqt import mw, gui_hooks
from aqt.editor import Editor
from aqt.utils import showInfo

# TODO: Add configuration

JISHO_SEARCH = 'https://jisho.org/api/v1/search/words?keyword={0}'
LOOKUP_FIELD = 'Expression'
WORD_FIELD = 'Expression'
READING_FIELD = 'Reading'
MEANING_FIELD = 'Meaning'

editor: Optional[Editor] = None


def loaded_note(note_editor: Editor) -> None:
    global editor
    editor = note_editor


gui_hooks.editor_did_load_note.append(loaded_note)


def jisho_import() -> None:
    if not (editor and editor.note):
        showInfo('Not editing a note.')
        return

    editor.saveNow(fill_meaning)


def fill_meaning() -> None:
    if not (editor and editor.note):
        showInfo('No note to save.')
        return

    note = editor.note

    try:
        word = note[LOOKUP_FIELD]
    except KeyError:
        showInfo(f'{LOOKUP_FIELD} not in note.')
        return
    if not word:
        showInfo(f'{LOOKUP_FIELD} is empty.')
        return

    url = JISHO_SEARCH.format(quote(word.encode('utf8')))

    try:
        response = urlopen(url).read()
        data = json.loads(response)
    except IOError:
        showInfo('Cannot reach Jisho.')
        return

    try:
        data = data['data'][0]
        jp = data['japanese'][0]
    except (IndexError, KeyError):
        showInfo('No results from Jisho.')
        return

    word = try_get_data(jp, 'word', 'reading')
    try_set_field(note, WORD_FIELD, word)

    reading = try_get_data(jp, 'reading')
    try_set_field(note, READING_FIELD, reading)

    senses = try_get_data(data, 'senses')
    try_set_field(note, MEANING_FIELD, get_meaning(senses))

    editor.loadNoteKeepingFocus()
    return


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
    showInfo(f'{", ".join(keys)} not in Jisho data.')
    return None


def try_set_field(note: Note, key: str, value: Any):
    if not (key and value):
        return

    try:
        note[key] = value
    except KeyError:
        showInfo(f'{key} not in note.')


action = qt.QAction('&Jisho Auto-Fill', mw)
action.setShortcut('Ctrl+Shift+J')
action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
qt.qconnect(action.triggered, jisho_import)
mw.form.menuTools.addAction(action)
