create table accounts
(
  id      serial              not null,
  name    varchar default 250 not null,
  status  boolean   default true,
  created timestamp default CURRENT_TIMESTAMP
);

create unique index accounts_id_uindex
  on accounts (id);
