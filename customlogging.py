import logging
import logging.handlers

import notifications


class BufferingEmailHandler(logging.handlers.BufferingHandler):
    def __init__(self, subject, flushLevel=logging.ERROR):
        super(BufferingEmailHandler, self).__init__(capacity=0)
        self.flushLevel = logging.getLevelName(flushLevel)
        self.tripped = False
        self.subject = subject

    def shouldFlush(self, record):
        # only flush on close()
        return False

    def handle(self, record):
        if record.levelno >= self.flushLevel:
            self.tripped = True
        super(BufferingEmailHandler, self).handle(record)

    def flush(self):
        self.acquire()
        try:
            if not self.buffer:
                return
            if not self.tripped:
                self.buffer = []
                return
            msg = {
                "title": self.subject,
                "body": "\n".join(self.format(record)
                                  for record in self.buffer),
            }
            notifications.send_email(msg)
            self.buffer = []
        finally:
            self.release()
