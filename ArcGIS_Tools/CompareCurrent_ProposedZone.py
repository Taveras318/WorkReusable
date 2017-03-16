import arcpy

Workspace = arcpy.GetParameterAsText(0)
SchoolLocation = arcpy.GetParameterAsText(1)
CurrentZone = arcpy.GetParameterAsText(2)
ProposedZone = arcpy.GetParameterAsText(3)


#Create 2640 ft buffer around school location
IdealZone = arcpy.GetParameterAsText(4)
Buffer = arcpy.Buffer_analysis(SchoolLocation, IdealZone, "2640 Feet", "FULL", "ROUND", "NONE", "")
arcpy.AddField_management(Buffer,"Compactness","DOUBLE","","","","","NULLABLE","NON_REQUIRED","")
arcpy.CalculateField_management(Buffer,"Compactness","(4*3.14*[Shape_Area]) / ([Shape_Length] * [Shape_Length])","VB","")


#Calculate compactness of each polygon
if CurrentZone != '':
    arcpy.AddField_management(CurrentZone,"Compactness","DOUBLE","","","","","NULLABLE","NON_REQUIRED","")
    arcpy.CalculateField_management(CurrentZone,"Compactness","(4*3.14*[Shape_Area]) / ([Shape_Length] * [Shape_Length])","VB","")

arcpy.AddField_management(ProposedZone,"Compactness","DOUBLE","","","","","NULLABLE","NON_REQUIRED","")
arcpy.CalculateField_management(ProposedZone,"Compactness","(4*3.14*[Shape_Area]) / ([Shape_Length] * [Shape_Length])","VB","")


#Create feature class for area of polygon that falls outside of the buffer within the current zone
if CurrentZone != '':
    Eligible_Current = arcpy.GetParameterAsText(5)
    arcpy.Erase_analysis(CurrentZone, Buffer, Eligible_Current, "")

#Create feature class for area of polygon that falls outside of the buffer within the proposed zone zone
Eligible_Proposed = arcpy.GetParameterAsText(6)
arcpy.Erase_analysis(ProposedZone, IdealZone, Eligible_Proposed, "")

