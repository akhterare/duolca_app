-- DROP TABLE IF EXISTS course;

CREATE TABLE course (
  username TEXT primary key, 
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  vm_name TEXT NOT NULL,
  resource_group TEXT NOT NULL,
  location TEXT NOT NULL
);

