"""
This tool is to filter source .mbtiles file and make it smaller
for quick tests

Current example is to leave tiles for zoom level 2 only
"""

import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()


class MBTIle:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def filter(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM tiles WHERE zoom_level!=2")
        self.conn.commit()
        self.conn.execute("VACUUM")
        self.conn.close()

    def touch(self):
        cur = self.conn.cursor()
        sql = "SELECT zoom_level, tile_column, tile_row FROM tiles LIMIT 1"
        for row in cur.execute(sql):
            print(row)


mbt = MBTIle(os.getenv("MBTILE_SOURCE"))
mbt.filter()

