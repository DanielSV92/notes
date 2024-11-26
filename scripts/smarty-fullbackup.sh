#!/usr/bin/env bash

docker exec cerebrom_mysql_1 /usr/bin/mysqldump -u whatever --password=changeme smarty > ~/smarty-fullbackup.sql
