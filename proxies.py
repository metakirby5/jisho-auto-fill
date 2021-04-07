# -*- coding: utf-8 -*-
"""
Proxy classes.
"""

from PyQt5.QtWidgets import QTextEdit


class QMultiLineEdit(QTextEdit):
    def text(self):
        return self.toPlainText()
