# -*- coding: UTF-8 -*-
import sqlite3
import csv, codecs, cStringIO
from sqlite_read import find_firefox_cookies

# 功能：使用python将Sqlite中的数据直接输出为CVS

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def save_to_csv(csv_filename):
    sqlite_filename = find_firefox_cookies()
    conn = sqlite3.connect(sqlite_filename)
    c = conn.cursor()
    c.execute("SELECT * FROM moz_cookies WHERE baseDomain='webscraping.com';")
    writer = UnicodeWriter(open(csv_filename, 'wb'))
    writer.writerows(c)


if __name__ == '__main__':
    save_to_csv('export_data.csv')
