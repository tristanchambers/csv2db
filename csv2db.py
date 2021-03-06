# Use Python3
# Copyright 2017 Tristan Chambers
# https://github.com/tristanchambers/csv2db
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import csv
import re
import argparse

# Command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("INPUTFILE", help="Path to CSV file")
parser.add_argument("TABLENAME", help="Name of table to create")
args = parser.parse_args()

csv_filename = args.INPUTFILE
table_name = args.TABLENAME

def makealphanum(string):
    return(re.sub(r'\W+', '_', string).lower())

def quantize(number):
    if number < 16:
        return 16
    if number < 32:
        return 32
    if number < 64:
        return 64
    if number < 128:
        return 128
    if number < 256:
        return 256
    if number < 512:
        return 512
    if number < 1024:
        return 1024
    if number < 2048:
        return 2048
    if number < 4096:
        return 4096

    return number

max_lengths = {}
types = {}
with open(csv_filename) as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:

        # Get longest length of field contents
        for field in reader.fieldnames:
            try:
                last_max_length = max_lengths[field]
            except KeyError: # first time
                max_lengths[field] = len(row[field])
                continue
            current_length = len(row[field])
            if last_max_length < current_length:
                max_lengths[field] = len(row[field])

        # Test what kind of data type is in each field
        # int
        # float
        # date - skipping this for now
        # string
        for field in reader.fieldnames:
            try:
                int(row[field])
            except ValueError:
                try:
                    float(row[field])
                except ValueError:
                    types[field] = 'character varying'
                else:
                    types[field] = 'decimal'
            else:
                types[field] = 'integer'

# make safe field names
safe_names = {}
for field in reader.fieldnames:
    safe_names[field] = makealphanum(field)

# Start the create statement
command_create_table = "CREATE TABLE %s (\n" % table_name

# Generate schema lines, one for each field
for fieldname in reader.fieldnames[:-1]:
    if types[fieldname] == 'character varying':
        command_create_table = command_create_table + "\t%s character varying(%s),\n" % (makealphanum(fieldname), quantize(max_lengths[fieldname]))
    else:
        command_create_table = command_create_table + "\t%s %s,\n" % (makealphanum(fieldname), types[fieldname])
if types[reader.fieldnames[-1]] == 'character varying':
    command_create_table = command_create_table + "\t%s character varying(%s)\n" % (makealphanum(reader.fieldnames[-1]), quantize(max_lengths[reader.fieldnames[-1]]))
else:
    command_create_table = command_create_table + "\t%s %s\n" % (makealphanum(reader.fieldnames[-1]), types[reader.fieldnames[-1]])

# Close the create statement
command_create_table = command_create_table + ");"

# Generate list of field names, in the same order!
fieldnames_safe = []
for fieldname in reader.fieldnames:
    fieldnames_safe.append(makealphanum(fieldname))

print(command_create_table)

print("COPY %s(%s)" % (table_name, ','.join(fieldnames_safe)))
print("FROM '%s' DELIMITER ',' CSV HEADER;" % os.path.abspath(csv_filename))
