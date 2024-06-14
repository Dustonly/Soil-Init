import sys
from importlib.machinery import SourceFileLoader

from geo import Geo
from helper import Helper


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

        self.rlons = None
        self.rlats = None

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

    def get_rlons_rlats(self):
        self.rlons = [self.startlon + i * self.dx
                      for i in range(self.ie_tot)]
        self.rlats = [self.startlat + i * self.dx
                      for i in range(self.je_tot)]

    def get_edge(self, offset=0):
        # define edge of the domain for the first rough cut out
        rlons = [self.startlon + i * self.dx
                 for i in range(-offset, self.ie_tot+offset)]
        rlats = [self.startlat + i * self.dx
                 for i in range(-offset, self.je_tot+offset)]

        # southers edge
        edgelon = [rlons[i] for i in range(len(rlons))]
        edgelat = [rlats[0]]*len(rlons)

        # northern edge
        edgelon += rlons
        edgelat += [rlats[-1]]*len(rlons)

        # eastern edge
        edgelon += [rlons[0]]*len(rlats)
        edgelat += rlats

        # western edge
        edgelon += [rlons[-1]]*len(rlats)
        edgelat += rlats

        (elongeo, elatgeo) = Geo().rot2geo(edgelon, edgelat,
                                           self.pol_lon, self.pol_lat)

        # xgeomin = np.min(elongeo)
        # xgeomax = np.max(elongeo)
        # ygeomin = np.min(elatgeo)
        # ygeomax = np.max(elatgeo)

        # return xgeomin, xgeomax, ygeomin, ygeomax
        return elongeo, elatgeo
