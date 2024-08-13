-- create users table
create table users (
    chat_id integer not null default (0),
    user_id integer not null default (0),
	user_name text not null default (''),
	first_name text not null default (''),
	last_name text not null default (''),
    primary key (chat_id, user_id)
);

-- create messages table
create table messages (
    chat_id integer not null default 0,
    user_id integer not null default 0,
    msg_id integer not null default 0,
    msg_text text not null default '',
    msg_dt timestamp not null default current_timestamp,
    reply_to_msg_id integer,
    primary key (chat_id, msg_id),
    constraint messages_fk foreign key (chat_id, user_id) references users(chat_id, user_id)
);

-- create indexes for messages table
create index messages_chat_id_idx on messages (chat_id);
create index messages_comp_idx2 on messages (chat_id, user_id);
create index messages_comp_idx3 on messages (chat_id, msg_dt);

-- create reactions table
create table reactions (
    id integer primary key autoincrement,
    chat_id integer not null default 0,
    user_id integer not null default 0,
    msg_id integer not null default 0,
    emoticon text not null default '',
    constraint reactions_fk1 foreign key (chat_id, msg_id) references messages(chat_id, msg_id)
    constraint reactions_fk2 foreign key (chat_id, user_id) references users(chat_id, user_id)
);

-- create index for reactions table
create index reactions_comp_idx on reactions (chat_id, msg_id);
