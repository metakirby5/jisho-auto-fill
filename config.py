# -*- coding: utf-8 -*-
"""
Configuration values.
"""

from aqt import mw

config = mw.addonManager.getConfig(__name__)
shortcut = config['hotkey']
note = config['note']
fields = config['fields']
lookup_field = fields['lookup']
word_field = fields['word']
reading_field = fields['reading']
meaning_field = fields['meaning']
tags = config['tags']
added_tag = tags['added']
changed_tag = tags['changed']
duplicate_tag = tags['duplicate']
