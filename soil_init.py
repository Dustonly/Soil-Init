import os
import sys
from importlib.machinery import SourceFileLoader
import requests
from tqdm import tqdm


class Helper:
    def check_file(self, filename):
        return os.path.isfile(filename)

    def make_dir(self, name):
        if not os.path.isdir(name):
            os.makedirs(name)

    def download_file(self, url, local_path):
        response = requests.get(url, stream=True)

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB

        with open(local_path, 'wb') as file, tqdm(
                desc="Downloading",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                miniters=1) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                file.write(data)

        print("File downloaded successfully.\n")


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


class Soilgrids:
    def __init__(self):
        self.sandfile = None
        self.siltfile = None
        self.clayfile = None
        self.cfvofile = None

    def initialize(self, resolution):
        self.check_resolution(resolution)

        Helper().make_dir(f'./soilgrids/{resolution}')

        for var in ['sand', 'silt', 'clay', 'cfvo']:
            filename = f'./soilgrids/{resolution}/{var}_{resolution}.tif'

            if var == 'sand':
                self.sandfile = filename
            if var == 'silt':
                self.siltfile = filename
            if var == 'clay':
                self.clayfile = filename
            if var == 'cfvo':
                self.cfvofile = filename

            if not Helper().check_file(filename):
                self.download_data(var, filename, resolution)

    def check_resolution(self, resolution):
        if resolution == 'coarse':
            pass
        elif resolution == 'medium':
            pass
        elif resolution == 'fine':
            print('sg_res = fine is not defined yet; exit')
            exit()
        else:
            print('sg_res must be coarse, medium or fine; exit')
            exit()

    def make_url(self, var, resolution):
        url = 'https://files.isric.org/soilgrids/latest/'
        if resolution == 'coarse':
            url += f'data_aggregated/5000m/{var}/{var}_0-5cm_mean_5000.tif'
        elif resolution == 'medium':
            url += f'data_aggregated/1000m/{var}/{var}_0-5cm_mean_1000.tif'
        elif resolution == 'fine':
            print('sg_res = fine is not defined yet; exit')
            exit()

        return url
    # https://files.isric.org/soilgrids/latest/data_aggregated/5000m/clay/

    def download_data(self, var, filename, resolution):
        print(f'Downloading {var} from the soilgrids file server')

        url = self.make_url(var, resolution)
        Helper().download_file(url, filename)


def main():
    domain = Domain()
    domain.read_domain_file()
    print(domain.sg_res)

    soilgrids = Soilgrids()
    soilgrids.initialize(domain.sg_res)


main()
