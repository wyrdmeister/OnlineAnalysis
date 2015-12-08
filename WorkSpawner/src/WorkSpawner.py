#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import threading
import multiprocessing
import Queue
import sighandler


class LoggerStub(object):
    """ A fake logging class. """
    def __init__(self, level, host):
        pass

    def debug(*arg, **kwargs):
        pass

    def info(*arg, **kwargs):
        pass

    def warning(*arg, **kwargs):
        pass

    def error(*arg, **kwargs):
        pass

    DEBUG = 0
    INFO = 0
    WARNING = 0
    ERROR = 0

try:
    from OACommon import Logger
    from OACommon import LoggerServer

except ImportError:
    print "Cannot find the OACommon Logger classes."
    # Replace logger
    Logger = LoggerStub


# Set log level used by the logging module
LOG_LEVEL = Logger.INFO
LOG_HOST = "localhost:9999"
LOG_FILE = "/tmp/workspawner.log"


class WSNoOp(object):

    """ Default WorkSpawner function. """

    def __init__(self):
        """ Constructor. """
        self.logger = Logger("NoOp", LOG_LEVEL, LOG_HOST)

    def process(self, filename):
        """ Default action. """
        self.logger.error("No function configured. File '%s' will be ignored.", filename)


class Worker(multiprocessing.Process):
    """ Worker process
    """

    def __init__(self, job_queue, result_queue=None):
        """ Worker process constructor
        Worker(job_queue, result_queue=None)
        Result queue may be null if the results are not needed.
        """

        # base class initialization
        multiprocessing.Process.__init__(self)

        # job management stuff
        self.job_queue = job_queue
        self.result_queue = result_queue

        # Module management
        self.lastmodule = None
        self.lastfunction = None
        self.coremodule = None
        self.coreclass = None
        self.corefunction = None

        # Setup logging
        self.logger = Logger(self._name, LOG_LEVEL, LOG_HOST)

    def load_module(self, module, function):
        """ General function to load a function from a module. If the function
        is a method of a class, an instance of that class is created and
        returned.
        The returned value is a tuple containing:
            1) The module
            2) The function
            3) The class instance if required
        """
        try:
            # Reset core class
            coreclass = None

            # Import module
            if module != "":
                __import__(module, level=0)

                # Get the submodule, if needed
                coremodule = sys.modules[module]
            else:
                coremodule = sys.modules[__name__]

            # If needed separate class from function
            func_parts = function.split('.')

            # If we have a class we must create an instance
            if len(func_parts) > 1:
                tempclass = coremodule
                for i in range(len(func_parts) - 1):
                    tempclass = getattr(tempclass, func_parts[i])
                coreclass = tempclass()  # Instance

                # Get function
                corefunction = getattr(coreclass, func_parts[-1])

            # If we have a simple function we search for it in coremodule
            else:
                corefunction = getattr(coremodule, func_parts[0])
            return (coremodule, corefunction, coreclass)

        except Exception as e:
            self.logger.error("Processing function failed (Error: %s)", e, exc_info=True)
            return (None, None, None)

    def run(self):
        """ Worker entry point
        Cycle indefinitely waiting for jobs on the job queue. The worker will
        be terminated when it will receive a job tuple with the first element
        set as None.
        """
        while True:
            try:
                # Get a job from the queue
                # A job is a tuple with the following format:
                # (0:job ID, 1:filename, 2:module, 3:function, 4:parameters)
                job = self.job_queue.get(timeout=0.2)

                # When we receive a tuple where the job ID is None we terminate
                # the worker
                if job[0] == None:
                    break

            except Queue.Empty:
                continue

            except Exception as e:
                self.logger.error("Error reading from the job queue (Error: %s)", e)
                break

            if job[2] != self.lastmodule or job[3] != self.lastfunction:
                (self.coremodule, self.corefunction, self.coreclass) = self.load_module(job[2], job[3])
                if self.corefunction == None:
                    self.logger.error("Cannot find processing function '%s'", job[3])
                    if self.result_queue:
                        self.result_queue.put((job[0], False))
                    self.lastmodule = None
                    self.lastfunction = None
                    continue
                else:
                    self.lastmodule = job[2]
                    self.lastfunction = job[3]

            try:
                retval = False
                if job[4] != '':
                    retval = self.corefunction(job[1], job[4])
                else:
                    retval = self.corefunction(job[1])
            except Exception as e:
                self.logger.error("Processing function failed (Error: %s)", e, exc_info=True)
                if self.result_queue:
                    self.result_queue.put((job[0], False))
            else:
                # Store the function result
                if self.result_queue:
                    self.result_queue.put((job[0], retval))

        self.logger.info("Terminating worker.")


class WorkSpawnerServer(threading.Thread):

    # Status constants
    ON = 0
    OFF = 1
    STANDBY = 2
    RUNNING = 3
    ERROR = 4
    WARN = 5
    NONE = 6

    def __init__(self):
        # Parent init
        threading.Thread.__init__(self)
        self.reload = False

        # Job handling stuff
        self.runningflag = True
        self.num_processes = 2  # Parallel
        self.maxjobs = 6

        # Init logging server
        try:
            self.log_server = LoggerServer('WorkSpawner', LOG_LEVEL, LOG_FILE)
        except:
            self.log_server = None

        # Default values when there's only a name
        self.defaultjobmetainfo = ('', 'WSNoOp.process', '')
        self.defaultpostmetainfo = ('', '', '')

        # Job queue from outside
        self.tangoqueue = Queue.Queue()

        # State flag
        self._state = WorkSpawnerServer.STANDBY

        # Setup logging
        self.logger = Logger('WorkSpawnerMaster', LOG_LEVEL, LOG_HOST)

    def start_worker(self, job_queue, result_queue=None):
        """ start_worker(job_queue, result_queue=None)
        Method to create a new worker
        """
        worker = Worker(job_queue, result_queue)
        worker.start()
        return worker

    def getErrorState(self):
        """ Return the error state of the workspawner. """
        if self.log_server is not None:
            log_state = self.log_server.getStatus()
            if log_state == Logger.ERROR:
                return WorkSpawnerServer.ERROR
            elif log_state == Logger.WARN:
                return WorkSpawnerServer.WARN
        return WorkSpawnerServer.NONE

    def getProcessingState(self):
        """ Return the processing state of the workspawner. """
        if self.tangoqueue.empty() and len(self.pending_jobs) == 0 and len(self.pending_post) == 0:
            return WorkSpawnerServer.STANDBY
        else:
            return WorkSpawnerServer.RUNNING

    def multProcessSrv(self):
        """ Main processing function
        """

        # Workers stuff
        job_id = 0
        worker_list = []
        self.job_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.pending_jobs = []

        # Post processing stuff
        post_worker = None
        self.post_jobs = multiprocessing.Queue()
        self.post_results = multiprocessing.Queue()
        self.pending_post = []

        # Start worker processes
        try:
            for i in range(0, self.num_processes):
                worker_list.append(self.start_worker(self.job_queue, self.result_queue))
            if all(self.defaultpostmetainfo[0:2]):
                post_worker = self.start_worker(self.post_jobs, self.post_results)
        except Exception as e:
            self.logger.error("[multProcessSrv] Error starting worker pool (Error: %s)", e)
            return -1

        sighandler.term_interrupt = False
        while self.runningflag and not sighandler.term_interrupt:

            # Check reload signal
            if self.reload:
                # To reload all the workers just send them an empty job
                for i in range(len(worker_list)):
                    self.job_queue.put((None, ))
                if post_worker:
                    self.post_jobs.put((None, ))
                # Reset log server
                if self.log_server is not None:
                    self.log_server.resetError()
                # Reset reload flag
                self.reload = False

            # Fill the job queue
            while len(self.pending_jobs) < self.maxjobs:
                try:
                    jobinfo = self.tangoqueue.get(timeout=0.2)
                except Queue.Empty:
                    break

                except Exception as e:
                    self.logger.error("[multProcessSrv] Exception reading input job queue (Error: %s)", e)
                    # FIXME: this error should be handled better...
                    break

                # Complete job tuple (filename, module, function, parameters)
                if len(jobinfo) == 1:
                    jobinfo = jobinfo + self.defaultjobmetainfo
                elif len(jobinfo) == 2:
                    jobinfo = jobinfo + self.defaultjobmetainfo[1:]
                elif len(jobinfo) == 3:
                    jobinfo = jobinfo + self.defaultjobmetainfo[2:]

                self.logger.debug("[multProcessSrv] Job meta info: %s", jobinfo)

                self.job_queue.put((job_id,) + jobinfo)
                self.pending_jobs.append(job_id)
                job_id += 1

            # Check that all workers are still alive
            for worker in worker_list:
                if not worker.is_alive():
                    try:
                        worker.join()
                        self.logger.info("[multProcessSrv] worker '%s' terminated.", worker.name)
                        worker_list.remove(worker)
                    except Exception as e:
                        self.logger.error("[multProcessSrv] Error joining a dead worker process (Error: %s)", e)

            # If the number of running workers is more that what is configured we
            # kill a suitable number of processes appending a corresponding
            # number of (None, ) jobs. The first processes reading the null
            # job will be killed
            if self.num_processes < len(worker_list):
                self.job_queue.put((None, ))

            # If the number of running workers is less that what is configured
            # we start a suitable number of workers to meet the requirement
            if self.num_processes > len(worker_list):
                try:
                    worker_list.append(self.start_worker(self.job_queue, self.result_queue))
                    self.logger.info("[multProcessSrv] respawned a worker thread.")
                except Exception as e:
                    self.logger.error("[multProcessSrv] Error respawning a worker process (Error: %s)", e)

            # Check if the post-processing worker is needed and if it's
            # running. Terminate it in case is no more configured
            if all(self.defaultpostmetainfo[0:2]):
                if not post_worker:
                    try:
                        post_worker = self.start_worker(self.post_jobs, self.post_results)
                        self.logger.info("[multProcessSrv] started post-processing thread.")
                    except Exception as e:
                        self.logger.error("[multProcessSrv] Error starting post-processing process (Error: %s)", e)

                elif not post_worker.is_alive():
                    try:
                        post_worker.join()
                        post_worker = self.start_worker(self.post_jobs, self.post_results)
                        self.logger.info("[multProcessSrv] respawned post-processing thread.")
                    except Exception as e:
                        self.logger.error("[multProcessSrv] Error respawning post-processing process (Error: %s)", e)

            # Clean up the worker process if for some reason the
            # post-processing got disabled
            elif post_worker:
                self.post_jobs.put((None, ))
                try:
                    post_worker.join(timeout=0.2)
                except:
                    pass
                else:
                    try:
                        while True:
                            self.post_jobs.get()
                    except Queue.Empty:
                        pass
                    self.logger.info("[multProcessSrv] terminated post-processing thread")
                    post_worker = None

            # Collect results from processing workers
            while True:
                try:
                    result = self.result_queue.get(timeout=0.2)
                    self.logger.info("[multProcessSrv] Job with ID '%d' returned", result[0])

                    matches = [i for i, jid in enumerate(self.pending_jobs) if jid == result[0]]
                    if len(matches) == 0:
                        self.logger.error("[multProcessSrv] Got result from unexpected job with ID %d", result[0])
                    elif len(matches) > 1:
                        self.logger.error("[multProcessSrv] Got multiple matches (%d) for job with ID %d", len(matches), result[0])
                    for m in matches:
                        del self.pending_jobs[m]

                    # Pass return value to post-processing
                    if all(self.defaultpostmetainfo[0:2]) and post_worker:
                        # Submit result to post-processing worker
                        if result[1] != False:
                            self.post_jobs.put((result[0], result[1], self.defaultpostmetainfo[0], self.defaultpostmetainfo[1], self.defaultpostmetainfo[2]))
                            self.pending_post.append(result[0])

                except Queue.Empty:
                    break
                except Exception as e:
                    self.logger.error("[multProcessSrv] Got exception while getting results for completed jobs (Error: %s)", e, exc_info=True)

            # Collect result from post-processing worker
            while True:
                try:
                    result = self.post_results.get(timeout=0.1)
                    if result[1] == True:
                        self.logger.info("[multProcessSrv] Post-processing of job with ID '%d' completed successfully", result[0])
                    else:
                        self.logger.info("[multProcessSrv] Post-processing of job with ID '%d' completed with errors", result[0])

                    matches = [i for i, jid in enumerate(self.pending_post) if jid == result[0]]
                    if len(matches) == 0:
                        self.logger.error("[multProcessSrv] Got post-processing result from unexpected job with ID %d", result[0])
                    elif len(matches) > 1:
                        self.logger.error("[multProcessSrv] Got multiple matches (%d) for post-processing of job with ID %d", len(matches), result[0])
                    for m in matches:
                        del self.pending_post[m]

                except Queue.Empty:
                    break
                except Exception as e:
                    self.logger.error("[multProcessSrv] Got exception while getting results for completed post-processing jobs (Error: %s)", e, exc_info=True)

        # Stop all processing workers
        for worker in worker_list:
            self.job_queue.put((None, ))
        for worker in worker_list:
            worker.join()

        # Stop post-processing worker
        if post_worker:
            self.post_jobs.put((None, ))
            post_worker.join()

    def run(self):
        """ WorkSpawner server entry point
        """
        try:
            # Start logging server thread
            if self.log_server is not None:
                self.log_server.start()

            # Start multiprocessing
            self.logger.info("[__init__] Started WS server")
            self.multProcessSrv()

        except Exception as e:
            self.logger.error("[run] Unexpected exception (Error: %s)", e)
            retval = -1
        else:
            retval = 0
        finally:
            # Shutting down logging server
            if self.log_server is not None:
                self.log_server.server.shutdown()
                self.log_server.join()
            return retval


if __name__ == "__main__":

    logger = Logger(name="Main", level=LOG_LEVEL, filename=LOG_FILE)
    logger.info("Starting workspawner in standalone mode.")

    # Build server
    srv = WorkSpawnerServer()
    srv.defaultjobmetainfo = ('OnlineAnalysis.oa_root', 'oa_single.process', '')
    srv.defaultpostmetainfo = ('OnlineAnalysis.oa_root', 'oa_present.update', '')

    # Run server
    srv.start()

    # Wait for the server to setup the worker pool
    time.sleep(1)

    import glob
    files = glob.glob(sys.argv[1])
    logger.info("Submitting %d files for processing...", len(files))

    for f in files:
        srv.tangoqueue.put((f, ))
        time.sleep(0.9)
        if sighandler.term_interrupt:
            break

    srv.join(1000000)

    logger.info("Workspawner ended")