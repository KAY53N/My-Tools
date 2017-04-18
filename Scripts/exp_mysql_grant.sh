#!/bin/bash
#Function export user privileges

HOST='127.0.0.1'
USER='root'
PASS='111111'

expgrants()
{
  mysql -B -h${HOST} -u${USER} -p${PASS} -N $@ -e "SELECT CONCAT(
    'SHOW GRANTS FOR ''', user, '''@''', host, ''';'
    ) AS query FROM mysql.user" | \
  mysql -h${HOST} -u${USER} -p${PASS} $@ | \
  sed 's/\(GRANT .*\)/\1;/;s/^\(Grants for .*\)/-- \1 /;/--/{x;p;x;}'
}

expgrants > ./grants.sql