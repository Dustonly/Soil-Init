from itertools import product
import multiprocessing
import numpy as np

from soilgrids import Soilgrids
from domain import Domain
from geo import Geo


class Parallel:
    def __init__(self):
        self.interpolated_data = []

    def processing(self, domain, max_processes):
        rlonlatlist = list(product(domain.rlons, domain.rlats))

        # Create a multiprocessing pool
        with multiprocessing.Pool(processes=max_processes) as pool:
            # Map the function to the coordinates using multiple processes

            results = pool.starmap(self.get, rlonlatlist)

        sand, silt, clay, cfvo = [], [], [], []

        for res in results:
            sand.append(res[0])
            silt.append(res[1])
            clay.append(res[2])
            cfvo.append(res[3])

        sand = np.array(sand).reshape((domain.je_tot, domain.ie_tot))
        silt = np.array(silt).reshape((domain.je_tot, domain.ie_tot))
        clay = np.array(clay).reshape((domain.je_tot, domain.ie_tot))
        cfvo = np.array(cfvo).reshape((domain.je_tot, domain.ie_tot))

        self.interpolated_data.append(sand)
        self.interpolated_data.append(silt)
        self.interpolated_data.append(clay)
        self.interpolated_data.append(cfvo)

    def get(self, rlon, rlat):
        domain = Domain()
        domain.read_domain_file()
        soilgrids = Soilgrids()
        soilgrids.initialize(domain.sg_res)
        geo = Geo(domain)

        # print(rlon, rlat)

        corner_x, corner_y = geo.get_corners(rlon, rlat)
        sand, silt, clay, cfvo, lon, lat = soilgrids.read(corner_x, corner_y)

        polygon_vertices = np.array(list(zip(corner_x, corner_y)))
        mask = geo.mask_with_polygon(lon, lat, polygon_vertices)
        # sand = np.where(mask, sand, np.nan)
        data_mask = sand.mask | mask

        sand = np.ma.array(sand, mask=data_mask)
        silt = np.ma.array(silt, mask=data_mask)
        clay = np.ma.array(clay, mask=data_mask)
        cfvo = np.ma.array(cfvo, mask=data_mask)

        mean_sand, mean_silt, mean_clay = soilgrids.norm_box_mean(
            sand, silt, clay)
        mean_cfvo = soilgrids.box_mean(cfvo)

        return mean_sand, mean_silt, mean_clay, mean_cfvo

    def get_data(self):
        return self.interpolated_data
