from asyncpg.pool import Pool

from app.constants import ASSIGN_WAITING, ASSIGN_APPROVED


async def find_accounts_by_id(connection: Pool, account_id: int) -> dict:
    result = await connection.fetchrow(
        'SELECT * FROM accounts WHERE accounts.id = $1', account_id
    )

    return dict(result) if result is not None else None


async def find_accounts_by_user_id(connection: Pool, user_id: int) -> list:
    sql = '''
    SELECT
      accounts.*,
      au.role,
      au.created AS joined,
      (SELECT COUNT(account_users.account_id) FROM account_users WHERE account_users.status = $1 AND account_users.account_id = accounts.id) AS users_waiting,
      (SELECT COUNT(account_users.account_id) FROM account_users WHERE account_users.status = $2 AND account_users.account_id = accounts.id) AS users_approved
    FROM accounts
    LEFT JOIN account_users au ON accounts.id = au.account_id
    WHERE au.user_id = $3
    ORDER BY accounts.created ASC
    '''

    return await connection.fetch(sql, ASSIGN_WAITING, ASSIGN_APPROVED, user_id)


async def find_account_by_id_and_user_id(connection: Pool, id: int, user_id: int) -> dict:
    sql = '''
    SELECT
      accounts.*,
      au.role,
      au.created AS joined
    FROM accounts
    LEFT JOIN account_users au ON accounts.id = au.account_id
    WHERE au.account_id = $1 AND au.user_id = $2
    ORDER BY accounts.created ASC
    '''

    return await connection.fetchrow(sql, id, user_id)


async def user_joined_to_account(connection: Pool, account_id: int, user_id: int) -> bool:
    sql = 'SELECT TRUE FROM account_users ' \
          'WHERE account_users.account_id = $1 AND account_users.user_id = $2'

    return await connection.fetchrow(sql, account_id, user_id)


async def create_account(connection: Pool, name: str, status: bool = True) -> int:
    sql = 'INSERT INTO accounts (name, status) VALUES ($1, $2) RETURNING id;'

    return await connection.fetchval(sql, name, status)


async def create_account_user(
        connection: Pool,
        account_id: int,
        user_id: int,
        role: int = 0,
        status: int = 0) -> object:
    sql = 'INSERT INTO account_users (account_id, user_id, role, status) ' \
          'VALUES ($1, $2, $3, $4);'

    return await connection.execute(sql, account_id, user_id, role, status)


async def delete_user_from_account(
        connection: Pool, account_id: int, user_id: int
):
    sql = 'DELETE FROM account_users WHERE account_users.account_id = $1 ' \
          'AND account_users.user_id = $2'

    return await connection.execute(sql, account_id, user_id)


async def update_account(connection: Pool, account_id: int, name: str):
    sql = 'UPDATE accounts SET name = $2 WHERE accounts.id = $1'

    return await connection.execute(sql, account_id, name)
