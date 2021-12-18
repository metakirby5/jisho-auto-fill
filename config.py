# -*- coding: utf-8 -*-
"""
Configuration values.
"""
from typing import Any, Dict

from aqt import mw

config: Dict[str, Any] = mw.addonManager.getConfig(__name__)
shortcut: str = config['hotkey']
note: str = config['note']
retry: Dict[str, Any] = config['retry']
retry_times: int = retry['times']
retry_delay_seconds: float = retry['delay_seconds']
fields: Dict[str, str] = config['fields']
lookup_field: str = fields['lookup']
word_field: str = fields['word']
reading_field: str = fields['reading']
meaning_field: str = fields['meaning']
tags: Dict[str, str] = config['tags']
added_tag: str = tags['added']
changed_tag: str = tags['changed']
duplicate_tag: str = tags['duplicate']
missing_tag: str = tags['missing']
