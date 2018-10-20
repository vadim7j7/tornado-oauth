from tornado.web import HTTPError

from app.handlers import BaseHandler as MainHandler
from app.constants import DATA_TYPE_JSON
from app.sql_queries.User import find_user_by_id
from app.utils.auth import decode_token
from app.models.user import User


class BaseHandler(MainHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

        self.data_type = DATA_TYPE_JSON

    async def checking_access(self):
        authorization = self.request.headers.get("Authorization", None)
        if authorization is None:
            self.render(data={'error': 'Authorization is missing'})
            raise HTTPError(401)

        tmp = authorization.split(' ')
        if not tmp[0] == 'Bearer':
            self.render(data={'error': 'Type token is invalid'})
            raise HTTPError(401)

        data = decode_token(tmp[1])
        if data.get('error') is not None:
            self.render(data=data)
            raise HTTPError(401)

        # Loading the current user
        async with self.db_pool.acquire() as connection:
            user = await find_user_by_id(connection, data['id'])
            if user is None:
                self.render(data={'error': 'User is missing'})
                raise HTTPError(401)

            self.current_user = User(user)

    async def prepare(self):
        await self.checking_access()
