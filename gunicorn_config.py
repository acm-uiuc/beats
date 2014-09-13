# Gunicorn configuration file

bind = '0.0.0.0:5000'

workers = 1
worker_class = 'gevent'

errorlog = '-'
loglevel = 'info'
accesslog = '-'
