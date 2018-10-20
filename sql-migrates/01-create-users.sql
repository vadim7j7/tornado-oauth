create table users
(
  id       serial       not null,
  email    varchar(256) not null,
  password varchar(512) not null,
  role     integer   default 0,
  status   boolean   default true,
  created  timestamp default CURRENT_TIMESTAMP
);

create unique index users_id_uindex
  on users (id);

create unique index users_email_uindex
  on users (email);
