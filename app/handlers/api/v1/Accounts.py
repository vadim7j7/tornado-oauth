from tornado.web import HTTPError

from app.handlers.api import BaseHandler
from app.utils import compact_result
from app.constants import USER_ROLE_CLIENT, USER_ROLE_OWN,\
    ASSIGN_WAITING, ASSIGN_APPROVED
from app.sql_queries.User import find_user_by_id
from app.sql_queries.Account import create_account, create_account_user,\
    find_accounts_by_user_id, find_account_by_id_and_user_id,\
    user_joined_to_account, delete_user_from_account,\
    find_accounts_by_id, update_account


class Accounts(BaseHandler):
    async def get(self):
        async with self.db_pool.acquire() as connection:
            data = await find_accounts_by_user_id(connection,
                                                  self.current_user.id)
            self.render(data=compact_result(data))

    async def post(self, *args, **kwargs):
        if not self.current_user.allow_to_create_account:
            self.render(data={
                'message': "You don't have access to manage accounts"
            })
            raise HTTPError(406)

        action = self.get_argument('action', 'create')
        if action == 'create':
            name = self.get_argument('name', None)
            if not name:
                self.render(data={'message': 'Name cannot be blank'})
                raise HTTPError(400)

            # Create an account and join the current user to the account
            try:
                async with self.db_pool.acquire() as connection:
                    async with connection.transaction():
                        account_id = await create_account(connection, name)
                        if account_id is None:
                            raise Exception

                        result = await create_account_user(
                            connection,
                            account_id,
                            self.current_user.id,
                            USER_ROLE_OWN,
                            ASSIGN_APPROVED
                        )
                        if result is None:
                            raise Exception
            except:
                self.render(data={
                    'message': 'Account was not created, please try later again'
                })
                raise HTTPError(400)

            self.render(data={'message': 'Account was created'})

        elif action == 'assign' or action == 'unassign':
            user_id = int(self.get_argument('user_id', 0))
            account_id = int(self.get_argument('account_id', 0))
            if user_id is 0:
                self.render(data={'message': 'Missing argument user_id'})
                raise HTTPError(404)

            if account_id is 0:
                self.render(data={'message': 'Missing argument account_id'})
                raise HTTPError(404)

            async with self.db_pool.acquire() as connection:
                # Checking and loading the user
                user = await find_user_by_id(connection, user_id)
                if user is None:
                    self.render(data={'message': "User doesn't exists"})
                    raise HTTPError(404)
                elif not user['status']:
                    self.render(data={'message': 'User is inactive'})
                    raise HTTPError(400)

                # Checking the account with current user and loading that
                account = await find_account_by_id_and_user_id(
                    connection, account_id,
                    self.current_user.id)
                if account is None:
                    self.render(data={'message': "Account doesn't exists"})
                    raise HTTPError(404)
                elif not account['status']:
                    self.render(data={'message': 'Account is inactive'})
                    raise HTTPError(400)

                # Checking assigned the user to the account or not
                assigned = await user_joined_to_account(
                    connection, account_id, user_id
                )

                if action == 'unassign':
                    if assigned is None:
                        self.render(data={
                            'message': "User doesn't assigned to this account"
                        })
                        raise HTTPError(404)

                    # Unassign the user from the account
                    try:
                        async with connection.transaction():
                            result = await delete_user_from_account(
                                connection, account_id, user_id
                            )
                            if result is None:
                                raise Exception
                    except:
                        self.render(data={
                            'message': 'User was not unassigned, '
                                       'please try later again'
                        })
                        raise HTTPError(400)
                    self.render(data={'message': 'User was unassigned'})

                elif action == 'assign':
                    if assigned is not None:
                        self.render(data={
                            'message': 'User already assigned to this account'
                        })
                        raise HTTPError(404)

                    # assign the user to the account
                    try:
                        async with connection.transaction():
                            result = await create_account_user(
                                connection,
                                account_id,
                                user_id,
                                USER_ROLE_CLIENT,
                                ASSIGN_APPROVED
                            )
                            if result is None:
                                raise Exception
                    except:
                        self.render(data={
                            'message': 'User was not joined, '
                                       'please try later again'
                        })
                        raise HTTPError(400)

                    self.render(data={'message': 'User was assigned'})
                else:
                    raise HTTPError(405)
        else:
            raise HTTPError(405)

    async def put(self, *args, **kwargs):
        if not self.current_user.allow_to_update_account:
            self.render(data={
                'message': "You don't have access to manage accounts"
            })
            raise HTTPError(406)

        account_id = int(self.get_argument('account_id', 0))
        if account_id is 0:
            self.render(data={'message': 'Missing argument account_id'})
            raise HTTPError(404)

        async with self.db_pool.acquire() as connection:
            account = await find_account_by_id_and_user_id(
                connection, account_id, self.current_user.id
            )
            if account is None:
                self.render(data={'message': "Account doesn't exists"})
                raise HTTPError(404)

            name = self.get_argument('name', account['name'])
            await update_account(connection, account['id'], name)

        self.render(data={'message': 'Account was updated'})


class AccountUser(BaseHandler):
    async def post(self, *args, **kwargs):
        account_id = int(self.get_argument('account_id', 0))

        if account_id is 0:
            self.render(data={'message': 'Missing argument account_id'})
            raise HTTPError(404)

        async with self.db_pool.acquire() as connection:
            # Checking the account with current user and loading that
            account = await find_accounts_by_id(connection, account_id)
            if account is None:
                self.render(data={'message': "Account doesn't exists"})
                raise HTTPError(404)

            elif not account['status']:
                self.render(data={'message': 'Account is inactive'})
                raise HTTPError(400)

            assigned = await user_joined_to_account(
                connection, account_id, self.current_user.id
            )
            if assigned is not None:
                self.render(data={
                    'message': 'Your request was already submitted'
                })
                raise HTTPError(400)

            await create_account_user(
                connection,
                account_id,
                self.current_user.id,
                USER_ROLE_CLIENT,
                ASSIGN_WAITING
            )

            self.render(data={
                'message': 'Your request was successfully '
                           'submitted and waiting to approve'
            })

    async def delete(self, *args, **kwargs):
        account_id = int(self.get_argument('account_id', 0))

        if account_id is 0:
            self.render(data={'message': 'Missing argument account_id'})
            raise HTTPError(404)

        async with self.db_pool.acquire() as connection:
            # Checking the account with current user and loading that
            account = await find_accounts_by_id(connection, account_id)
            if account is None:
                self.render(data={'message': "Account doesn't exists"})
                raise HTTPError(404)

            assigned = await user_joined_to_account(
                connection, account_id, self.current_user.id
            )
            if assigned is None:
                self.render(data={'message': 'You have not sent request yet'})
                raise HTTPError(400)

            await delete_user_from_account(
                connection, account_id, self.current_user.id
            )

            self.render(data={
                'message': 'You have just unjoined from this account'
            })
