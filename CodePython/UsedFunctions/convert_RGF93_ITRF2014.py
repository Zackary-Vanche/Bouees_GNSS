from pyproj import CRS, Transformer
import numpy as np 

# ITRF2014 -> Bouee La Rochelle 
# EPSG:9000 # Ellipsoidale 2D
# EPSG:7912 Ellipsoidale 3D
# EPSG:7789 Cartesian 3D

crs_ITRF14 = CRS.from_epsg(7912) # Pride PPP 
crs_RGF93 = CRS.from_epsg(9776) # Positionnement RTK

transformer = Transformer.from_crs(crs_from=crs_RGF93, crs_to=crs_ITRF14)

# PATH_ITRF14 = r''
PATH_larochelle_RGF93 = r''

# pos_BOUEE_ITRF14 = np.loadtxt(PATH_ITRF14)
# pos_larochelle_RGF93 = np.loadtxt(PATH_larochelle_RGF93)
pos_larochelle_RGF93 = np.array([[-3.027901, 48.195742, 40.125, 1999.11],
                                 [-3.029394, 48.196635, 40.135, 2013.11]])

pos_larochelle_ITRF14 = transformer.transform(xx=pos_larochelle_RGF93[:, 0], 
                                              yy=pos_larochelle_RGF93[:, 1],
                                              zz=pos_larochelle_RGF93[:, 2],
                                              tt=pos_larochelle_RGF93[:, 3])