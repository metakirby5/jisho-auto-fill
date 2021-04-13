# -*- coding: utf-8 -*-
"""
Anki collection selectors.
"""

from typing import Optional

from anki.notes import Note
from aqt import mw
from aqt.utils import chooseList


def try_add_tag(note: Note, tag: str) -> bool:
    if not tag:
        return False

    note.addTag(tag)
    return True


def select_deck_id(prompt: str) -> Optional[int]:
    decks = sorted(mw.col.decks.all_names_and_ids(), key=lambda x: x.name)
    if not decks:
        return

    names = [deck.name for deck in decks]
    choice = chooseList(prompt, names)
    return decks[choice].id
