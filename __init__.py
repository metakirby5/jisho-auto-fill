# -*- coding: utf-8 -*-
"""
Adds a menu item to auto-fill word, reading, and meaning from jisho.org.
Globally bound to Ctrl+Shift+J.

Based on https://ankiweb.net/shared/info/1545080191.
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

JISHO_SEARCH = 'https://jisho.org/api/v1/search/words?keyword={0}'

config = mw.addonManager.getConfig(__name__)
shortcut = config['hotkey']
fields = config['fields']
lookup_field = fields['lookup']
word_field = fields['word']
reading_field = fields['reading']
meaning_field = fields['meaning']

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

    if not lookup_field:
        showInfo('No lookup field.')
        return

    try:
        word = note[lookup_field]
    except KeyError:
        showInfo(f'{lookup_field} not in note.')
        return
    if not word:
        showInfo(f'{lookup_field} is empty.')
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
    try_set_field(note, word_field, word)

    reading = try_get_data(jp, 'reading')
    try_set_field(note, reading_field, reading)

    senses = try_get_data(data, 'senses')
    try_set_field(note, meaning_field, get_meaning(senses))

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
action.setShortcut(shortcut)
action.setShortcutContext(QtCore.Qt.ApplicationShortcut)
qt.qconnect(action.triggered, jisho_import)
mw.form.menuTools.addAction(action)
