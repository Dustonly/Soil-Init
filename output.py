import numpy as np
from netCDF4 import Dataset


class Output:
    def __init__(self, domain, data):
        self.sand = data[0]
        self.silt = data[1]
        self.clay = data[2]
        self.cfvo = data[3]

        self.filename = 'output.nc'
        self.rlon_dim = domain.ie_tot
        self.rlat_dim = domain.je_tot

    def write_netcdf(self):

        self.creat_ncfile()
        self.write_attributes()
        self.write_data()

    def creat_ncfile(self):
        # Create a new NetCDF file
        ncfile = Dataset(self.filename, 'w', format='NETCDF4')

        rlon_dim = self.rlon_dim
        rlat_dim = self.rlat_dim

        # Define dimensions
        ncfile.createDimension('rlon', rlon_dim)
        ncfile.createDimension('rlat', rlat_dim)

        # Define variables
        ncfile.createVariable('lon', np.float32, ('rlat', 'rlon'))
        ncfile.createVariable('lat', np.float32, ('rlat', 'rlon'))
        ncfile.createVariable('rlon', np.float32, ('rlon',))
        ncfile.createVariable('rlat', np.float32, ('rlat',))
        ncfile.createVariable('rotated_pole', 'c')

        ncfile.createVariable('sand', np.float32, ('rlat', 'rlon'))
        ncfile.createVariable('silt', np.float32, ('rlat', 'rlon'))
        ncfile.createVariable('clay', np.float32, ('rlat', 'rlon'))
        ncfile.createVariable('cfvo', np.float32, ('rlat', 'rlon'))

        ncfile.close()

    def write_attributes(self):

        ncfile = Dataset(self.filename, 'a')

        # Assign attributes to variables
        lon = ncfile.variables['lon']
        lat = ncfile.variables['lat']
        rlon = ncfile.variables['rlon']
        rlat = ncfile.variables['rlat']
        rotated_pole = ncfile.variables['rotated_pole']
        sand = ncfile.variables['sand']
        silt = ncfile.variables['silt']
        clay = ncfile.variables['clay']
        cfvo = ncfile.variables['cfvo']

        # Assign attributes
        lon.standard_name = "longitude"
        lon.long_name = "longitude"
        lon.units = "degrees_east"
        lon._CoordinateAxisType = "Lon"

        lat.standard_name = "latitude"
        lat.long_name = "latitude"
        lat.units = "degrees_north"
        lat._CoordinateAxisType = "Lat"

        rlon.standard_name = "projection_x_coordinate"
        rlon.long_name = "rotated longitude"
        rlon.units = "degrees"
        rlon.axis = "X"

        rlat.standard_name = "projection_y_coordinate"
        rlat.long_name = "rotated latitude"
        rlat.units = "degrees"
        rlat.axis = "Y"

        rotated_pole.long_name = "coordinates of the rotated North Pole"
        rotated_pole.grid_mapping_name = "rotated_latitude_longitude"
        rotated_pole.grid_north_pole_latitude = 80.0
        rotated_pole.grid_north_pole_longitude = 165.0

        sand.standard_name = "sand"
        sand.long_name = "sand fraction"
        sand.units = "-"
        sand.grid_mapping = "rotated_pole"
        sand.coordinates = "lat lon"

        silt.standard_name = "silt"
        silt.long_name = "silt fraction"
        silt.units = "-"
        silt.grid_mapping = "rotated_pole"
        silt.coordinates = "lat lon"

        clay.standard_name = "clay"
        clay.long_name = "clay fraction"
        clay.units = "-"
        clay.grid_mapping = "rotated_pole"
        clay.coordinates = "lat lon"

        cfvo.standard_name = "cfvo"
        cfvo.long_name = "cfvo"
        cfvo.units = "-"
        cfvo.grid_mapping = "rotated_pole"
        cfvo.coordinates = "lat lon"

        # Assign global attributes
        ncfile.pollon = 165.0
        ncfile.pollat = 80.0

        # Close the file
        ncfile.close()

    def write_data(self):
        ncfile = Dataset(self.filename, 'a')

        print(self.sand.shape)

        # Write data to variables
        # ncfile.variables['lon'][:, :] = lon_data
        # ncfile.variables['lat'][:, :] = lat_data
        # ncfile.variables['rlon'][:] = rlon_data
        # ncfile.variables['rlat'][:] = rlat_data

        ncfile.variables['sand'][:, :] = self.sand
        ncfile.variables['silt'][:, :] = self.silt
        ncfile.variables['clay'][:, :] = self.clay
        ncfile.variables['cfvo'][:, :] = self.cfvo

        # Close the file
        ncfile.close()
