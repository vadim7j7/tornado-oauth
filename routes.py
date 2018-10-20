routes = [
    (r'/.*', 'app.handlers.Home.Index'),
]

routes_api_v1 = [
    (r'/api/v1', 'app.handlers.api.v1.Home.Index'),
    (r'/api/v1/auth/token', 'app.handlers.api.v1.Auth.Session'),
    (r'/api/v1/auth/registration', 'app.handlers.api.v1.Auth.Registration'),

    (r'/api/v1/accounts', 'app.handlers.api.v1.Accounts.Accounts'),
    (r'/api/v1/account/request', 'app.handlers.api.v1.Accounts.AccountUser'),
]
