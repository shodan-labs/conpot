# Copyright (C) 2013  Lukas Rist <glaslos@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import sqlite3
import pwd
import os
import platform
import grp


class ShodanLogger(object):

    def __init__(self):
        pass

    def _create_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS events
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                remote TEXT,
                protocol TEXT,
                request TEXT,
                response TEXT
            )""")

    def log(self, event):
        print event

    def log_session(self, session):
        pass

    def select_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM events")
        print cursor.fetchall()
