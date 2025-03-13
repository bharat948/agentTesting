# logger.py
import datetime

class SimpleLogger:
    def __init__(self, log_file='app.log'):
        self.log_file = log_file

    def _log(self, level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - {level} - {message}\n"
        with open(self.log_file, 'a') as file:
            file.write(log_message)
        print(log_message, end='')

    def info(self, message):
        self._log('INFO', message)

    def warning(self, message):
        self._log('WARNING', message)

    def error(self, message):
        self._log('ERROR', message)