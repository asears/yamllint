# Copyright (C) 2016 Adrien Vergé
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections.abc import Iterator
from typing import Any

import yaml


class Line:
    def __init__(self, line_no: int, buffer: str, start: int, end: int) -> None:
        """
        Initialize a Line.

        :param line_no: The line number.
        :param buffer: The complete text buffer.
        :param start: The starting index of the line.
        :param end: The ending index of the line.
        """
        self.line_no = line_no
        self.start = start
        self.end = end
        self.buffer = buffer

    @property
    def content(self) -> str:
        """
        Get the content of the line.

        :return: The substring representing the line content.
        """
        return self.buffer[self.start : self.end]


class Token:
    def __init__(self, line_no: int, curr: yaml.Token, prev: yaml.Token | None = None,
                 next: yaml.Token | None = None, nextnext: yaml.Token | None = None) -> None:
        """
        Initialize a Token.

        :param line_no: The line number of the token.
        :param curr: The current token.
        :param prev: The previous token.
        :param next: The next token.
        :param nextnext: The token following the next token.
        """
        self.line_no = line_no
        self.curr = curr
        self.prev = prev
        self.next = next
        self.nextnext = nextnext


class Comment:
    def __init__(
        self,
        line_no: int,
        column_no: int,
        buffer: str,
        pointer: int,
        token_before: yaml.Token | None = None,
        token_after: yaml.Token | None = None,
        comment_before: Any | None = None,
    ) -> None:
        """
        Initialize a Comment.

        :param line_no: The line number where the comment appears.
        :param column_no: The column number where the comment starts.
        :param buffer: The full text buffer.
        :param pointer: The position in the buffer where the comment starts.
        :param token_before: The token immediately before the comment.
        :param token_after: The token immediately after the comment.
        :param comment_before: The preceding comment, if any.
        """
        self.line_no = line_no
        self.column_no = column_no
        self.buffer = buffer
        self.pointer = pointer
        self.token_before = token_before
        self.token_after = token_after
        self.comment_before = comment_before

    def __str__(self) -> str:
        """
        Return the string representation of the comment.

        :return: The comment as a string.
        """
        end = self.buffer.find('\n', self.pointer)
        if end == -1:
            end = self.buffer.find('\0', self.pointer)
        if end != -1:
            return self.buffer[self.pointer : end]
        return self.buffer[self.pointer :]

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Comment instance.

        :param other: The object to compare.
        :return: True if equal, False otherwise.
        """
        return (
            isinstance(other, Comment)
            and self.line_no == other.line_no
            and self.column_no == other.column_no
            and str(self) == str(other)
        )

    def is_inline(self) -> bool:
        """
        Determine if the comment is inline (associated with a token).

        :return: True if inline, False otherwise.
        """
        return (
            not isinstance(self.token_before, yaml.StreamStartToken)
            and self.line_no == self.token_before.end_mark.line + 1
            and
            # sometimes token end marks are on the next line
            self.buffer[self.token_before.end_mark.pointer - 1] != '\n'
        )


def line_generator(buffer: str) -> Iterator[Line]:
    """
    Yield a Line instance for each line in the buffer.

    :param buffer: The complete text buffer.
    :yield: A Line representing each line.
    """
    line_no = 1
    cur_line = 0
    next_line = buffer.find('\n')
    while next_line != -1:
        if next_line > 0 and buffer[next_line - 1] == '\r':
            yield Line(line_no, buffer, start=cur_line, end=next_line - 1)
        else:
            yield Line(line_no, buffer, start=cur_line, end=next_line)
        cur_line = next_line + 1
        next_line = buffer.find('\n', cur_line)
        line_no += 1

    yield Line(line_no, buffer, start=cur_line, end=len(buffer))


def comments_between_tokens(token1: yaml.Token, token2: yaml.Token | None) -> Iterator[Comment]:
    """
    Yield comments found between two tokens.

    :param token1: The first token.
    :param token2: The second token; if None, process to the end of buffer.
    :yield: Comments found between token1 and token2.
    """
    if token2 is None:
        buf = token1.end_mark.buffer[token1.end_mark.pointer :]
    elif (
        token1.end_mark.line == token2.start_mark.line
        and not isinstance(token1, yaml.StreamStartToken)
        and not isinstance(token2, yaml.StreamEndToken)
    ):
        return
    else:
        buf = token1.end_mark.buffer[
            token1.end_mark.pointer : token2.start_mark.pointer
        ]

    line_no = token1.end_mark.line + 1
    column_no = token1.end_mark.column + 1
    pointer = token1.end_mark.pointer

    comment_before = None
    for line in buf.split('\n'):
        pos = line.find('#')
        if pos != -1:
            comment = Comment(
                line_no,
                column_no + pos,
                token1.end_mark.buffer,
                pointer + pos,
                token1,
                token2,
                comment_before,
            )
            yield comment

            comment_before = comment

        pointer += len(line) + 1
        line_no += 1
        column_no = 1


def token_or_comment_generator(buffer: str) -> Iterator[Token | Comment]:
    """
    Yield tokens and their associated comments from the buffer.

    :param buffer: The text buffer.
    :yield: Token or Comment instances.
    """
    yaml_loader = yaml.BaseLoader(buffer)

    try:
        prev_token = None
        curr_token = yaml_loader.get_token()
        while curr_token is not None:
            next_token = yaml_loader.get_token()
            nextnext_token = (
                yaml_loader.peek_token() if yaml_loader.check_token() else None
            )

            yield Token(
                curr_token.start_mark.line + 1,
                curr_token,
                prev_token,
                next_token,
                nextnext_token,
            )

            yield from comments_between_tokens(curr_token, next_token)

            prev_token = curr_token
            curr_token = next_token

    except yaml.scanner.ScannerError:
        pass


def token_or_comment_or_line_generator(buffer: str) -> Iterator[Token | Comment | Line]:
    """
    Yield tokens, comments, and lines ordered by their line numbers.

    :param buffer: The text buffer.
    :yield: A Token, Comment, or Line instance.
    """
    tok_or_com_gen = token_or_comment_generator(buffer)
    line_gen = line_generator(buffer)

    tok_or_com = next(tok_or_com_gen, None)
    line = next(line_gen, None)

    while tok_or_com is not None or line is not None:
        if tok_or_com is None or (
            line is not None and tok_or_com.line_no > line.line_no
        ):
            yield line
            line = next(line_gen, None)
        else:
            yield tok_or_com
            tok_or_com = next(tok_or_com_gen, None)
