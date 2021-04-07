from nldi_xstool.utils import geom_to_geojson, get_local_catchment, get_local_flowlines, get_coordsys, project_point
from nldi_xstool.utils import get_flowgrid, get_onFlowline, get_raindropPath, get_intersectionPoint, get_reachMeasure, split_flowline, merge_downstreamPath
import json


class Flowtrace:
    """Define inputs and outputs for the main Flowtrace class"""

    def __init__(self, x=None, y=None, raindropTrace=bool, direction=str, file=None):

        self.x = x
        self.y = y
        self.raindropTrace = raindropTrace
        self.direction = direction
        self.catchmentIdentifier = None
        self.flowlines = None
        self.flw = None
        self.flwdir_transform = None
        self.projected_xy = None
        self.onFlowline = bool
        self.output = None
        self.outfile = file

        #geoms
        self.catchmentGeom = None
        self.splitCatchmentGeom = None
        self.upstreamBasinGeom = None
        self.mergedCatchmentGeom = None 
        self.intersectionPointGeom = None
        self.raindropPathGeom = None   
        self.nhdFlowlineGeom = None
        self.upstreamFlowlineGeom = None
        self.downstreamFlowlineGeom = None
        self.downstreamPathGeom = None

        #outputs
        self.catchment = None
        self.splitCatchment = None
        self.upstreamBasin = None
        self.mergedCatchment = None
        self.intersectionPoint = None
        self.raindropPath = None
        self.nhdFlowline = None
        self.streamInfo = None
        self.upstreamFlowline = None
        self.downstreamFlowline = None
        self.downstreamPath = None

        #create transform
        self.transformToRaster = None  
        self.transformToWGS84 = None 

        #kick off
        self.run()

    # def serialize(self):
    #     # return {
    #     #     'catchment': self.catchment,
    #     #     'intersectionPoint': self.intersectionPoint,
    #     #     'raindropPath': self.raindropPath,
    #     #     'nhdFlowline': self.nhdFlowline,
    #     #     'streamInfo': self.streamInfo, 
    #     #     'upstreamFlowline': self.upstreamFlowline, 
    #     #     'downstreamFlowline': self.downstreamFlowline,
    #     #     'downstreamPath': self.downstreamPath
    #     # }
    #     if self.onFlowline == True:
    #         if self.direction == 'up':
    #             return {
    #                 'streamInfo': self.streamInfo,
    #                 'upstreamFlowline': self.upstreamFlowline
    #             }
    #         if self.direction == 'down':
    #             return {                    
    #                 'streamInfo': self.streamInfo, 
    #                 'downstreamFlowline': self.downstreamFlowline
    #             }
    #         if self.direction == 'none':
    #             return {
    #                 'nhdFlowline': self.nhdFlowline,
    #                 'streamInfo': self.streamInfo
    #             }
        
        # if self.onFlowline == False:
        #     if self.direction == 'up' and self.raindropTrace == True:
        #         return {
        #             'raindropPath': self.raindropPath,
        #             'streamInfo': self.streamInfo, 
        #             'upstreamFlowline': self.upstreamFlowline
        #         }
            # if self.direction == 'down' and self.raindropTrace == True:
            #     return {
            #         'streamInfo': self.streamInfo,  
            #         'downstreamPath': self.downstreamPath
            #     }
            # if self.direction == 'none' and self.raindropTrace == True:
            #     return {
            #         'raindropPath': self.raindropPath,
            #         'nhdFlowline': self.nhdFlowline,
            #         'streamInfo': self.streamInfo
            #     }
            # if self.direction == 'up' and self.raindropTrace == False:
            #     return {
            #         'streamInfo': self.streamInfo, 
            #         'upstreamFlowline': self.upstreamFlowline
            #     }
            # if self.direction == 'down' and self.raindropTrace == False:
            #     return {
            #         'streamInfo': self.streamInfo,  
            #         'downstreamFlowline': self.downstreamFlowline
            #     }
            # if self.direction == 'none' and self.raindropTrace == False:
            #     return {
            #         'nhdFlowline': self.nhdFlowline,
            #         'streamInfo': self.streamInfo
            #     }
                

## main functions
    def run(self):
        # Order of these functions is important!
        self.catchmentIdentifier, self.catchmentGeom = get_local_catchment(self.x, self.y)
        self.flowlines, self.nhdFlowlineGeom = get_local_flowlines(self.catchmentIdentifier)
        self.transformToRaster, self.transformToWGS84 = get_coordsys()
        self.projected_xy = project_point(self.x, self.y, self.transformToRaster)
        self.flw, self.flwdir_transform = get_flowgrid( self.catchmentGeom, self.transformToRaster, self.transformToWGS84 )
        self.onFlowline = get_onFlowline( self.projected_xy, self.flowlines, self.transformToRaster, self.transformToWGS84)
        self.catchment = geom_to_geojson(self.catchmentGeom, 'catchment')


        if self.onFlowline == True:
            self.intersectionPointGeom = get_intersectionPoint(self.x, self.y, self.onFlowline)
            self.streamInfo = get_reachMeasure(self.intersectionPointGeom, self.flowlines)
            self.upstreamFlowlineGeom, self.downstreamFlowlineGeom = split_flowline(self.intersectionPointGeom, self.flowlines)

            # Outputs
            if self.direction == 'up':
                self.upstreamFlowline = geom_to_geojson(self.upstreamFlowlineGeom, 'upstreamFlowline')
                self.output = {
                    'streamInfo': self.streamInfo,
                    'upstreamFlowline': self.upstreamFlowline
                }
            
            if self.direction == 'down':
                self.downstreamFlowline = geom_to_geojson(self.downstreamFlowlineGeom, 'downstreamFlowline')
                self.output = {                    
                    'streamInfo': self.streamInfo, 
                    'downstreamFlowline': self.downstreamFlowline
                }
            
            if self.direction == 'none':
                self.nhdFlowline = geom_to_geojson(self.nhdFlowlineGeom, 'nhdFlowline')
                self.output = {
                    'nhdFlowline': self.nhdFlowline,
                    'streamInfo': self.streamInfo
                }

        if self.onFlowline == False:
            self.raindropPathGeom = get_raindropPath(self.flw, self.projected_xy,  self.nhdFlowlineGeom, self.flowlines, self.transformToRaster, self.transformToWGS84)
            self.intersectionPointGeom = get_intersectionPoint(self.x, self.y, self.onFlowline, self.raindropPathGeom)
            self.streamInfo = get_reachMeasure(self.intersectionPointGeom, self.flowlines)
            self.upstreamFlowlineGeom, self.downstreamFlowlineGeom = split_flowline(self.intersectionPointGeom, self.flowlines)            

            # Outputs
            if self.direction == 'up' and self.raindropTrace == True:
                self.upstreamFlowline = geom_to_geojson(self.upstreamFlowlineGeom, 'upstreamFlowline')
                self.raindropPath = geom_to_geojson(self.raindropPathGeom, 'raindropPath')
                self.output = {
                    'raindropPath': self.raindropPath,
                    'streamInfo': self.streamInfo, 
                    'upstreamFlowline': self.upstreamFlowline
                }
            
            if self.direction == 'down' and self.raindropTrace == True:
                # self.downstreamFlowline = geom_to_geojson(self.downstreamFlowlineGeom, 'downstreamFlowline')
                # self.raindropPath = geom_to_geojson(self.raindropPathGeom, 'raindropPath')
                self.downstreamPathGeom = merge_downstreamPath(self.raindropPathGeom, self.downstreamFlowlineGeom)
                self.downstreamPath = geom_to_geojson(self.downstreamPathGeom, 'downstreamPath')
                self.output = {
                    'streamInfo': self.streamInfo,  
                    'downstreamPath': self.downstreamPath
                }
            
            if self.direction == 'none' and self.raindropTrace == True:
                self.nhdFlowline = geom_to_geojson(self.nhdFlowlineGeom, 'nhdFlowline')
                self.raindropPath = geom_to_geojson(self.raindropPathGeom, 'raindropPath')
                self.output = {
                    'raindropPath': self.raindropPath,
                    'nhdFlowline': self.nhdFlowline,
                    'streamInfo': self.streamInfo
                }
            
            if self.direction == 'up' and self.raindropTrace == False:
                 self.upstreamFlowline = geom_to_geojson(self.upstreamFlowlineGeom, 'upstreamFlowline')
                 self.output = {
                    'streamInfo': self.streamInfo, 
                    'upstreamFlowline': self.upstreamFlowline
                }
            
            if self.direction == 'down' and self.raindropTrace == False:
                self.downstreamFlowline = geom_to_geojson(self.downstreamFlowlineGeom, 'downstreamFlowline')
                self.output = {
                    'streamInfo': self.streamInfo,  
                    'downstreamFlowline': self.downstreamFlowline
                }
            
            if self.direction == 'none' and self.raindropTrace == False:
                self.nhdFlowline = geom_to_geojson(self.nhdFlowlineGeom, 'nhdFlowline')
                self.output = {
                    'nhdFlowline': self.nhdFlowline,
                    'streamInfo': self.streamInfo
                }

        # self.intersectionPoint = geom_to_geojson(self.intersectionPointGeom, 'intersectionPoint')
        self.output = json.dumps(self.output)

        if self.outfile:
            self.outfile.write(self.output)
            self.outfile.close()
            print("Wrote output to ", self.outfile)
        print('Success: Flowtrace tool complete!')

        return self.output