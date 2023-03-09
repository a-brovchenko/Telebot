import logging
from pythonjsonlogger import jsonlogger

formatter = jsonlogger.JsonFormatter("%(asctime)s %(threadName)s %(name)s %(levelname)s %(message)s")
file_out = logging.FileHandler('/app/telebot.log')
console_out = logging.StreamHandler()
file_out.setFormatter(formatter)
console_out.setFormatter(formatter)
logging.basicConfig(handlers=(file_out, console_out), level=logging.INFO)