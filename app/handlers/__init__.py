from asyncpg.pool import Pool
from tornado.web import RequestHandler, HTTPError
from tornado.escape import json_encode
from jinja2.exceptions import TemplateNotFound

from app.constants import DATA_TYPE_HTML


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

        self.current_user = None
        self.data_type = DATA_TYPE_HTML
        self.__data = {}

    def data_received(self, chunk):
        pass

    @property
    def db_pool(self) -> Pool:
        return self.application.db_pool

    @property
    def env(self):
        return self.application.env

    def write_error(self, status_code, **kwargs):
        self.render('errors/%s.html' % status_code, code=status_code)

    def render(self, template_name=None, **kwargs):
        if self.data_type == DATA_TYPE_HTML:
            try:
                template = self.env.get_template(template_name)
            except TemplateNotFound:
                raise HTTPError(404)

            kwargs.update({
                'static_url': self.static_url,
                'xsrf_form_html': self.xsrf_form_html
            })

            self.write(template.render(kwargs))
        else:
            self.add_header('Content-type', 'application/json')
            self.set_status(kwargs.get('status', self.get_status()))
            self.__data = kwargs.get('data', self.__data)
            self.write(json_encode(self.__data))
