# -*- coding: utf-8 -*-
"""
Online Analysis - Offline OA worker process

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

import Queue
import multiprocessing
from OACommon import Logger

# Online analysis
from OACommon.Configuration import Configuration
from OACommon.Analyzer import Analyzer
from OACommon.Presenter import Presenter


class OfflineWorker(multiprocessing.Process):

    """ Offline worker. """

    def __init__(self, configfile, job_queue, result_queue, loglevel=Logger.INFO, loghost="localhost:9999"):
        """ Constructor. """
        # Parent constructor
        multiprocessing.Process.__init__(self)

        # Setup logging
        self.logger = Logger(self._name, loglevel, loghost)

        try:
            # Init OA
            self.config = Configuration(configfile)
            # Create analyzer
            self.analyzer = Analyzer(self.config)
            # Create presenter
            self.presenter = Presenter(self.config)
        except Exception, e:
            self.logger.error("[__init__] Error initializing the OA (Error: %s)", e)

        # Job queue
        self.job_queue = job_queue

        # Result queue
        self.res_queue = result_queue

        # Output
        self.out = {}

    def run(self):
        """ Worker entry point. """
        index = 0
        while(True):
            try:
                # Get a file to process from the queue. If the file is None
                # terminate.
                filename = self.job_queue.get(timeout=0.2)

                # When we receive a filename that is None we terminate
                if filename == None:
                    break

            except Queue.Empty:
                continue

            except Exception as e:
                self.logger.error("Error reading from the job queue (Error: %s)", e)
                self.res_queue.put((-1, "Error reading from the job queue (Error: %s)" % (e, )))
                break

            try:
                index += 1

                # Processing
                data = self.analyzer.analyze(filename)

                # Post-processing
                self.out = self.presenter.update(data)

                # Return name of processed file
                self.res_queue.put((index, filename))
            except Exception, e:
                self.logger.error("Error processing file '%s' (Error: %s)", filename, e)
                self.res_queue.put((-1, "Error processing file '%s' (Error: %s)" % (filename, e)))
                break

        # Exiting worker. Store presenter data into result_queue
        self.res_queue.put((None, self.out))

        self.logger.info("Terminating worker.")