# -*- coding: utf-8 -*-
"""
Online Analysis - SQLite benchmarking decorator

Version 1.0

Michele Devetta (c) 2013


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import time
import os
import stat
import sqlite3
import cPickle

_sq_db = None
_prof = None
DB_LOCATION = '/tmp/timings.db'


def sqlite_log(f):
    """ Decorate a function measuring its execution time and storing the
    result into an SQLite database.
    """
    # Start global sqline connection
    global _sq_db
    _sq_db = sqlite3.connect(DB_LOCATION)
    # Chmod db file
    os.chmod(DB_LOCATION, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    c = _sq_db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function TEXT,
            start REAL,
            end REAL
        )
    """)
    _sq_db.commit()

    def wrapper(*arg, **kwargs):
        global _sq_db
        c = _sq_db.cursor()

        t1 = time.time()
        res = f(*arg, **kwargs)
        t2 = time.time()

        c.execute("INSERT INTO logs (function, start, end) VALUES (?,?,?)", (f.func_name, t1, t2))
        _sq_db.commit()
        c.close()

        return res
    return wrapper


def sqlite_profile(f):
    """ Decorate a function profiling its execution and storing the
    results into an SQLite database.
    """
    import cProfile
    # Start global sqline connection
    global _sq_db
    _sq_db = sqlite3.connect(DB_LOCATION)
    os.chmod(DB_LOCATION, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    c = _sq_db.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            function TEXT,
            totaltime REAL,
            stats TEXT
        )
    """)
    _sq_db.commit()
    global _prof
    _prof = cProfile.Profile()

    def wrapper(*arg, **kwargs):
        global _sq_db
        global _prof
        c = _sq_db.cursor()

        res = _prof.runcall(f, *arg, **kwargs)
        _prof.snapshot_stats()

        t = -1.0
        for s in _prof.stats:
            if s[2] == f.func_name:
                t = _prof.stats[s][3]
                break

        c.execute("INSERT INTO profile (function, totaltime, stats) VALUES (?, ?, ?)", (f.func_name, t, cPickle.dumps(_prof.stats)))
        _sq_db.commit()
        c.close()

        return res
    return wrapper


#def call_graph(f):
#    import pycallgraph
#    import random
#
#    def wrapper(*args, **kwargs):
#
#        pycallgraph.start_trace()
#
#        res = f(*args, **kwargs)
#
#        outname = "/tmp/trace_%d.png" % random.randint(1, 1000)
#        pycallgraph.make_dot_graph(outname)
#
#        return res
#    return wrapper