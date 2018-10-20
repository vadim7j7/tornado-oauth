from asyncpg.pool import Pool


async def find_user_by_email(connection: Pool, email: str) -> dict:
    result = await connection.fetchrow(
        'SELECT users.* FROM users where users.email = $1;', email
    )

    return dict(result) if result is not None else None


async def find_user_by_id(connection: Pool, user_id: int) -> dict:
    result = await connection.fetchrow(
        'SELECT users.* FROM users where users.id = $1;', user_id
    )

    return dict(result) if result is not None else None


async def create_user(connection: Pool, email: str, password: str) -> str:
    sql = 'INSERT INTO users (email, password) VALUES ($1, $2) RETURNING id;'
    return await connection.fetchval(sql, email, password)
