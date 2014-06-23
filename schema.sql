drop table if exists blog;
create table blog(
	id integer primary key autoincrement,
	title string not null,
	username string not null,
	password string not null,
	contents string not null
);
