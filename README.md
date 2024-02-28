# Soil-Init
Interpolate SoilGrids 2.0 data for Dustonly

## SoilGrids
[SoilGrids](https://soilgrids.org/) is a rich database for raster soil data. Most important for Dustonly is the soil texture, consisting of the sand, silt and clay content of the soil, and the coarse fragments of the soil indicating the volume fraction of soil particles bigger than 2mm.
The data is available in several horizontal resolutions: 5000m, 1000m, and 250m.
It is accessible from the [ISRIC file server](https://files.isric.org/soilgrids/latest/).


## Road Map
#### Core Features

- [ ] read predefined domains
- [ ] read SoilGrids tiff files from the file server
- [ ] interpolate 5000m and 1000m SoilGrids to the model domain
- [ ] NetCDF output


#### Additional features

- [ ] read tiles for 250m SoilGrids
- [ ] land use dependencies
- [ ] doc blocs
- [ ] parallelisation for large domains
