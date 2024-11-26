#!/usr/bin/env bash

cat datasources_and_environments.sql | docker exec -i cerebrom_mysql_1 /usr/bin/mysql -u whatever --password=changeme smarty
