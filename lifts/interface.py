'''
The interface of lifts.
'''
import os


class FileInterface:

    def __init__(self, fid):
        self.in_name = '{}.in'.format(fid)
        self.out_name = '{}.out'.format(fid)
        open(self.in_name, 'w')  # Create the file if not there
        self.fin = open(self.in_name, 'r')
        self.fout = open(self.out_name, 'w')

    def read(self):
        bookmark = self.fin.tell()
        line = self.fin.readline()
        if line == '\n':
            return
        if line:
            return line.strip()
        self.fin.seek(bookmark)

    def write(self, line):
        print(line, file=self.fout, flush=True)

    def claenup(self):
        os.remove(self.in_name)
        os.remove(self.out_name)
