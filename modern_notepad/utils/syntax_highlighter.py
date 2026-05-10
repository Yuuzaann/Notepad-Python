from __future__ import annotations
from typing import Optional
from PySide6.QtGui import (
    QSyntaxHighlighter,
    QTextCharFormat,
    QColor,
    QFont,
    QTextDocument,
)

try:
    from pygments import lex
    from pygments.lexers import get_lexer_for_filename, TextLexer
    from pygments.token import Token
    from pygments.util import ClassNotFound
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False


def _make_format(color: str, bold: bool, italic: bool) -> QTextCharFormat:
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(color))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


def _build_dark_palette() -> dict:
    if not PYGMENTS_AVAILABLE:
        return {}
    return {
        Token.Keyword: ("#569cd6", False, False),
        Token.Keyword.Constant: ("#569cd6", False, False),
        Token.Keyword.Declaration: ("#569cd6", False, False),
        Token.Keyword.Namespace: ("#c586c0", False, False),
        Token.Keyword.Type: ("#4ec9b0", False, False),
        Token.Name.Builtin: ("#dcdcaa", False, False),
        Token.Name.Function: ("#dcdcaa", False, False),
        Token.Name.Class: ("#4ec9b0", False, True),
        Token.Name.Decorator: ("#dcdcaa", False, False),
        Token.Name.Exception: ("#f44747", False, False),
        Token.String: ("#ce9178", False, False),
        Token.String.Doc: ("#608b4e", False, False),
        Token.Comment: ("#608b4e", False, True),
        Token.Comment.Single: ("#608b4e", False, True),
        Token.Comment.Multiline: ("#608b4e", False, True),
        Token.Number: ("#b5cea8", False, False),
        Token.Number.Integer: ("#b5cea8", False, False),
        Token.Number.Float: ("#b5cea8", False, False),
        Token.Operator: ("#d4d4d4", False, False),
        Token.Punctuation: ("#d4d4d4", False, False),
        Token.Name.Tag: ("#4ec9b0", False, False),
        Token.Name.Attribute: ("#9cdcfe", False, False),
        Token.Literal.String.Single: ("#ce9178", False, False),
        Token.Literal.String.Double: ("#ce9178", False, False),
        Token.Literal.Number: ("#b5cea8", False, False),
    }


def _build_light_palette() -> dict:
    if not PYGMENTS_AVAILABLE:
        return {}
    return {
        Token.Keyword: ("#0000ff", True, False),
        Token.Keyword.Declaration: ("#0000ff", True, False),
        Token.Keyword.Namespace: ("#af00db", False, False),
        Token.Keyword.Type: ("#267f99", False, False),
        Token.Name.Builtin: ("#795e26", False, False),
        Token.Name.Function: ("#795e26", False, False),
        Token.Name.Class: ("#267f99", False, True),
        Token.Name.Decorator: ("#795e26", False, False),
        Token.String: ("#a31515", False, False),
        Token.Comment: ("#008000", False, True),
        Token.Number: ("#098658", False, False),
        Token.Operator: ("#000000", False, False),
        Token.Name.Tag: ("#800000", False, False),
        Token.Name.Attribute: ("#ff0000", False, False),
    }


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document: QTextDocument, filename: str = "", theme: str = "Dark"):
        super().__init__(document)
        self._filename = filename
        self._theme = theme
        self._lexer = None
        self._formats: dict = {}
        if PYGMENTS_AVAILABLE:
            self._set_lexer(filename)
            self._build_formats()

    def set_filename(self, filename: str) -> None:
        self._filename = filename
        if PYGMENTS_AVAILABLE:
            self._set_lexer(filename)
            self.rehighlight()

    def set_theme(self, theme: str) -> None:
        self._theme = theme
        if PYGMENTS_AVAILABLE:
            self._build_formats()
            self.rehighlight()

    def _set_lexer(self, filename: str) -> None:
        if not filename:
            self._lexer = TextLexer()
            return
        try:
            self._lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            self._lexer = TextLexer()

    def _build_formats(self) -> None:
        palette = (
            _build_dark_palette()
            if self._theme.lower() in ("dark", "dracula", "midnight")
            else _build_light_palette()
        )
        self._formats = {}
        for token_type, (color, bold, italic) in palette.items():
            self._formats[token_type] = _make_format(color, bold, italic)

    def _get_format(self, token_type) -> Optional[QTextCharFormat]:
        while token_type:
            if token_type in self._formats:
                return self._formats[token_type]
            token_type = token_type.parent
        return None

    def highlightBlock(self, text: str) -> None:
        if not PYGMENTS_AVAILABLE or not self._lexer:
            return
        if isinstance(self._lexer, TextLexer):
            return

        block = self.currentBlock()
        block_start = block.position()
        full_text = block.document().toPlainText()
        block_text = full_text[block_start: block_start + len(text)]

        try:
            tokens = list(lex(block_text + "\n", self._lexer))
        except Exception:
            return

        pos = 0
        for token_type, value in tokens:
            length = len(value.rstrip("\n")) if value.endswith("\n") else len(value)
            fmt = self._get_format(token_type)
            if fmt and length > 0:
                self.setFormat(pos, length, fmt)
            pos += len(value)
            if pos > len(text):
                break
