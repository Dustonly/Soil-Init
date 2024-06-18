import numpy as np
from itertools import product
import time
import multiprocessing

# from helper import Helper
from soilgrids import Soilgrids
from domain import Domain
from geo import Geo


def plot_box(x_points, y_points, array, lon, lat):
    import matplotlib.pyplot as plt
    # Plot the box edges
    x_points.append(x_points[0])
    y_points.append(y_points[0])

    extent = [lon.min(), lon.max(), lat.min(), lat.max()]

    plt.imshow(array, extent=extent)
    plt.plot(x_points, y_points, color='blue')

    # Add labels and title
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Plotting the edges of a box')

    # Show the plot
    plt.grid(True)
    plt.axis('equal')  # Ensure aspect ratio is equal
    plt.show()
    exit()


def get(rlon, rlat):
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

    # return np.mean(sand)
    return sand


def main():
    domain = Domain()
    soilgrids = Soilgrids()
    geo = Geo(domain)

    domain.read_domain_file()
    domain.get_rlons_rlats()
    print(domain.sg_res)

    soilgrids.initialize(domain.sg_res)

    # print(geo.get_corners(np.min(domain.rlons), np.min(domain.rlats)))
    # print(geo.get_corners(np.max(domain.rlons), np.max(domain.rlats)))
    # loop over all grid boxes
    count = 0
    sumtime = 0
    rlonlatlist = list(product(domain.rlons, domain.rlats))
    # for rlon, rlat in product(domain.rlons, domain.rlats):
    stime = time.time()
    #     stime = time.time()
    #     count += 1
    #     # print(rlon, rlat)
    #     corner_x, corner_y = geo.get_corners(rlon, rlat)
    #     sand, silt, clay, lon, lat = soilgrids.read(corner_x, corner_y)

    #     sumtime += time.time() - stime
    #     # plot_box(corner_x, corner_y, sand, lon, lat)
    #     # print(sand)

    #   print(sumtime, count, sumtime/count)

    # print(rlonlatlist[0])
    rlon = rlonlatlist[0][0]
    rlat = rlonlatlist[0][1]
    corner_x, corner_y = geo.get_corners(rlon, rlat)
    # print(corner_x, corner_y)
    # sand = get(rlonlatlist[0])

    max_processes = 1
# Create a multiprocessing pool
    with multiprocessing.Pool(processes=max_processes) as pool:
        # Map the function to the coordinates using multiple processes

        sand = pool.starmap(get, rlonlatlist)

    sand = np.array(sand)
    print(sand)
    # print(sand.shape)
    print(time.time()-stime)


if __name__ == '__main__':
    main()
