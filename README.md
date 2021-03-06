# Jisho Auto-Fill

An Anki menu item found in `Tools` which will search
[jisho.org](https://jisho.org)
for a lookup term and automatically fill out fields.

Supports batch creation.

Based on 
[https://ankiweb.net/shared/info/1545080191](https://ankiweb.net/shared/info/1545080191).

## Configuration

### hotkey

The app-wide 
[hotkey](https://doc.qt.io/archives/qt-4.8/qkeysequence.html)
to activate auto-fill.

### note

The note type to use for batch creation.

### retry

Options relating to retry policy when API lookup fails,
which can happen when too many requests are made.

### fields

Configuration values are field names.

`lookup` is used as the search term, 
and is commonly set to the same as `word`
so label from jisho.org is used.
It is the only mandatory field configuration value.

All other field names may be left empty,
and they will simply be ignored.

### tags

Tags used to identify error cases.
Leave empty to not tag.

`duplicate` tagging is based on the `word` label.