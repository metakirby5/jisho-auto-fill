# -*- coding: utf-8 -*-
"""
Adds a menu item to auto-fill word, reading, and meaning from jisho.org.
Globally bound to Ctrl+Shift+J.

Based on https://ankiweb.net/shared/info/1545080191.
"""
from concurrent.futures import Future
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional, Set

import aqt.qt as qt
from PyQt5 import QtCore
from anki.notes import Note
from aqt import mw, gui_hooks
from aqt.editor import Editor
from aqt.utils import getOnlyText, getTag, showInfo, showWarning, showCritical

from . import config
from . import jisho
from . import proxies
from . import util

menu = qt.QMenu('&Jisho Auto-Fill', mw)

batch_create_action = menu.addAction('&Batch Create')

fill_card_action = menu.addAction('&Current Card')
fill_card_action.setShortcut(config.shortcut)
fill_card_action.setShortcutContext(QtCore.Qt.ApplicationShortcut)

mw.form.menuTools.addMenu(menu)

editors: Set[Optional[Editor]] = set()


def get_editor():
    return next(filter(lambda x: x.currentField is not None, editors), None)


gui_hooks.editor_did_load_note.append(editors.add)
gui_hooks.editor_did_unfocus_field.append(lambda c, n, i: fill_card_action.setEnabled(False))
gui_hooks.editor_did_focus_field.append(lambda n, i: fill_card_action.setEnabled(True))


def batch_create() -> None:
    if not config.note:
        showCritical("No note type configured.")
        return

    col = mw.col
    model = col.models.byName(config.note)
    if not model:
        showCritical(f"No note type with name {config.note}.")
        return

    deck_id = util.select_deck_id("Select the destination.")
    if deck_id is None:
        showCritical("No decks.")
        return

    terms_text = getOnlyText("Enter each term separated by a newline.", edit=proxies.QMultiLineEdit())
    if not terms_text:
        showInfo("No terms to create.")
        return

    # noinspection PyTypeChecker
    tags_text, tags_ok = getTag(mw, col, "Enter tags for created cards.")
    if not tags_ok:
        return

    terms = [x.strip() for x in terms_text.splitlines() if x]
    tags = col.tags.split(tags_text)
    missing = []
    changed = []
    dupes = []

    def create_cards() -> None:
        with ThreadPoolExecutor() as executor:
            for term, data in zip(terms, executor.map(jisho.fetch_with_retry, terms)):
                note = Note(col, model)
                word = term

                if data:
                    word = jisho.set_note_data(note, data)
                else:
                    note[config.word_field] = word
                    missing.append(term)
                    util.try_add_tag(note, config.missing_tag)

                def apply_tags(target: Note):
                    if term != word:
                        changed.append(f"{term} → {word}")
                        util.try_add_tag(target, config.changed_tag)

                    target.tags.extend(tags)

                if not note.dupeOrEmpty():
                    util.try_add_tag(note, config.added_tag)
                    apply_tags(note)
                    col.add_note(note, deck_id)
                    continue

                dupes.append(word)
                for nid in col.find_notes(f"{config.word_field}:{word}"):
                    existing_note = col.getNote(nid)
                    util.try_add_tag(existing_note, config.duplicate_tag)
                    apply_tags(existing_note)
                    existing_note.flush()

    def finish(_: Future) -> None:
        mw.autosave()
        mw.reset()
        showInfo("Done!")

        if missing:
            showWarning(f"Lookup failed:\n\n" + '\n'.join(missing))

        if changed:
            showWarning(f"Terms differed from search result:\n\n" + '\n'.join(changed))

        if dupes:
            showWarning(f"Merged tags of duplicates:\n\n" + '\n'.join(dupes))

    mw.taskman.with_progress(create_cards, finish, label="Creating cards...")


qt.qconnect(batch_create_action.triggered, batch_create)


def fill_card() -> None:
    if not config.lookup_field:
        showCritical('No lookup field configured.')
        return

    editor = get_editor()
    if not (editor and editor.note):
        showInfo('Not focusing an editor.')
        fill_card_action.setEnabled(False)
        return

    def fill_meaning() -> None:
        if not (editor and editor.note):
            showCritical('No note to save.')
            fill_card_action.setEnabled(False)
            return

        note = editor.note

        try:
            term = note[config.lookup_field].strip()
        except KeyError:
            showCritical(f'{config.lookup_field} not in note.')
            return
        if not term:
            showInfo(f'{config.lookup_field} is empty.')
            return

        def finish(future: Future) -> None:
            data = future.result()
            if not data:
                showWarning("Lookup failed.")
                return

            jisho.set_note_data(note, data)
            editor.loadNoteKeepingFocus()

            if not editor.addMode:
                note.flush()

        mw.taskman.with_progress(lambda: jisho.fetch_with_retry(term), finish, label="Fetching data...")

    editor.saveNow(fill_meaning)


qt.qconnect(fill_card_action.triggered, fill_card)
