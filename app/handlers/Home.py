from app.handlers import BaseHandler


class Index(BaseHandler):
    def get(self, *args, **kwargs):
        self.render('home/index.html')
