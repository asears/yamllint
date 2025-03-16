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

from yamllint.parser import (
    Comment,
    Line,
    Token,
    line_generator,
    token_or_comment_generator,
    token_or_comment_or_line_generator,
)


def test_line_generator():
    """
    Test line_generator functionality.

    :return: None
    """
    e = list(line_generator(''))
    assert len(e) == 1
    assert e[0].line_no == 1
    assert e[0].start == 0
    assert e[0].end == 0

    e = list(line_generator('\n'))
    assert len(e) == 2

    e = list(line_generator(' \n'))
    assert len(e) == 2
    assert e[0].line_no == 1
    assert e[0].start == 0
    assert e[0].end == 1

    e = list(line_generator('\n\n'))
    assert len(e) == 3

    e = list(line_generator('---\n'
                              'this is line 1\n'
                              'line 2\n'
                              '\n'
                              '3\n'))
    assert len(e) == 6
    assert e[0].line_no == 1
    assert e[0].content == '---'
    assert e[2].content == 'line 2'
    assert e[3].content == ''
    assert e[5].line_no == 6

    e = list(line_generator('test with\n'
                              'no newline\n'
                              'at the end'))
    assert len(e) == 3
    assert e[2].line_no == 3
    assert e[2].content == 'at the end'


def test_token_or_comment_generator():
    """
    Test token_or_comment_generator functionality.

    :return: None
    """
    e = list(token_or_comment_generator(''))
    assert len(e) == 2
    assert e[0].prev is None
    from yaml import Token as YamlToken
    assert isinstance(e[0].curr, YamlToken)
    assert isinstance(e[0].next, YamlToken)
    assert e[1].prev == e[0].curr
    assert e[1].curr == e[0].next
    assert e[1].next is None

    e = list(token_or_comment_generator('---\n'
                                          'k: v\n'))
    assert len(e) == 9
    from yaml import KeyToken, ValueToken
    assert isinstance(e[3].curr, KeyToken)
    assert isinstance(e[5].curr, ValueToken)

    e = list(token_or_comment_generator('# start comment\n'
                                          '- a\n'
                                          '- key: val  # key=val\n'
                                          '# this is\n'
                                          '# a block     \n'
                                          '# comment\n'
                                          '- c\n'
                                          '# end comment\n'))
    assert len(e) == 21
    assert isinstance(e[1], Comment)
    assert e[1] == Comment(1, 1, '# start comment', 0)
    assert e[11] == Comment(3, 13, '# key=val', 0)
    assert e[12] == Comment(4, 1, '# this is', 0)
    assert e[13] == Comment(5, 1, '# a block     ', 0)
    assert e[14] == Comment(6, 1, '# comment', 0)
    assert e[18] == Comment(8, 1, '# end comment', 0)

    e = list(token_or_comment_generator('---\n'
                                          '# no newline char'))
    assert e[2] == Comment(2, 1, '# no newline char', 0)

    e = list(token_or_comment_generator('# just comment'))
    assert e[1] == Comment(1, 1, '# just comment', 0)

    e = list(token_or_comment_generator('\n'
                                          '   # indented comment\n'))
    assert e[1] == Comment(2, 4, '# indented comment', 0)

    e = list(token_or_comment_generator('\n'
                                          '# trailing spaces    \n'))
    assert e[1] == Comment(2, 1, '# trailing spaces    ', 0)

    e = [c for c in
         token_or_comment_generator('# block\n'
                                    '# comment\n'
                                    '- data   # inline comment\n'
                                    '# block\n'
                                    '# comment\n'
                                    '- k: v   # inline comment\n'
                                    '- [ l, ist\n'
                                    ']   # inline comment\n'
                                    '- { m: ap\n'
                                    '}   # inline comment\n'
                                    '# block comment\n'
                                    '- data   # inline comment\n')
         if isinstance(c, Comment)]
    assert len(e) == 10
    assert not e[0].is_inline()
    assert not e[1].is_inline()
    assert e[2].is_inline()
    assert not e[3].is_inline()
    assert not e[4].is_inline()
    assert e[5].is_inline()
    assert e[6].is_inline()
    assert e[7].is_inline()
    assert not e[8].is_inline()
    assert e[9].is_inline()


def test_token_or_comment_or_line_generator():
    """
    Test token_or_comment_or_line_generator functionality.

    :return: None
    """
    e = list(token_or_comment_or_line_generator('---\n'
                                                  'k: v  # k=v\n'))
    assert len(e) == 13
    from yaml import (
        BlockMappingStartToken,
        DocumentStartToken,
        KeyToken,
        StreamStartToken,
        ValueToken,
    )
    assert isinstance(e[0], Token)
    assert isinstance(e[0].curr, StreamStartToken)
    assert isinstance(e[1], Token)
    assert isinstance(e[1].curr, DocumentStartToken)
    assert isinstance(e[2], Line)
    assert isinstance(e[3].curr, BlockMappingStartToken)
    assert isinstance(e[4].curr, KeyToken)
    assert isinstance(e[6].curr, ValueToken)
    assert isinstance(e[8], Comment)
    assert isinstance(e[9], Line)
    assert isinstance(e[12], Line)
