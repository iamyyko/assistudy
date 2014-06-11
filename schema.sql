drop table if exists user;
create table user(
	id integer primary key autoincrement,
	username string not null,
	password string not null
);
