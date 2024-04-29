import os
import sys
from importlib.machinery import SourceFileLoader
import requests
from tqdm import tqdm
import numpy as np
from itertools import product
from geotiff import GeoTiff
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import time


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


class Geo:
    def __init__(self, domain):
        self.domain = domain

    def rot2geo(self, xin, yin):

        pollon = self.domain.pol_lon
        pollat = self.domain.pol_lat

        xgeo = [i for i in xin]
        ygeo = [i for i in yin]

        pi_r = np.pi/180.

        for i in range(len(xin)):
            ygeo[i] = 1./pi_r * np.arcsin(
                np.sin(pi_r*yin[i])*np.sin(pi_r*pollat) +
                np.cos(pi_r*yin[i])*np.cos(pi_r*xin[i]) *
                np.cos(pi_r*pollat))

            xgeo[i] = 1./pi_r * np.arctan(
                (np.cos(pi_r*yin[i])*np.sin(pi_r*xin[i])) /
                (np.sin(pi_r*pollat)*np.cos(pi_r*yin[i]) *
                 np.cos(pi_r*xin[i])-np.sin(pi_r*yin[i]) *
                 np.cos(pi_r*pollat))) + pollon + 180.

            if xgeo[i] > 180.:
                xgeo[i] -= 360.

        return (xgeo, ygeo)

    def geo2rot(self, xin, yin):

        singlepoint = None

        pollon = self.domain.pol_lon
        pollat = self.domain.pol_lat

        if type(xin) is float or type(xin) is int:
            singlepoint = True
            xin = [xin]
            yin = [yin]

        xrot = [None] * len(xin)
        yrot = [None] * len(yin)

        pi_r = np.pi/180.

        for i in range(len(xin)):

            yrot[i] = 1./pi_r * np.arcsin(
                np.sin(pi_r*yin[i])*np.sin(pi_r*pollat) +
                np.cos(pi_r*yin[i])*np.cos(pi_r*pollat) *
                np.cos(pi_r*(xin[i]-pollon)))

            xrot[i] = 1./pi_r * np.arctan(
                (np.cos(pi_r*yin[i])*np.sin(pi_r*(xin[i]-pollon))) /
                (np.cos(pi_r*yin[i])*np.sin(pi_r*pollat) *
                 np.cos(pi_r*(xin[i]-pollon)) -
                 np.sin(pi_r*yin[i])*np.cos(pi_r*pollat)))

        if singlepoint:
            return xrot[0], yrot[0]
        else:
            return xrot, yrot

    def get_corners(self, rlon, rlat):

        dx = self.domain.dx

        corner_x = [rlon - dx/2,
                    rlon + dx/2,
                    rlon + dx/2,
                    rlon - dx/2]
        corner_y = [rlat - dx/2,
                    rlat - dx/2,
                    rlat + dx/2,
                    rlat + dx/2]

        corner_x, corner_y = self.rot2geo(corner_x, corner_y)

        return corner_x, corner_y


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
            rawfilename = f'./soilgrids/{resolution}/{var}_{resolution}_raw.tif'
            filename = f'./soilgrids/{resolution}/{var}_{resolution}.tif'

            if var == 'sand':
                self.sandfile = filename
            if var == 'silt':
                self.siltfile = filename
            if var == 'clay':
                self.clayfile = filename
            if var == 'cfvo':
                self.cfvofile = filename

            if not Helper().check_file(rawfilename) and not Helper().check_file(filename):
                self.download_data(var, rawfilename, resolution)

            if not Helper().check_file(filename) and Helper().check_file(rawfilename):
                self.convert_to_epsg4326(rawfilename, filename)

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

    def convert_to_epsg4326(self, input_file, output_file):
        """
        Convert a GeoTIFF file to EPSG:4326.

        Args:
            input_file (str): Path to the input GeoTIFF file.
            output_file (str): Path to save the output GeoTIFF file in EPSG:4326.
        """
        print(input_file, output_file)
        # Open the input GeoTIFF file
        with rasterio.open(input_file) as src:
            # Define the target CRS (EPSG:4326)
            dst_crs = 'EPSG:4326'

            # Calculate the transform for reprojection
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)

            # Set the output file options
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            # Create the output GeoTIFF file and perform reprojection
            with rasterio.open(output_file, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)

    def read(self, corner_x, corner_y):
        box = [(np.min(corner_x), np.min(corner_y)),
               (np.max(corner_x), np.max(corner_y))]

        geo_tiff = GeoTiff(self.sandfile)
        sand = geo_tiff.read_box(box, outer_points=2)
        sand = np.ma.masked_where(sand < 0, sand/1000)
        geo_tiff = GeoTiff(self.siltfile)
        silt = geo_tiff.read_box(box, outer_points=2)
        silt = np.ma.masked_where(silt < 0, silt/1000)
        geo_tiff = GeoTiff(self.clayfile)
        clay = geo_tiff.read_box(box, outer_points=2)
        clay = np.ma.masked_where(clay < 0, clay/1000)
        geo_tiff = GeoTiff(self.cfvofile)
        cfvo = geo_tiff.read_box(box, outer_points=2)
        cfvo = np.ma.masked_where(cfvo < 0, cfvo/1000)

        int_box = geo_tiff.get_int_box(box, outer_points=2)

        dim = sand.shape

        i = int_box[0][0]
        j = int_box[0][1]
        lon0, lat0 = geo_tiff.get_wgs_84_coords(i, j)
        i = int_box[1][0]
        j = int_box[1][1]
        lon1, lat1 = geo_tiff.get_wgs_84_coords(i, j)
        lon = np.linspace(lon0, lon1, (dim[1]))
        lat = np.linspace(lat0, lat1, (dim[0]))

        return sand, silt, clay, lon, lat

def main():
    domain = Domain()
    soilgrids = Soilgrids()
    geo = Geo(domain)

    domain.read_domain_file()
    domain.get_rlons_rlats()
    print(domain.sg_res)

    soilgrids.initialize(domain.sg_res)

    # loop over all grid boxes
    count = 0
    sumtime = 0
    for rlon, rlat in product(domain.rlons, domain.rlats):
        stime = time.time()
        count += 1
        # print(rlon, rlat)
        corner_x, corner_y = geo.get_corners(rlon, rlat)
        sand, silt, clay, lon, lat = soilgrids.read(corner_x, corner_y)

        sumtime += time.time() - stime
        # plot_box(corner_x, corner_y, sand, lon, lat)
        # print(sand)

    print(sumtime, count, sumtime/count)


main()
