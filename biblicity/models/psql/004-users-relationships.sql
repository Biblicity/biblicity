-- users_relationships indicates following, blocking

create table users_relationships (
    user_email      varchar not null
                        references users(email)
                        on update cascade,
    other_email     varchar not null
                        references users(email)
                        on update cascade,
    kind            varchar not null,
    created         timestamptz default current_timestamp,
    primary key (user_email, other_email),
    check (kind in ('following', 'blocking'))
);