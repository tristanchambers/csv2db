# csv2db
Automatically convert csv files into a database (written for PostgreSQL)

## How to use
example:

``` bash
$ createdb mydatabase
$ python3 csv2db.py mydata.csv mytable | psql mydatabase
```

The above commands would create a table called `mytable` in a new database called `mydatabase`, then import the contents of mydata.csv into the table. The schema of the table is _automagically_ generated based on the content in the columns of the input data.

To see the result:
``` bash
$ psql mydatabase
mydatabase=# select * from mytable;
```

## Limitations
Dates aren't implemented yet. Workaround: You can output the code to your terminal, cut and paste into a text editor, and edit the schema as needed.
