"""Main module."""
from nldi_xstool.XSGen import XSGen
import requests
import json
import py3dep
from pynhd import NLDI
import xarray as xr
from matplotlib import pyplot as plt
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import os.path as path

class HPoint(Point):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __hash__(self):
       return hash(tuple(self.coords))


def dataframe_to_geodataframe(df):
    geometry = [HPoint(xy) for xy in zip(df.x, df.y)]
    df = df.drop(['x','y'], axis=1)
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    return gdf


def getXSAtPoint(point, numpoints, width, file=None):
    tpoint = f'POINT({point[1]} {point[0]})'
    df = pd.DataFrame({'pointofinterest':['this'],
                        'Lat':[point[0]],
                        'Lon':[point[1]]})
    gpd_pt = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Lon, df.Lat))
    comid = getCIDFromLatLon(point)
    strm_seg = NLDI().getfeature_byid("comid", "3561878", basin=False).to_crs('epsg:3857')
    xs = XSGen(point=gpd_pt, cl_geom=strm_seg, ny=100, width=1000)
    xs_line = xs.get_xs()
    # get topo polygon with buffer to ensure there is enough topography to interpolate xs line
    # With coarsest DEM (30m) 100. m should
    bb = xs_line.total_bounds - ((100., 100., -100., -100.))
    dem = py3dep.get_map("DEM", tuple(bb), resolution=10, geo_crs="EPSG:3857", crs="epsg:3857")
    x,y = xs.get_xs_points()
    dsi = dem.interp(x=('z', x), y=('z', y))
    pdsi = dsi.to_dataframe()

    # gpdsi = gpd.GeoDataFrame(pdsi, gpd.points_from_xy(pdsi.x.values, pdsi.y.values))
    gpdsi = dataframe_to_geodataframe(pdsi)
    gpdsi.set_crs(epsg=3857, inplace=True)
    gpdsi.to_crs(epsg=4326, inplace=True)
    if(file):
        if not isinstance(file, str):
        # with open(file, "w") as f:
            file.write(gpdsi.to_json())
            file.close()
            return 0
        else:
            with open(file, "w") as f:
                f.write(gpdsi.to_json())
                f.close()
        # gpdsi.to_file(file, driver="GeoJSON")
            return 0
    else:
        return gpdsi

def latlonToPoint(lat, lon):
    return Point(lat, lon)

def getCIDFromLatLon(point):
    print(point)
    pt = latlonToPoint(point[1], point[0])
    location = pt.wkt
    location = f'POINT({point[1]} {point[0]})'
    baseURL = 'https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/position?f=json&coords='
    url = baseURL+location
    print(url)
    response = requests.get(url)
    jres = response.json()
    comid = jres['features'][0]['properties']['comid']
    return comid


