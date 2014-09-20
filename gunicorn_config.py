# Gunicorn configuration file

bind = '0.0.0.0:5000'

daemon = True
pidfile = 'beats.pid'

workers = 1
worker_class = 'gevent'

errorlog = 'error.log'
loglevel = 'info'
accesslog = 'access.log'
