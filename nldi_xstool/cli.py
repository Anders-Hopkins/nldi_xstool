"""Console script for nldi_xstool."""
import sys
import click
import numpy as np
from nldi_xstool.nldi_xstool import getXSAtPoint
import geopandas as gpd
import pandas as pd
import json
from nldi_xstool.splitcatchment import SplitCatchment
from nldi_xstool.flowtrace import Flowtrace

class XSTool:
    def __init__(self):
        self.out_crs = "epsg:4326"

    def setoutCRS(self, out_crs="epsg:4326"):
        self.out_crs = out_crs

    def outCRS(self):
        return self.out_crs

    def __repr__(self):
        return f"XSTool {self.out_crs}"

#class SplitCatchmentTool:
    

pass_xstool = click.make_pass_decorator(XSTool)
pass_splitcatchment = click.make_pass_decorator(XSTool)
pass_flowtrace = click.make_pass_decorator(Flowtrace)


@click.group()
@click.option("--outcrs",
              default="epsg:4326",
              help="Projection CRS to return cross-section geometry: default is epsg:4326")
@click.version_option("0.1")
@click.pass_context
def main(ctx, outcrs):
    '''XSTool is a command line tool to extract topographic cross-sections along NHD stream-segments with user-defined
    topographic resolution from 3dep products'''

    ctx.obj = XSTool()
    ctx.obj.setoutCRS(outcrs)
    return 0

###################### Cross Section Command ######################
@main.command()
@click.option("--file",
              required=True,
              type=click.File('w'),
              help='Output json file')
@click.option("--latlon",
              required=True,
              # nargs=2,
              type=tuple((np.float, np.float)),
              # default=(-103.80119199999999, 40.268403),
              help="format lat lon as floats for example lat lon or -103.8011 40.2684")
@click.option("--numpoints",
             default=100,
             type=int,
             help="number of points in cross-section")
@click.option("--width",
              default=1000.0,
              type=float,
              help="width of cross-section")

@pass_xstool
def XSAtPoint(xstool, latlon, numpoints, width, file):
    lat = latlon[0]
    lon = latlon[1]
    print(f'input={latlon}, lat={lat}, lon={lon}, \
    npts={numpoints}, width={width} and crs={xstool.outCRS()} and \
    file={file} and out_epsg={xstool.outCRS()}')
    # print(tuple(latlon))
    xs = getXSAtPoint(point=tuple((lat, lon)),
                      numpoints=numpoints,
                      width=width,
                      file=file)
    # jsdict = xs.to_crs(xstool.out_crs).to_dict() #.to_crs(xstool.out_crs)
    # # print(type(jsdict))
    # # print(jsdict)
    # json.dump(xs.to_dict(), file)
    return xs
    # df = pd.DataFrame({'elevation':xs.elevation.values,
    #                    'Latitude':xs.coords.y.values,
    #                    'Longitude':xs.coords.x.values})
    # gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))
    # return gdf.to_json()

##################### Splitcatchment Command ######################## 

@main.command()
@click.option("--file",
              required=True,
              type=click.File('w'),
              help='Output json file')
@click.option("--latlon",
             required=True,
             type=tuple((np.float, np.float)),
             help="format lat lon as floats for example lat lon or -103.8011 40.2684")
@click.option("--upstream",
              type=bool,
              default=False)

@pass_xstool
def SplitAtPoint(splitcatchment, latlon, upstream, file):  # splitcatchment, latlon, upstream, file
    print('execute splitcatchment')
    lat = latlon[0] 
    lon = latlon[1]
    result = SplitCatchment(lon, lat, upstream, file=file)
    print(result)
    return result

##################### Flowtrace Command ######################## 

@main.command()
@click.option("--file",
              required=True,
              type=click.File('w'),
              help='Output json file')
@click.option("--latlon",
             required=True,
             type=tuple((np.float, np.float)),
             help="format lat lon as floats for example lat lon or -103.8011 40.2684")
@click.option("--raindroptrace",
              type=bool,
              default=True)
@click.option("--direction",
              type=str,
              default='down')

@pass_xstool
def TraceAtPoint(flowtrace, latlon, raindroptrace, direction, file):  # splitcatchment, latlon, upstream, file
    print('execute flowtrace')
    lat = latlon[0] 
    lon = latlon[1]
    result = Flowtrace(lon, lat, raindroptrace, direction, file=file)
    print(result)
    return result

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

# else:
#     print("Not main")
#     sys.exit(cli())
