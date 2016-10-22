-- users model

begin;
---------------------------------------------------------------------------

create table users (
    email       varchar primary key,    -- user's email is better for joins than surrogate id 
    id          uuid not null unique,   -- created using uuid5 and the URL namespace with email address
    pwd         varchar not null,
    name        varchar not null,
    registered  timestamptz(0) default current_timestamp,
    verified    timestamptz(0),
    bio         text
);

---------------------------------------------------------------------------
commit;