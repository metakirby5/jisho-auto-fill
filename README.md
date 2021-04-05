# Jisho Auto-Fill

An Anki menu item found in `Tools` which will search
[jisho.org](https://jisho.org)
for a lookup term and automatically fill out fields.

Based on 
[https://ankiweb.net/shared/info/1545080191](https://ankiweb.net/shared/info/1545080191).

## Configuration

### shortcut

The app-wide 
[hotkey](https://doc.qt.io/archives/qt-4.8/qkeysequence.html)
to activate auto-fill.

### fields

Configuration values are field names.

`lookup` is used as the search term, 
and is commonly set to the same as `word`
so label from jisho.org is used.
It is the only mandatory configuration value.

All other field names may be left blank,
and they will simply be ignored.