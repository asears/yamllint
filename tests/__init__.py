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

import locale

# Set the locale to C to ensure consistent output across different systems
# (e.g. for error messages).
# This is necessary because the locale is inherited from the environment
# and can cause tests to fail if the output is different (e.g. due to
# different decimal separators).
# 'C' is a locale that is always available and should be understood by all
# systems.  'C' is for the POSIX locale, which is the same as the 'en_US'
# locale on some systems.
locale.setlocale(locale.LC_ALL, 'C')
