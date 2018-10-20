import time

from app.handlers.api import BaseHandler

from setting import REFRESH_TOKEN_EXPIRATION_TIME
from app.sql_queries.User import find_user_by_email,\
    find_user_by_id, create_user
from app.utils.auth import compare_password
from app.utils.auth import encode_password,\
    encode_token, decode_token


def get_refresh_token(user_id):
    return encode_token({'id': user_id, 'time': time.time()},
                        REFRESH_TOKEN_EXPIRATION_TIME)


class Session(BaseHandler):
    # Skip to check token
    def prepare(self):
        pass

    # Checking token
    def get(self, *args, **kwargs):
        token = self.get_argument("token", None)
        data = decode_token(token)

        if data.get('error') is not None:
            self.set_status(401)

        self.render(data=data)

    # Update token by refresh token
    async def put(self, *args, **kwargs):
        token = self.get_argument("refresh_token", None)
        data = decode_token(token)

        if data.get('error') is None:
            async with self.db_pool.acquire() as connection:
                user = await find_user_by_id(connection, data['id'])
                if user is not None:
                    data['token'] = encode_token({'id': user['id']})
                    data['refreshToken'] = get_refresh_token(user['id'])
                else:
                    self.set_status(400)
        else:
            self.set_status(400)

        self.render(data=data)

    # Get token by email and password
    async def post(self, *args, **kwargs):
        data = {}
        email = self.get_argument("email", None)
        password = self.get_argument('password', None)

        if email:
            async with self.db_pool.acquire() as connection:
                user = await find_user_by_email(connection, email)
                if user is not None and compare_password(password,
                                                         user['password']):
                    data['token'] = encode_token({'id': user['id']})
                    data['refreshToken'] = get_refresh_token(user['id'])
                else:
                    data['message'] = 'Email or password is invalid'
                    self.set_status(400)
        else:
            data['message'] = 'Email can not be blank'
            self.set_status(400)

        self.render(data=data)


class Registration(BaseHandler):
    # Skip to check token
    def prepare(self):
        pass

    async def post(self, *args, **kwargs):
        data = {}
        email = self.get_argument("email", None)
        password = self.get_argument('password', None)

        if email and password:
            async with self.db_pool.acquire() as connection:
                user = await find_user_by_email(connection, email)
                if user is None:
                    pwd = encode_password(password)
                    try:
                        async with connection.transaction():
                            user_id = await create_user(connection, email, pwd)
                            data['message'] = 'User was created'
                            data['token'] = encode_token({'id': user_id})
                            data['refreshToken'] = get_refresh_token(user_id)
                            if not user_id:
                                raise Exception
                    except:
                        data['message'] = 'User was not created, ' \
                                          'please try later again'
                        self.set_status(400)
                else:
                    data['message'] = 'Email already exists'
                    self.set_status(400)
        else:
            data['message'] = 'Email cannot be blank' if not email else\
                'Password cannot ne blank'
            self.set_status(400)

        self.render(data=data)
