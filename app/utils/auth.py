import bcrypt
import time
import jwt

from setting import TOKEN_EXPIRATION_TIME, TOKEN_SECRET, TOKEN_ALGORITHM


def encode_token(payload, exp=TOKEN_EXPIRATION_TIME):
    payload['exp'] = int(time.time() + int(exp))

    return jwt.encode(payload, TOKEN_SECRET,
                      algorithm=TOKEN_ALGORITHM).decode("utf-8")


def decode_token(token):
    try:
        result = jwt.decode(token, TOKEN_SECRET, algorithms=[TOKEN_ALGORITHM])
    except (jwt.exceptions.DecodeError,
            jwt.exceptions.ExpiredSignatureError,
            jwt.exceptions.InvalidSignatureError) as error:
        result = {'error': str(error)}

    return result


def encode_password(pwd):
    return bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def compare_password(pwd, enc_pwd):
    enc_pwd = enc_pwd.encode("utf-8")

    return bcrypt.hashpw(pwd.encode("utf-8"), enc_pwd) == enc_pwd
