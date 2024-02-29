import os
import sys
from importlib.machinery import SourceFileLoader


class Helper:
    def check_file(self, filename):
        return os.path.isfile(filename)


class Domain:
    def __init__(self):
        self.name = None
        self.dx = None
        self.pol_lon = None
        self.pol_lat = None
        self.ie_tot = None
        self.je_tot = None
        self.startlat = None
        self.startlon = None
        self.dx_coarse = None
        self.start_date = None
        self.end_date = None
        self.sg_res = None

    def get_dfilename(self):
        # check if a domain file is given as sys argument
        if len(sys.argv) > 1:
            dfilename = sys.argv[1]
            return (dfilename)
        else:
            print('ERROR: no domain file')
            # print('python sourcefraction_pp.py my.domain')
            exit()

    def check_domain_file(self, dfilename=''):
        if not Helper().check_file(dfilename):
            print('ERROR: domain file "'+dfilename+'" not found')
            exit()

    def read_domain_file(self, dfilename=''):
        if not dfilename:
            dfilename = self.get_dfilename()

        self.check_domain_file(dfilename)

        dfile = SourceFileLoader('d', dfilename).load_module()

        self.name = dfile.name
        self.dx = dfile.dx
        self.pol_lon = dfile.pol_lon
        self.pol_lat = dfile.pol_lat
        self.ie_tot = dfile.ie_tot
        self.je_tot = dfile.je_tot
        self.startlat = dfile.startlat
        self.startlon = dfile.startlon
        self.dx_coarse = dfile.dx_coarse
        self.start_date = dfile.start_date
        self.end_date = dfile.end_date
        self.sg_res = dfile.sg_res


def main():
    domain = Domain()
    domain.read_domain_file()
    print(domain)


main()
