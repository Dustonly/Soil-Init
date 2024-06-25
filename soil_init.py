import numpy as np
import time

# from helper import Helper
from soilgrids import Soilgrids
from domain import Domain
from geo import Geo
from parallel import Parallel
from output import Output


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


def main():
    stime = time.time()
    tot_time = time.time()
    domain = Domain()
    soilgrids = Soilgrids()
    parallel = Parallel()
    # geo = Geo(domain)

    domain.read_domain_file()
    domain.get_rlons_rlats()
    print(domain.sg_res)

    soilgrids.initialize(domain.sg_res)
    print("init: ", time.time()-stime)
    stime = time.time()

    parallel.processing(domain, 10)
    print("parallel processing: ", time.time()-stime)
    stime = time.time()

    interpolated_data = parallel.get_data()

    output = Output(domain, interpolated_data)
    output.write_netcdf()
    print("output: ", time.time()-stime)
    stime = time.time()

    # print(geo.get_corners(np.min(domain.rlons), np.min(domain.rlats)))
    # print(geo.get_corners(np.max(domain.rlons), np.max(domain.rlats)))
    # loop over all grid boxes
    # print(sand.shape)
    print(time.time()-tot_time)


if __name__ == '__main__':
    main()
