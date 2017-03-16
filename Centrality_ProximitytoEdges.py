import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("spatial")


#Set workspace
Workspace = arcpy.GetParameterAsText(0)

arcpy.env.workspace = Workspace


Polygon = arcpy.GetParameterAsText(1)

#Calculate compactness
arcpy.AddField_management(Polygon,"Compactness","DOUBLE","","","","","NULLABLE","NON_REQUIRED","")
arcpy.CalculateField_management(Polygon,"Compactness","(4*3.14*[Shape_Area]) / ([Shape_Length] * [Shape_Length])","VB","")


#Set mask to polygon
arcpy.env.mask = Polygon

#Create FC of polygon centroid
Centroid = arcpy.GetParameterAsText(2)
arcpy.FeatureToPoint_management(Polygon, Centroid, 
                                "CENTROID")


arcpy.env.workspace = r"in_memory"
#Convert polygon to line
PolygonTolineOutput = "LineFC"
Polyline = arcpy.PolygonToLine_management(Polygon, PolygonTolineOutput, "IDENTIFY_NEIGHBORS")

#Convert line to multipart feature class(each edge is a feature)
SplitLineOutput = "SplitLine"
SplitLine = arcpy.SplitLine_management(PolygonTolineOutput, SplitLineOutput)

#Create list of individual features in multipart feature class
def UniqueValues(table, field):
    """Gets list of unique Values from feature class"""
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

Sides = UniqueValues(SplitLineOutput, "OBJECTID")


#Create feature class for each feature in multipart feature class(feature class created for each edge)
for OID in Sides:
    expression = "OBJECTID =" + str(OID)
    arcpy.FeatureClassToFeatureClass_conversion(SplitLineOutput, "in_memory", "SIDE" + str(OID), "OBJECTID =" + str(OID))

#Create list on feature classes in workspace
Edges = arcpy.ListFeatureClasses()

#Creates Euclidean Distance Raster layer for each feature class in workspace with "SIDE" in name(creates euc_distance for every edge)
for fc in Edges:
    if "SIDE" in fc or Centroid in fc:
        #Set extent and maske for tool to the same as the input polygon
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = arcpy.GetParameterAsText(3)
        tempEnvironment1 = arcpy.env.mask
        arcpy.env.mask = Polygon
        arcpy.gp.EucDistance_sa(fc, "in_memory" + '\\' + fc + "EucDistance", "", "")
        arcpy.env.extent = tempEnvironment0
        arcpy.env.mask = tempEnvironment1


#Create a list of rasters in the workspace
Euc_Distances = arcpy.ListRasters()


#Creates fuzzy membership layer for every raster in the workspace
for dis in Euc_Distances:
    #Create variable for maximum distance in Euclidean distance layers
    MAX = arcpy.GetRasterProperties_management(dis, "MAXIMUM", "")
    if "SIDE" in dis:
        arcpy.gp.FuzzyMembership_sa(dis, dis[0:5]+"Fuzz", "LINEAR 0 " + str(MAX), "NONE")
    if Centroid in dis:
        arcpy.gp.FuzzyMembership_sa(dis, dis[0:5]+"Fuzz", "LINEAR" + " "+ str(MAX) +" "+"0", "NONE")


#Create list of fuzzy membership layers
Fuzz = []
for ras in arcpy.ListRasters():
    if "Fuzz" in ras:
        Fuzz.append(ras)


#Create variable for Raster Calculator Result, set it equal to first fuzzy membership layer in list
OutRaster_ = Raster(Fuzz[0])

#Map Algebra Expression, multiply each fuzzy membership layer by eachother
print type(OutRaster_)
for i in Fuzz[1:]:
    print Fuzz[1:]
    OutRaster_ *= Raster(i)

arcpy.env.workspace = Workspace
OutRaster_.save(arcpy.GetParameterAsText(4))



arcpy.Delete_management("in_memory")