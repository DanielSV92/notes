#!/usr/bin/env bash

cat ~/smarty-fullbackup.sql | docker exec -i cerebrom_mysql_1 /usr/bin/mysql -u whatever --password=changeme smarty
