import logging

class StreamlitLogHandler(logging.Handler):
    def __init__(self, container):
        super().__init__()
        self.container = container
        
    def emit(self, record):
        log_entry = self.format(record)
        self.container.markdown(f"`{log_entry}`")
