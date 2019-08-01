Ports JSON generator
====================

```plain
$ doas pkg_add python%3 sqlports
$ git clone https://github.com/juanfra684/ports-json.git
$ cd ports-json
$ ./ports-json.py -h
usage: ports-json.py [-h] [-l | -o OUTPUT] database

positional arguments:
  database              sqlports database file

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            list columns, useful to detect new entries in the DB
  -o OUTPUT, --output OUTPUT
                        json file where the results will be written
$ ./ports-json.py -o packages.json /usr/local/share/sqlports

```
