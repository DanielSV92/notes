#!/usr/bin/env bash

cat roles_and_permissions.sql | docker exec -i cerebrom_mysql_1 /usr/bin/mysql -u whatever --password=changeme smarty
