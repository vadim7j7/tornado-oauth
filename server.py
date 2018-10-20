import sys
import logging

import asyncio
import asyncpg
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.log
from tornado.options import define, options
from jinja2 import Environment, FileSystemLoader

from setting import STATIC_PATCH, TEMPLATE_PATH, DB_PSQL_DSN
from routes import routes_api_v1, routes


define('address',
       default='127.0.0.1', help='run on the given address', type=str)
define('port', default=8001, help='run on the given port', type=int)
define('debug', default=True, help='env type', type=bool)
define('access_to_stdout', default=False, help='Log tornado.access to stdout')


logger = logging.getLogger(__name__)


def init_logging(access_to_stdout=False):
    if access_to_stdout:
        access_log = logging.getLogger('tornado.access')
        access_log.propagate = False
        access_log.setLevel(logging.INFO)
        stdout_handler = logging.StreamHandler(sys.stdout)
        access_log.addHandler(stdout_handler)


class Application(tornado.web.Application):
    def __init__(self):
        setting = {
            'static_path': STATIC_PATCH,
            'template_path': TEMPLATE_PATH,
            'debug': options.debug,
            'xsrf_cookies': False
        }

        tornado.web.Application.__init__(
            self, (routes_api_v1 + routes), **setting
        )
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))

        # psql Connect
        loop = asyncio.get_event_loop()
        self.db_pool = loop.run_until_complete(
            asyncpg.create_pool(dsn=DB_PSQL_DSN)
        )


if __name__ == '__main__':
    options.parse_command_line()
    init_logging(options.access_to_stdout)

    logger.info('Run web server (%s:%s)' % (options.address, options.port))

    try:
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port, address=options.address)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger.info('Stop web server')
