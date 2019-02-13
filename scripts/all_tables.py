"""
A test script (throw it away later) to get all tables from an access database
"""

# Third party modules #
import pyodbc

###############################################################################
db_file = "\\deploy\\cbm_runner\\tests\\tutorial_six\\data\\output\\cbm_formatted_db\\project.mdb"
conn = pyodbc.connect("Driver={Microsoft Access Driver (*.mdb, *.accdb)};User Id='admin';DBQ=" + db_file)

cur = conn.cursor()

table = [x[2] for x in cur.tables() if x[2].startswith('tbl')]

conn.close()