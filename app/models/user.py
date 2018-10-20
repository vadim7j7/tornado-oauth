from app.constants import USER_ROLE_OWN, USER_ROLE_CLIENT


class User(object):
    def __init__(self, user: dict):
        self.__user = user

    @property
    def id(self) -> dict:
        return self.__user.get('id')

    @property
    def email(self) -> dict:
        return self.__user.get('email')

    @property
    def role(self) -> dict:
        return self.__user.get('role')

    @property
    def own(self) -> bool:
        return self.role == USER_ROLE_OWN

    @property
    def client(self) -> bool:
        return self.role == USER_ROLE_CLIENT

    @property
    def allow_to_create_account(self) -> bool:
        return self.own

    @property
    def allow_to_update_account(self) -> bool:
        return self.own
