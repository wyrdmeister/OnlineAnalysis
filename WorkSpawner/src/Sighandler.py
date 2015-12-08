import signal

term_interrupt = False


# Signal handler
def handler(signum, frame):
    """ handler(): termination signal handler """
    global term_interrupt

    term_interrupt = True

signal.signal(signal.SIGINT, handler)