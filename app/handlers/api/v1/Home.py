from app.handlers.api import BaseHandler


class Index(BaseHandler):
    def get(self, *args, **kwargs):
        data = {'apiVersion': 1, 'id': self.current_user.id}
        self.render(data=data)
