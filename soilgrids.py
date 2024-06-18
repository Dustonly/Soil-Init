import numpy as np
from geotiff import GeoTiff
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

from helper import Helper
from geo import Geo


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
        lon = np.linspace(lon0, lon1, (dim[1])+1)
        lat = np.linspace(lat0, lat1, (dim[0]+1))

        return sand, silt, clay, cfvo, lon, lat
