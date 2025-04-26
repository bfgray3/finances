create table if not exists finances.classes (
  id smallint not null auto_increment,
  name varchar(255) unique not null,
  is_asset bool not null,
  primary key (id)
);

create table if not exists finances.dates (
  id mediumint not null auto_increment,
  day date unique not null,
  primary key (id),
);

create table if not exists finances.amounts (
  id mediumint not null auto_increment,
  day_id mediumint not null,
  amount decimal(10,2) not null,
  class_id smallint not null,
  primary key (id),
  foreign key (class_id) references classes(id),
  foreign key (day_id) references dates(id),
  unique (day_id, class_id)
);

create table if not exists finances.comments (
  id mediumint not null auto_increment,
  day_id mediumint not null,
  comments varchar(255) not null,
  primary key (id),
  foreign key (day_id) references dates(id),
  unique (day_id)
);
