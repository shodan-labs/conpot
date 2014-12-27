#!/usr/bin/env python
# Copyright (C) 2014 Lukas Rist <glaslos@gmail.com>
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

import json
import logging
import uuid
import time

from datetime import datetime

import ConfigParser
from gevent.queue import Empty

from conpot.core.loggers.shodan import ShodanLogger
from conpot.core.loggers.sqlite_log import SQLiteLogger
from conpot.core.loggers.syslog import SysLogger

logger = logging.getLogger(__name__)


class LogWorker(object):
    def __init__(self, config, dom, session_manager, public_ip):
        self.config = config
        self.log_queue = session_manager.log_queue
        self.session_manager = session_manager
        self.sqlite_logger = None
        self.syslog_client = None
        self.public_ip = public_ip
        self.shodan_logger = ShodanLogger()

        if config.getboolean('sqlite', 'enabled'):
            self.sqlite_logger = SQLiteLogger()

        if config.getboolean('syslog', 'enabled'):
            host = config.get('syslog', 'host')
            port = config.getint('syslog', 'port')
            facility = config.get('syslog', 'facility')
            logdevice = config.get('syslog', 'device')
            logsocket = config.get('syslog', 'socket')
            self.syslog_client = SysLogger(host, port, facility, logdevice, logsocket)

        self.enabled = True

    def _json_default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            return None

    def _process_sessions(self):
        sessions = self.session_manager._sessions
        try:
            session_timeout = self.config.get("session", "timeout")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            session_timeout = 5
        for session in sessions:
            if len(session.data) > 0:
                sec_last_event = max(session.data) / 1000
            else:
                sec_last_event = 0
            sec_session_start = time.mktime(session.timestamp.timetuple())
            sec_now = time.mktime(datetime.utcnow().timetuple())
            if (sec_now - (sec_session_start + sec_last_event)) >= session_timeout:
                # TODO: We need to close sockets in this case
                logger.info("Session timed out: {0}".format(session.id))
                session.set_ended()
                sessions.remove(session)

    def start(self):
        self.enabled = True
        while self.enabled:
            try:
                event = self.log_queue.get(timeout=2)
            except Empty:
                self._process_sessions()
            else:
                if self.public_ip:
                    event["public_ip"] = self.public_ip

                # if self.friends_feeder:
                #     self.friends_feeder.log(json.dumps(event, default=self._json_default))

                if self.sqlite_logger:
                    self.sqlite_logger.log(event)

                if self.syslog_client:
                    self.syslog_client.log(event)

                if self.shodan_logger:
                    self.shodan_logger.log(event)

    def stop(self):
        self.enabled = False
