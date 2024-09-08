create database foo;
use foo;

create table if not exists classes (
  id smallint not null auto_increment,
  name varchar(255) not null,
  is_asset bool not null,
  primary key (id)
);

create table if not exists amounts (
  id mediumint not null auto_increment,
  day date not null,
  amount decimal(10,2) not null,
  class_id smallint not null,
  primary key (id),
  foreign key (class_id) references classes(id)
);
