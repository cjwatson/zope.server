##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for zope.server.serverchannelbase zombie logic
"""
import doctest
import unittest


class FakeSocket:
    data        = ''
    setblocking = lambda *_: None
    close = lambda *_: None

    def __init__(self, no):
        self.no = no

    def fileno(self):
        return self.no

    def getpeername(self):
        return ('localhost', self.no)

    def send(self, data):
        self.data += data
        return len(data)


def zombies_test():
    """Regression test for ServerChannelBase kill_zombies method

    Bug: This method checks for channels that have been "inactive" for a
    configured time. The bug was that last_activity is set at creation time but
    never updated during async channel activity (reads and writes), so any
    channel older than the configured timeout will be closed when a new channel
    is created, regardless of activity.

    >>> import time
    >>> import zope.server.adjustments
    >>> config = zope.server.adjustments.Adjustments()

    >>> from zope.server.serverbase import ServerBase
    >>> class ServerBaseForTest(ServerBase):
    ...     def bind(self, (ip, port)):
    ...         print "Listening on %s:%d" % (ip or '*', port)
    >>> sb = ServerBaseForTest('127.0.0.1', 80, start=False, verbose=True)
    Listening on 127.0.0.1:80

    First we confirm the correct behavior, where a channel with no activity
    for the timeout duration gets closed.

    >>> from zope.server.serverchannelbase import ServerChannelBase
    >>> socket = FakeSocket(42)
    >>> channel = ServerChannelBase(sb, socket, ('localhost', 42))

    >>> channel.connected
    True

    >>> channel.last_activity -= int(config.channel_timeout)

    >>> channel.next_channel_cleanup[0] = channel.creation_time - int(
    ...     config.cleanup_interval)

    >>> socket2 = FakeSocket(7)
    >>> channel2 = ServerChannelBase(sb, socket2, ('localhost', 7))

    >>> channel.connected
    False

    Now we make sure that if there is activity the channel doesn't get closed
    incorrectly.

    >>> channel2.connected
    True

    >>> channel2.last_activity -= int(config.channel_timeout)

    >>> channel2.handle_write()

    >>> channel2.next_channel_cleanup[0] = channel2.creation_time - int(
    ...     config.cleanup_interval)

    >>> socket3 = FakeSocket(3)
    >>> channel3 = ServerChannelBase(sb, socket3, ('localhost', 3))

    >>> channel2.connected
    True

"""

def test_suite():
    return doctest.DocTestSuite()


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
