-- items model

begin;
---------------------------------------------------------------------------

create table items (
    id              uuid primary key,       -- created using uuid5 with user's uuid and the item's created timestamp
    previous_id     uuid                    -- linked list item version history
                        references items(id),
    user_email      varchar not null
                        references users(email)
                        on update cascade,
    created         timestamptz default current_timestamp,
    title           varchar not null,
    bref            varchar,                -- Bible reference
    bversion        varchar,                -- Bible version
    body            text,
    history         jsonb                   -- complete version history: array of objects, keys = id, user_email, created
);

---------------------------------------------------------------------------
commit;