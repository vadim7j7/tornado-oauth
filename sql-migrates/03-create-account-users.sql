create table account_users
(
  account_id integer           not null
    constraint account_users_accounts_id_fk
    references accounts (id)
    on delete cascade,
  user_id    integer           not null
    constraint account_users_users_id_fk
    references users (id)
    on delete cascade,
  role       integer default 0 not null,
  created    timestamp default CURRENT_TIMESTAMP
);
