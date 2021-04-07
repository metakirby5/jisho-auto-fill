# -*- coding: utf-8 -*-
"""
Anki collection selectors.
"""

from typing import Optional

from aqt import mw
from aqt.utils import chooseList


def select_deck_id(prompt: str) -> Optional[int]:
    decks = sorted(mw.col.decks.all_names_and_ids(), key=lambda x: x.name)
    if not decks:
        return

    names = [deck.name for deck in decks]
    choice = chooseList(prompt, names)
    return decks[choice].id
