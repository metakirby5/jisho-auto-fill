# -*- coding: utf-8 -*-
"""
Adds a menu item to auto-fill word, reading, and meaning from jisho.org.
Globally bound to Ctrl+Shift+J.

Based on https://ankiweb.net/shared/info/1545080191.
"""

from typing import Optional

import aqt.qt as qt
from PyQt5 import QtCore
from anki.notes import Note
from aqt import mw, gui_hooks
from aqt.editor import Editor
from aqt.utils import getOnlyText, getTag, showInfo, showCritical

from . import config
from . import pickers
from . import jisho

menu = qt.QMenu('&Jisho Auto-Fill', mw)

batch_create_action = menu.addAction('&Batch Create')

fill_card_action = menu.addAction('&Current Card')
fill_card_action.setShortcut(config.shortcut)
fill_card_action.setShortcutContext(QtCore.Qt.ApplicationShortcut)

mw.form.menuTools.addMenu(menu)

editor: Optional[Editor] = None


def loaded_note(note_editor: Editor) -> None:
    global editor
    editor = note_editor
    fill_card_action.setEnabled(bool(editor and editor.note))


gui_hooks.editor_did_load_note.append(loaded_note)


def batch_create() -> None:
    if not config.note:
        showCritical("No note type configured.")
        return

    model = mw.col.models.byName(config.note)
    if not model:
        showCritical(f"No note type with name {config.note}.")

    deck_id = pickers.select_deck_id("Select the destination.")
    if deck_id is None:
        showCritical("No decks!")
        return

    # TODO(!): Change to multi-line input.
    terms_text = getOnlyText("Enter each term separated by a newline.")
    if not terms_text:
        showInfo("No terms to create.")
        return

    # noinspection PyTypeChecker
    tags_text, _ = getTag(mw, mw.col, "Enter tags for created cards.")

    terms = terms_text.splitlines()

    def create_cards() -> None:
        for term in terms:
            data = jisho.fetch(term)
            note = Note(mw.col, model)
            jisho.set_note_data(note, data)
            note.setTagsFromStr(tags_text)
            mw.col.add_note(note, deck_id)

        mw.autosave()

    mw.taskman.with_progress(create_cards, label="Creating cards...")


qt.qconnect(batch_create_action.triggered, batch_create)


def fill_card() -> None:
    if not (editor and editor.note):
        showInfo('Not editing a note.')
        fill_card_action.setEnabled(False)
        return

    def fill_meaning() -> None:
        if not config.lookup_field:
            showCritical('No lookup field configured.')
            return

        if not (editor and editor.note):
            showCritical('No note to save.')
            return

        note = editor.note

        try:
            term = note[config.lookup_field]
        except KeyError:
            showCritical(f'{config.lookup_field} not in note.')
            return
        if not term:
            showInfo(f'{config.lookup_field} is empty.')
            return

        data = jisho.fetch(term)
        jisho.set_note_data(note, data)

        editor.loadNoteKeepingFocus()

    editor.saveNow(fill_meaning)


qt.qconnect(fill_card_action.triggered, fill_card)
