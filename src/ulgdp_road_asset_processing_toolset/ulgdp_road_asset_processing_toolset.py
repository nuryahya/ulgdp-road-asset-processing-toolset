import arcpy,os,time,logging,datetime,getpass,re

# The Following classes are enhanced in Bishoftu COVID :-
###### Validate_Fields_and_Types  ...
###### Calculate_ULGDP   .....
###### Percent_Deter_Cond  .... .....

class Toolbox(object):
    def __init__(self):
        self.name = "ULGDP Tools"
        self.label = "ULGDP Tools"
        self.description = "Dire Dawa Urban Local Government  : AMP Toolsets"
        self.alias = "ulgdp"

        # List of tool classes associated with this toolbox
        self.tools = [Validate_Fields_and_Deter_Types, InitiateRoadUpdate, Road_FeatureLine_To_ChildTables, GPS_To_Road_Maintainance, CalculateTotalMaintainance, ValuateDeteriorationAndCondition]
        self.category = ["AMP-ROAD-FEATURE-UPDATE","AMP-ANALYSIS"]

#--------------------------------------------------------------------- If U have Geometry

class InitiateRoadUpdate(object):
    def __init__(self):
        self.label = "STEP 1 : Initiate Road Update"
        self.description = "This Tool is Road Update Initiator  " + \
                           "Please, run this tool before you begin any update on Road" + \
                           "Feature Class ."
        self.canRunInBackground = False
        self.category = "AMP-ROAD-FEATURE-UPDATE"

    def getParameterInfo(self):
        # Define parameter definitions

        # Input Features parameter
        gdbFullPath = arcpy.Parameter(
            displayName="ULGDP:AMP File GeoDatabase",
            name="in_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input")
        in_features = arcpy.Parameter(
            displayName="ULGDP:AMP Road Feature Class",

            name="in_features",
            datatype="Feature Class",
            parameterType="Required",
            direction="Input")


        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="Feature Class",
            parameterType="Derived",
            direction="Output")
        # Required  Vs Output is ---> The user will select the location of the Output
        # Drived Vs Output is ------> Is For Modification
        out_features.parameterDependencies = [in_features.name]
        # out_features.schema.clone = True

        parameters = [gdbFullPath, in_features,out_features]

        return parameters

    def isLicensed(self):  # optional
        return True

    def updateMessages(self, parameters):  # optional
        return

    def execute(self, parameters, messages):
        readTime = 2.5  # Pause to read what's written on dialog

        messages.AddMessage(os.getenv("username") + " welcome to ArcEthio Tools")
        time.sleep(readTime)

        arcpy.SetProgressorLabel("You are running ArcEthio Dire Toolsets")
        time.sleep(readTime)

        gdbFullPath = parameters[0].valueAsText
        data = parameters[1].valueAsText   # The Road feature class

        arcpy.env.workspace = gdbFullPath

        listFields = arcpy.ListFields(data)
        fNames = []
        for field in listFields:
            fNames.append(field.name)
        fld = "updateFilter"
        fld_name = "cw_replic"  # Carriage_Width Replica
        fld_lname = "le_replic"
        fld_report = "Report"
        fld_surfC = "surfaceCode"
        if fld not in fNames:
            arcpy.AddField_management(data, fld, "TEXT")
        if fld_name not in fNames:
            arcpy.AddField_management(data, fld_name, "DOUBLE")
        if fld_lname not in fNames:
            arcpy.AddField_management(data, fld_lname, "DOUBLE")
        if fld_report not in fNames:
            arcpy.AddField_management(data, fld_report, "TEXT", field_alias="Editing Report")
        if fld_surfC not in fNames:
            arcpy.AddField_management(data, fld_surfC, "TEXT")
        else:
            arcpy.AddMessage("ULGDP-Dire: updateFilter Field already exists")

        # Get Replica fields now

        fields = ["OBJECTID", "surfaceCode", "Road_Element_Id", "Route_id", "updateFilter", "Carriage_Width",
                  "cw_replic", "Shape_Length", "le_replic","Surface_Type"]

        # Copy the values of Surface_Type Field to SurfaceCode field ..... ...............................NEW UPDATE
        # cursor = arcpy.da.UpdateCursor(data, fields)
        # for row in cursor:
        #     row[1] = row[9]
        #     cursor.updateRow(row)
        # del cursor

        # Assign Default Values to Null values of Road_Element_Id , and Route_id ..... ...............................NEW UPDATE
        cursor = arcpy.da.UpdateCursor(data, fields)
        for row in cursor:
            if row[2] == None:
                row[2] = "RDXYDDRADD_0000_00"
            cursor.updateRow(row)
        del cursor

        cursor = arcpy.da.UpdateCursor(data, fields)
        for row in cursor:
            if row[3] == None:
                row[3] = "0000_00"
            cursor.updateRow(row)
        del cursor



        cursor = arcpy.da.UpdateCursor(data, fields)
        for row in cursor:
            if row[5] <= 0.1:
                row[5] = 0
                row[6] = 0
                row[8] = 0
            else:
                row[6] = row[5] # cw_replic = Carriage_Width
                row[8] = row[7]
            cursor.updateRow(row)
        del cursor

        arcpy.AssignDefaultToField_management(data, fields[2], default_value="RDXYDDRADD_0000_00")
        arcpy.AssignDefaultToField_management(data, fields[3], default_value= "0000_00")

        # domName = "xx"
        # inField = "surfaceCode"
        # arcpy.CreateDomain_management(gdbFullPath, domName, "Hy its me nur", field_type="TEXT", domain_type="CODED")
        # domDict = {"AE": "AR", "CR": "CR", "ER": "ER", \
        #            "GR": "GR", "LR": "LR"}
        # for code in domDict:
        #     arcpy.AddCodedValueToDomain_management(gdbFullPath, domName, code, domDict[code])
        # arcpy.AssignDomainToField_management(data, inField, domName)


class Road_FeatureLine_To_ChildTables(object):
    def __init__(self):
        self.label = "STEP 2 : Road FeatureLine To ChildTables"
        self.description = "Road Asset Data Processing Tool." + \
                           "It used to update Road Asset Data as per GIS Application Manual " + \
                           "for the revised ULGDP Asset Management Plan."
        self.canRunInBackground = False
        self.category = "AMP-ROAD-FEATURE-UPDATE"

    def getParameterInfo(self):
        # Define parameter definitions

        # Input Features parameter
        gdbFullPath = arcpy.Parameter(
            displayName="ULGDP:AMP File Geodatabase",
            name="in_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input")
        in_features = arcpy.Parameter(
            displayName="ULGDP:AMP Road Feature Class",
            name="in_features",
            datatype="Feature Class",
            parameterType="Required",
            direction="Input")

        out_features = arcpy.Parameter(
            displayName="Output Features",
            name="out_features",
            datatype="Feature Class",
            parameterType="Derived",
            direction="Output")
        # Required  Vs Output is ---> The user will select the location of the Output
        # Drived Vs Output is ------> Is For Modification
        out_features.parameterDependencies = [in_features.name]
        # out_features.schema.clone = True

        parameters = [gdbFullPath, in_features, out_features]

        return parameters

    def isLicensed(self):  # optional
        return True

    def updateMessages(self, parameters):  # optional
        return

    def execute(self, parameters, messages):
        readTime = 2.5  # Pause to read what's written on dialog

        messages.AddMessage(os.getenv("username") + " welcome to ArcEthio Tools")
        time.sleep(readTime)

        arcpy.SetProgressorLabel("You are running ArcEthio Dire Toolsets")
        time.sleep(readTime)

        def pathAssignment(parameters):

            gdbFullPath = parameters[0].valueAsText
            fc = parameters[1].valueAsText

            mytable = gdbFullPath + "/" + "Asphalt_Valuation"
            mytable1 = gdbFullPath + "/" + "Asphalt_Maintcondition"
            mytable2 = gdbFullPath + "/" + "Cobble_Valuation"
            mytable3 = gdbFullPath + "/" + "Cobble_Maintcondition"
            mytable4 = gdbFullPath + "/" + "EarthRoad_Valuation"
            mytable5 = gdbFullPath + "/" + "Earth_Road_Maintcondition"
            mytable6 = gdbFullPath + "/" + "Gravel_Redash_valuation"
            mytable7 = gdbFullPath + "/" + "Gravel_Redash_Maintcondition"
            mytable8 = gdbFullPath + "/" + "Large_Block_Stone_Valuation"
            mytable9 = gdbFullPath + "/" + "Large_Block_Stone_Maintcond"
            mytable10 = gdbFullPath + "/" + "Road_Physical"

            dirName = os.path.dirname(gdbFullPath)  # ......... index = 13

            GetFieldNames(fc)

            pathParameter = [gdbFullPath, fc, mytable, mytable1, mytable2, mytable3, mytable4, mytable5, mytable6,
                             mytable7, mytable8, mytable9, mytable10, dirName]
            return pathParameter

        def addAccessories(pathParameter):
            fc = pathParameter[1]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            # ---------------------------------------------------------------

            fc = pathParameter[2]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor
            # ----------------------------------------------------------------------

            fc = pathParameter[3]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[4]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[5]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[6]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[7]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[8]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[9]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[10]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[11]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

            fc = pathParameter[12]

            fcfieldlist = arcpy.ListFields(fc)
            fcFieldsList2 = []
            for fld in fcfieldlist:
                fcFieldsList2.append(fld.name)
            t = "Update_Time"
            if t not in fcFieldsList2:
                arcpy.AddField_management(fc, t, "DATE")
                cursor = arcpy.da.UpdateCursor(fc, t)
                d = datetime.datetime.now()
                for row in cursor:
                    row[0] = d
                    cursor.updateRow(row)
                del cursor

        def makeDefaltFields(pathParameter):

            fields = ["OBJECTID", "surfaceCode", "Road_Element_Id", "Route_id", "updateFilter", "Carriage_Width",
                      "cw_replic", "Report", "Shape_Length", "le_replic"]

            cursor = arcpy.da.UpdateCursor(pathParameter[1], fields)
            for row in cursor:

                if row[2] == "" or row[2] == None or row[2] == " ":
                    row[2] = "RDXYDDRADD_0000_00"
                if row[3] == "" or row[3] == None or row[3] == " ":
                    row[3] = "0000_00"
                    cursor.updateRow(row)
            del cursor

            cursor = arcpy.da.UpdateCursor(pathParameter[1], fields)
            for row in cursor:

                if row[6] != row[5]:
                    row[3] = "0000_00"
                    row[7] = "Carriage_W update frm {0} to {1} meters".format(row[5], row[6])

                if row[1][0] != row[2][2] or row[1][1] != row[2][3]:
                    row[3] = "0000_00"
                    row[7] = "Surface update frm {0} to {1}".format(row[2][2] + row[2][3], row[1][0] + row[1][1])

                if row[9] != row[8]:
                    row[3] = "0000_00"
                    row[7] = "Length update frm {0} to {1} meters".format(row[9], row[8])

                    # If all Carriage width, Surface Material , Length respectively and are updated symmul

                if row[6] != row[5] and row[1][0] != row[2][2] and row[9] != row[8]:
                    row[3] = "0000_00"
                    row[7] = "Carriage_W + Surface_Mat + Length : Updated"

                    # If Surface Material and Road Length are updated ...
                if row[1][0] != row[2][2] and row[9] != row[8]:
                    row[3] = "0000_00"
                    row[7] = "Surface_Mat + Length : Updated"

                    # If Carriage width and Road Length are updated ...
                if row[6] != row[5] and row[9] != row[8]:
                    row[3] = "0000_00"
                    row[7] = "Carriage_W + Length : Updated"

                    # If Carriage width and Surface Material are updated ...
                if row[6] != row[5] and row[1][0] != row[2][2]:
                    row[3] = "0000_00"
                    row[7] = "Carriage_W + Surface_Mat : Updated"

                if row[3] == "" or row[3] == None or row[3] == "0000_00" or row[3] == "0" or row[3] == "00" or row[
                    3] == "000" or row[3] == "000_" or row[3] == "000_0" or row[3] == " ":
                    row[3] = "0000_00"

                if row[3] == "0000_00":
                    row[2] = "RDXYDDRADD_0000_00"
                if row[2] == "RDXYDDRADD_0000_00":
                    row[3] = "0000_00"

                    cursor.updateRow(row)
            del cursor




        def Assign_Route_Id(pathParameter):


            fields = ["OBJECTID", "surfaceCode", "Road_Element_Id", "Route_id", "updateFilter"]
            # pathParameter = [gdbFullPath,fc]

            wrCl = """"Route_id" = '0000_00' """
            cursor = arcpy.da.UpdateCursor(pathParameter[1], fields)
            placeDict = {}
            updatedRecodsDict = {}
            finalDict_rd_elementID = {}
            finalDict_rtIDD = {}

            for row in cursor:
                if row[3]== None or row[3]== "0000_00" or row[3]== "" or row[3]== "0000":
                    row[3]= "0000_00"
                    row[2] = "RDXYDDRADD_0000_00"
                cursor.updateRow(row)
            del cursor

            cursor = arcpy.da.UpdateCursor(pathParameter[1], fields)

            for row in cursor:
                if len(str(row[0])) == 1 and row[3] != "0000_00":
                    row[3]= "000" + str(row[0]) + "_00"
                if len(str(row[0])) == 2 and row[3] != "0000_00":
                    row[3] = "00" + str(row[0]) + "_00"
                if len(str(row[0])) == 3 and row[3] != "0000_00":
                    row[3] = "0" + str(row[0]) + "_00"
                if len(str(row[0])) == 4 and row[3] != "0000_00":
                    row[3] = str(row[0]) + "_00"

                        # for ki,rmid in placeDict.iteritems():
                cursor.updateRow(row)
            del cursor








        def correctIDSS(pathParameter):

            ''' Before calling this function , make sure that Route_id field
            must be populated with a Default Value = 0000_00
            Road_Element_id field muat also be populated with the default value "RDXYDDRADD_0000_00"
            surfaceCode Field with = NL

            Road_Element_id  is Updated if and only if XY  =! NL  ... That means This function updates
            Road_Element_Id if andOnly if there is change in surfaceCode '''
            import arcpy, datetime

            fields = ["OBJECTID", "surfaceCode", "Road_Element_Id", "Route_id", "updateFilter"]
            # pathParameter = [gdbFullPath,fc]

            wrCl = """"Route_id" = '0000_00' """
            cursor = arcpy.da.UpdateCursor(pathParameter[1], fields, wrCl)
            placeDict = {}
            updatedRecodsDict = {}
            finalDict_rd_elementID = {}
            finalDict_rtIDD = {}

            for row in cursor:
                # for ki,rmid in placeDict.iteritems():

                ki = row[0]
                rd_elmt_id = row[2]  # "Road_Element_Id"
                surfaceCode = row[1]
                routeID = row[3]  # "Route_id"
                combinlist = [rd_elmt_id, surfaceCode, routeID]
                placeDict[ki] = combinlist  # = {OBJECTID:[Road_Element_Id,surfaceCode,Route_id]}
                # placeDict = {123:["RDXYDDRADD_0000_00","AR","0000_00"]}

                for k, v in placeDict.iteritems():
                    if type(v[0]) != type(v[1]):  # inorder to Assign the Default
                        v[0] = "RDXYDDRADD_0000_00"  # Unnecessary ,,, RDXYDDRADD_0000_00
                        v[1] = "NL"
                        # u'RDGRDDRADD_4485_00'     ...................Below this line of code ... Begin ..
                    firstChr = v[0][2]  # OK ... necessary
                    secondChr = v[0][3]
                    both = firstChr + secondChr
                    if (v[1]) != both:  # .........................................................................

                        updatedRecodsDict[k] = v
                # print  updatedRecodsDict
                for kk, vv in updatedRecodsDict.iteritems():
                    kk_string = str(kk)
                    # print kk_string[3]
                    j = '$'.join(vv)  # j =    RDXYDDRADD_0000_0$NL$0000_00 Data Type =  <type 'unicode'>
                    m = '$'.join(j)
                    jm = m.split("$")

                    rd_elementID = jm[:18]

                    if len(kk_string) == 4:
                        rd_elementID[2] = jm[20]  # jm[19]
                        rd_elementID[3] = jm[21]  # Cha jm[20]
                        rd_elementID[11] = kk_string[0]
                        rd_elementID[12] = kk_string[1]
                        rd_elementID[13] = kk_string[2]
                        rd_elementID[14] = kk_string[3]
                        rd_elementID[16] = u'0'
                        rd_elementID[17] = u'0'
                    elif len(kk_string) == 3:
                        rd_elementID[2] = jm[20]
                        rd_elementID[3] = jm[21]
                        rd_elementID[11] = u'0'
                        rd_elementID[12] = kk_string[0]
                        rd_elementID[13] = kk_string[1]
                        rd_elementID[14] = kk_string[2]
                        rd_elementID[16] = u'0'
                        rd_elementID[17] = u'0'
                    elif len(kk_string) == 2:
                        rd_elementID[2] = jm[20]
                        rd_elementID[3] = jm[21]
                        rd_elementID[11] = u'0'
                        rd_elementID[12] = u'0'
                        rd_elementID[13] = kk_string[0]
                        rd_elementID[14] = kk_string[1]
                        rd_elementID[16] = u'0'
                        rd_elementID[17] = u'0'
                    elif len(kk_string) == 1:
                        rd_elementID[2] = jm[20]
                        rd_elementID[3] = jm[21]
                        rd_elementID[11] = u'0'
                        rd_elementID[12] = u'0'
                        rd_elementID[13] = u'0'
                        rd_elementID[14] = kk_string[0]
                        rd_elementID[16] = u'0'
                        rd_elementID[17] = u'0'
                    # print rd_elementID

                    rtIDD = jm[len(jm) - 7:]

                    if len(kk_string) == 4:
                        rtIDD[0] = kk_string[0]
                        rtIDD[1] = kk_string[1]
                        rtIDD[2] = kk_string[2]
                        rtIDD[3] = kk_string[3]
                        rtIDD[5] = u'0'
                        rtIDD[6] = u'0'
                    if len(kk_string) == 3:
                        rtIDD[0] = u'0'
                        rtIDD[1] = kk_string[0]
                        rtIDD[2] = kk_string[1]
                        rtIDD[3] = kk_string[2]
                        rtIDD[5] = u'0'
                        rtIDD[6] = u'0'

                    if len(kk_string) == 2:
                        rtIDD[0] = u'0'
                        rtIDD[1] = u'0'
                        rtIDD[2] = kk_string[0]
                        rtIDD[3] = kk_string[1]
                        rtIDD[5] = u'0'
                        rtIDD[6] = u'0'
                    if len(kk_string) == 1:
                        rtIDD[0] = u'0'
                        rtIDD[1] = u'0'
                        rtIDD[2] = u'0'
                        rtIDD[3] = kk_string[0]
                        rtIDD[5] = u'0'
                        rtIDD[6] = u'0'
                    # print rtIDD
                    vCorrect_rd_elementID = ''.join(rd_elementID)
                    vCorrect_rtIDD = ''.join(rtIDD)

                    finalDict_rd_elementID[kk] = vCorrect_rd_elementID
                    finalDict_rtIDD[kk] = vCorrect_rtIDD

                for kkk, vvv in finalDict_rd_elementID.iteritems():  # fields = ["OBJECTID", "surfaceCode", "Road_Element_Id", "Route_id","updateFilter" ]
                    if kkk == row[0]:
                        nurtime = datetime.datetime.now()
                        row[2] = vvv
                        row[4] = 'Updated at {}'.format(nurtime)
                        cursor.updateRow(row)
                for ku, vu in finalDict_rtIDD.iteritems():
                    if ku == row[0]:
                        row[3] = vu
                        row[4] = 'Updated at {}'.format(nurtime)
                        cursor.updateRow(row)

            del cursor
            #
            cursor = arcpy.da.UpdateCursor(pathParameter[1], fields)
            for row in cursor:
                if row[1] not in ["AR", "CR", "ER", "GR", "LR"]:
                    row[4] = 'Please Enter The Surface Code !!'

                    cursor.updateRow(row)
            del cursor

        def recordTransfer(pathParameter):
            fc = pathParameter[1]  # fc = Road
            mytable = pathParameter[2]  # "Asphalt_Valuation"
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []  # List of "Route_id" of fc = Road  ... all Route_id  ... Edited + Non Edited ... ie All Route_id list
            fc_id_dict = {}  # {"Route_id":"surfaceCode"} of fc = Road .. all Edited + Non edited ... all in fc

            for row in cursorSR:  # ["OBJECTID"[0], "Route_id"[1], "surfaceCode"[2], "Road_Element_Id", [3]]
                fc_id_list.append(row[1])  # Route_id
                k = row[1]  # Route_id
                v = row[2]  # SUrfaceCode
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)  # For "Asphalt_Valuation" table
            mytable_id_list = []  # List of "Route_id" of mytable = "Asphalt_Valuation"
            mytable_id_dict = {}  # {"OBJECTID_1":"Route_id"} of mytable = "Asphalt_Valuation"
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []  # "Route_id" Value Available in fc = Road  BUT NOT in mytable
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "AR":  # mytable_id_list = [] # List of "Route_id" of mytable = "Asphalt_Valuation"

                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # print ii
            # print ids_not_created_in_mytable

            if len(
                    ids_not_created_in_mytable) != 0:  # Under This Code ... Include cursurUpCobble = arcpy.da.UpdateCursor(pathParameter[4],"Route_id")
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)  # and for row in cursurUpCobble :
                    del row
                del cursorIN
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_cobbleValuation:
                    for roww in cursor_cobbleValuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_cobbleValuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_cobbleMaintcondition:
                    for ro in cursor_cobbleMaintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_cobbleMaintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_EarthRoad_Maintcondition:
                    for ro in cursor_EarthRoad_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # --------------

                    # with arcpy.da.UpdateCursor(pathParameter[4],["Route_id"]) as cursurUpCobble:
                    # for row , n in zip (cursurUpCobble,ids_not_created_in_mytable):
                    # if row[0] == n :
                    # arcpy.DeleteRows_management(row[0])
                    # print "The record {} is Inserted".format(i)
                    # del row

            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # --------------------------------------------------------------

            mytable = pathParameter[3]  # Asphalt_Maintcondition
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "AR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # print ii
            # print ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    print "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_cobbleValuation:
                    for roww in cursor_cobbleValuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_cobbleValuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_cobbleMaintcondition:
                    for ro in cursor_cobbleMaintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_cobbleMaintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_EarthRoad_Maintcondition:
                    for ro in cursor_EarthRoad_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE
            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")
            # --------------------------------------------------------------------------------------------------

            mytable = pathParameter[4]  # Cobble_Valuation  +++++++++++++++START++++++ START+++++++ NOT DONE
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "CR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # print ii
            # print ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    print "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_EarthRoad_Maintcondition:
                    for ro in cursor_EarthRoad_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE





            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")
            # --------------------------------------------------------------------------------------------------------

            mytable = pathParameter[5]
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "CR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # print ii
            # print ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    print "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_EarthRoad_Maintcondition:
                    for ro in cursor_EarthRoad_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE






            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # --------------------------------------------------------------------------------------------------------------------
            mytable = pathParameter[6]  # EarthRoad_Valuation
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "ER":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            print ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE




            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # ------------------------------------------------------------------------------------------

            mytable = pathParameter[7]
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "ER":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE





            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")
            # -----------------------------------------------------------------------------------------

            mytable = pathParameter[8]  # Gravel_Redash_valuation
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "GR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE




            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # ----------------------------------------------------------------------------------------

            mytable = pathParameter[9]
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "GR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE





            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # --------------------------------------------------------------------------

            mytable = pathParameter[10]
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "LR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # -------------- DOOONNNEEEEEEE





            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # -----------------------------------------------------------------------

            mytable = pathParameter[11]  # The Next 12
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id", "Road_Element_Id"]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list and v == "LR":
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # -------------- DOOONNNEEEEEEE




            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

            # ------------------------------------------------------------------------------------------------------------
            # +++++++ NOT DOND ++++ NOTDONE +++++++++ BELOW THIS LINE
            mytable = pathParameter[12]  # Road_Physical
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]
            mytable_fields_impo = ["OBJECTID", "Route_id",
                                   "Road_Element_Id"]  # ............................................................. Deleted "Road_Element_Id"

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []
            fc_id_dict = {}

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            cursorSR = arcpy.da.SearchCursor(mytable, mytable_fields_impo)
            mytable_id_list = []
            mytable_id_dict = {}
            for row in cursorSR:
                mytable_id_list.append(row[1])
                k = row[0]
                v = row[1]
                mytable_id_dict[k] = str(v)
            del cursorSR

            ids_not_created_in_mytable = []
            for f, v in fc_id_dict.iteritems():
                if f not in mytable_id_list:
                    # for f in fc_id_list:
                    #     if f not in mytable_id_list:
                    ids_not_created_in_mytable.append(f)
            ii = len(ids_not_created_in_mytable)
            # ii
            # ids_not_created_in_mytable

            if len(ids_not_created_in_mytable) != 0:
                cursorIN = arcpy.InsertCursor(mytable)
                for i in range(ii):
                    row = cursorIN.newRow()
                    newRecord = ids_not_created_in_mytable
                    row.setValue("Route_id", newRecord[i])
                    cursorIN.insertRow(row)
                    # "The record {} is Inserted".format(i)
                    del row
                del cursorIN

                with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                    for roww in cursor_Asphalt_Valuation:
                        for n in ids_not_created_in_mytable:
                            if roww[0] == n:
                                # arcpy.DeleteRows_management(roww[0])
                                cursor_Asphalt_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                    for ro in cursor_Asphalt_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Asphalt_Maintcondition.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                    for ro in cursor_Cobble_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                    for ro in cursor_Cobble_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Cobble_Maintcondition.deleteRow()  # LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
                with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                    for ro in cursor_EarthRoad_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_EarthRoad_Valuation.deleteRow()
                with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # ..................DOne
                with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                    for ro in cursor_Gravel_Redash_valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                    for ro in cursor_Gravel_Redash_Maintcondition:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Gravel_Redash_Maintcondition.deleteRow()  # -------------- DOOONNNEEEEEEEOOOOOOOOOOOOOOOOOOO
                with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                    for ro in cursor_Large_Block_Stone_Valuation:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Valuation.deleteRow()  # ...............

                with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                    for ro in cursor_Large_Block_Stone_Maintcond:
                        for vl in ids_not_created_in_mytable:
                            if ro[0] == vl:
                                # arcpy.DeleteRows_management(ro[0])
                                cursor_Large_Block_Stone_Maintcond.deleteRow()  # -------------- DOOONNNEEEEEEE


            else:
                arcpy.AddMessage("DDUPRPO: All Records Available")

        def GetFieldNames(data):
            listFields = arcpy.ListFields(data)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "updateFilter"
            if fld not in fNames:
                arcpy.AddField_management(data, fld, "TEXT")
            else:
                arcpy.AddMessage("ULGDP-Dire: updateFilter Field already exists")

        def CleanChildTables(pathParameter):  # Finally to be executed
            '''This Function cleans unnessary Route_id*
            values in Child Tabes. I.e All Route_id* Field Values
            in Child Tables not Available in Mother Feature Class : Road'''
            fc = pathParameter[1]  # fc = Road
            fc_fields_impo = ["OBJECTID", "Route_id", "surfaceCode", "Road_Element_Id", ]

            cursorSR = arcpy.da.SearchCursor(fc, fc_fields_impo)

            fc_id_list = []  # List of "Route_id" of fc = Road ...................................................1
            fc_id_dict = {}  # {"Route_id":"surfaceCode"} of fc = Road

            for row in cursorSR:
                fc_id_list.append(row[1])
                k = row[1]
                v = row[2]
                fc_id_dict[k] = str(v)
            del cursorSR

            with arcpy.da.UpdateCursor(pathParameter[2], ["Route_id"]) as cursor_Asphalt_Valuation:
                for row in cursor_Asphalt_Valuation:
                    if row[0] not in fc_id_list:
                        cursor_Asphalt_Valuation.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[3], ["Route_id"]) as cursor_Asphalt_Maintcondition:
                for row in cursor_Asphalt_Maintcondition:
                    if row[0] not in fc_id_list:
                        cursor_Asphalt_Maintcondition.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[4], ["Route_id"]) as cursor_Cobble_Valuation:
                for row in cursor_Cobble_Valuation:
                    if row[0] not in fc_id_list:
                        cursor_Cobble_Valuation.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[5], ["Route_id"]) as cursor_Cobble_Maintcondition:
                for row in cursor_Cobble_Maintcondition:
                    if row[0] not in fc_id_list:
                        cursor_Cobble_Maintcondition.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[6], ["Route_id"]) as cursor_EarthRoad_Valuation:
                for row in cursor_EarthRoad_Valuation:
                    if row[0] not in fc_id_list:
                        cursor_EarthRoad_Valuation.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[7], ["Route_id"]) as cursor_Earth_Road_Maintcondition:
                for row in cursor_Earth_Road_Maintcondition:
                    if row[0] not in fc_id_list:
                        cursor_Earth_Road_Maintcondition.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[8], ["Route_id"]) as cursor_Gravel_Redash_valuation:
                for row in cursor_Gravel_Redash_valuation:
                    if row[0] not in fc_id_list:
                        cursor_Gravel_Redash_valuation.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[9], ["Route_id"]) as cursor_Gravel_Redash_Maintcondition:
                for row in cursor_Gravel_Redash_Maintcondition:
                    if row[0] not in fc_id_list:
                        cursor_Gravel_Redash_Maintcondition.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[10], ["Route_id"]) as cursor_Large_Block_Stone_Valuation:
                for row in cursor_Large_Block_Stone_Valuation:
                    if row[0] not in fc_id_list:
                        cursor_Large_Block_Stone_Valuation.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[11], ["Route_id"]) as cursor_Large_Block_Stone_Maintcond:
                for row in cursor_Large_Block_Stone_Maintcond:
                    if row[0] not in fc_id_list:
                        cursor_Large_Block_Stone_Maintcond.deleteRow()
            with arcpy.da.UpdateCursor(pathParameter[12], ["Route_id"]) as cursor_Road_Physical:
                for row in cursor_Road_Physical:
                    if row[0] not in fc_id_list:
                        cursor_Road_Physical.deleteRow()

        def LoggingforASCII(pathParameter):
            fc = pathParameter[1]
            fields = ["OBJECTID", "Surface_Type", "Road_Element_Id", "surfaceCode", "updateFilter", "Update_Time"]
            os.chdir(pathParameter[13])
            fname = 'RoadUpdate_at_{0}'.format(time.time()) + ".log"
            logging.basicConfig(filename=fname, level=logging.INFO)
            fname = 'RoadUpdate_at_{0}'.format(time.time() + 1) + ".log"
            fullPath_fname = os.path.join(pathParameter[13], fname)
            # logging.info("It is Me")
            arcpy.ExportXYv_stats(fc, fields, "COMMA", fullPath_fname, "ADD_FIELD_NAMES")

        def finalize(pathParameter):
            fc = pathParameter[1]
            fieldList = arcpy.ListFields(fc)
            fNames = []
            for field in fieldList:
                fNames.append(field.name)

            for f in fNames:
                if f == "cw_replic" or f == "le_replic":
                    arcpy.DeleteField_management(fc, f)
            fields = ["OBJECTID", "surfaceCode", "Surface_Type", "Report"]

            cursor = arcpy.da.UpdateCursor(fc, fields)

            for row in cursor:
                if row[1] == "AR":
                    row[2] = "Asphalt Road"
                elif row[1] == "CR":
                    row[2] = "Cobblestone Road"
                elif row[1] == "ER":
                    row[2] = "Compacted Earth Road"
                elif row[1] == "GR":
                    row[2] = "Gravel Road"
                elif row[1] == "LR":
                    row[2] = "Large Block Stone Road"
                else:
                    row[3] = "Please Enter the Surface Code !"
                cursor.updateRow(row)
            del cursor

        def main():
            readTime = 2.5  # Pause to read what's written on dialog

            arcpy.SetProgressor("default",
                                "Dire Dawa ULGDP - Road Asset Updating Demo GP Tool    : \n  Developed by : Nur Yahya Kedirkhan ,Mobile:(+251)0982024688")
            arcpy.AddMessage("Dear {0}, You are Running Road Asset Updating Demo GP Tool".format(getpass.getuser()))

            time.sleep(5)

            pp = pathAssignment(parameters)
            makeDefaltFields(pp)
            Assign_Route_Id(pp)
            correctIDSS(pp)
            addAccessories(pp)
            recordTransfer(pp)
            recordTransfer(pp)
            CleanChildTables(pp)
            finalize(pp)
            arcpy.AddMessage(
                "For further info,contact\n Mr.Yonas Abate ... Mobile:(+251)0933266518 ... Dire ULGDP \n Mr.Binyam G/Tensay ... Mobile:(+251)0930102024 ... DDUPRP \n Mr.Nur Yahya ... Mobile:(+251)0982024688 ... The Developer \n Dire Dawa \n ETHIOPIA")
            time.sleep(5)
            arcpy.AddMessage("Dire ULGDP : All Done")
            LoggingforASCII(pp)
            arcpy.ResetProgressor()

        pathParameter = pathAssignment(parameters)
        fc = pathParameter[1]
        gdbFullpath = pathParameter[0]
        fieldList = arcpy.ListFields(fc)
        fNames = []
        for field in fieldList:
            fNames.append(field.name)
        if "cw_replic" in fNames or u'cw_replic' in fNames:
            main()

        else:
            raise IOError(
                "Dear {0}, Please,run the ULGDP Precondition Tool,first.\nFor further info:\nPlease Contact: Nur Yahya , Mobile: +2510982024688 ".format(
                    getpass.getuser()))


#---------------------------------------------------------------------

class Validate_Fields_and_Deter_Types(object): # First
    """  Further enhanced during covid-19 in Bishoft
    This validator has to be run before executing the ff classes
    Calculate_ULGDP , Percent_Deter_Cond and GPS_To_Road_Maintainance"""


    def __init__(self):
        self.label = "STEP 1 : Check Mandatory Fields and Deter Types"
        self.description = "Run this tool before executing 'Calculate Total Maintainance Tool'" \
                           "and 'Valuate Deterioration and Condition Tool'.It is used to validate " \
                           "the existance of necessary fields and field types in child tables............." \
                           "NOTE:The following Child Tables must exist before in you run this Tool:----------" \
                           "[[[----  Asphalt_Maintcondition,Cobble_Valuation,Cobble_Maintcondition,Earth_Road_Maintcondition" \
                           "Gravel_Redash_valuation,Gravel_Redash_Maintcondition,Large_Block_Stone_Valuation," \
                           "Large_Block_Stone_Maintcond,Road_Physical ----]]]----" \
                           "---- NOTE : All Table Names are Case Sensitive.----" \
                           "----------------------------------------------------------------------------------------" \








        self.canRunInBackground = False
        self.category = "AMP-ANALYSIS"

    def getParameterInfo(self):
        # Define parameter definitions

        # Input Features parameter
        gdbFullPath = arcpy.Parameter(
            displayName="ULGDP:AMP File Geodatabase",
            name="in_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input")

        in_features=arcpy.Parameter(
            displayName="ULGDP:AMP GPS Feature Class",
            name="in_features",
            datatype="Feature Class",
            parameterType="Required",
            direction="Input")









        parameters = [gdbFullPath,in_features]

        return parameters

    def isLicensed(self):  # optional
        return True


    def updateMessages(self, parameters):  # optional
        return

    def execute(self, parameters, messages):
        readTime = 2.5  # Pause to read what's written on dialog

        messages.AddMessage(os.getenv("username") + " welcome to ArcEthio Tools")
        time.sleep(readTime)

        arcpy.SetProgressorLabel("You are running ArcEthio Dire Toolsets")
        time.sleep(readTime)

        def pathAssignment(parameters):

            gdbFullPath = parameters[0].valueAsText
            fc = parameters[1].valueAsText

            mytable = gdbFullPath + "/" + "Asphalt_Valuation"
            mytable1 = gdbFullPath + "/" + "Asphalt_Maintcondition"
            mytable2 = gdbFullPath + "/" + "Cobble_Valuation"
            mytable3 = gdbFullPath + "/" + "Cobble_Maintcondition"
            mytable4 = gdbFullPath + "/" + "EarthRoad_Valuation"
            mytable5 = gdbFullPath + "/" + "Earth_Road_Maintcondition"
            mytable6 = gdbFullPath + "/" + "Gravel_Redash_valuation"
            mytable7 = gdbFullPath + "/" + "Gravel_Redash_Maintcondition"
            mytable8 = gdbFullPath + "/" + "Large_Block_Stone_Valuation"
            mytable9 = gdbFullPath + "/" + "Large_Block_Stone_Maintcond"
            mytable10 = gdbFullPath + "/" + "Road_Physical"

            dirName = os.path.dirname(gdbFullPath)  # ......... index = 13


            pathParameter = [gdbFullPath, fc, mytable, mytable1, mytable2, mytable3, mytable4, mytable5, mytable6,
                             mytable7, mytable8, mytable9, mytable10, dirName]
            return pathParameter

        def Find_Missing_Fields(pathParameter):

            gdbFullPath = pathParameter[0]
            # fc_gps = pathParameter[1]
            AsphaltMaint = pathParameter[3]
            CobbleMaint = pathParameter[5]
            EarthMaint= pathParameter[7]
            GravelMaint= pathParameter[9]
            LargeBlockMaint= pathParameter[11]




            arcpy.env.workspace = gdbFullPath

            list_field_objects_AspaltMaint = arcpy.ListFields(AsphaltMaint)
            list_field_objects_CobbleMaint = arcpy.ListFields(CobbleMaint)
            list_field_objects_EarthMaint = arcpy.ListFields(EarthMaint)
            list_field_objects_GravelMaint = arcpy.ListFields(GravelMaint)
            list_field_objects_LargeblockMaint = arcpy.ListFields(LargeBlockMaint)


            dict_of_fName_vs_fType_AsphaltMaint = {}
            dict_of_fName_vs_fType_CobbleMaint = {}
            dict_of_fName_vs_fType_EarthMaint = {}
            dict_of_fName_vs_fType_GravelMaint = {}
            dict_of_fName_vs_fType_LargeBlockMaint = {}


            for fld_obj in list_field_objects_AspaltMaint:
                k = fld_obj.name
                v = fld_obj.type
                dict_of_fName_vs_fType_AsphaltMaint[k] = v

            for fld_obj in list_field_objects_CobbleMaint:
                k = fld_obj.name
                v = fld_obj.type
                dict_of_fName_vs_fType_CobbleMaint[k] = v

            for fld_obj in list_field_objects_EarthMaint:
                k = fld_obj.name
                v = fld_obj.type
                dict_of_fName_vs_fType_EarthMaint[k] = v

            for fld_obj in list_field_objects_GravelMaint:
                k = fld_obj.name
                v = fld_obj.type
                dict_of_fName_vs_fType_GravelMaint[k] = v

            for fld_obj in list_field_objects_LargeblockMaint:
                k = fld_obj.name
                v = fld_obj.type
                dict_of_fName_vs_fType_LargeBlockMaint[k] = v



            must_fld_AspahltMaint = [ (u'Unit_Cost_Potholes', u'Double')
                , (u'Unit_Cost_Peeling', u'Double'), (u'Unit_Cost_Cracking', u'Double'), (u'Element_Start', u'Double'),
                                     (u'Element_End', u'Double'), (u'Width_Element', u'Double')]

            must_fld_CobbleMaint = [(u'Unit_Cost_Lifting', u'Double'),
                                    (u'Unit_Cost_Depression', u'Double'), (u'Unit_Cost_Cobedging', u'Double'),
                                    (u'Tot_Deter_Leng_edg_BNnod', u'Double'),
                                    (u'Element_Start', u'Double'), (u'Element_End', u'Double'),
                                    (u'Width_Element', u'Double')]

            must_fld_EarthMaint = [
                                   (u'Unit_Cost_Potholes', u'Double'), (u'Unit_Cost_Washing', u'Double'),
                                   (u'Element_Start', u'Double'), (u'Element_End', u'Double'),
                                   (u'Width_Element', u'Double')]

            must_fld_GravelMaint = [
                                    (u'Unit_Cost_Channeling', u'Double'), (u'Unit_Cost_Washing', u'Double'),
                                    (u'Unit_Cost_Potholes', u'Double'),
                                    (u'Element_Start', u'Double'), (u'Element_End', u'Double'),
                                    (u'Width_Element', u'Double')]

            must_fld_LargeBlockMaint = [(u'Unit_Cost_Lifting',u'Double'),
                                        (u'Unit_Cost_Depression',u'Double'),
                                        (u'Element_Start', u'Double'), (u'Element_End', u'Double'),
                                        (u'Width_Element', u'Double')]
            # Mandatory (Field Names , Field Types) Not available in ur input Table = Asphalt_Maint

            fields_not_in_AsphaltMaint = [fld for fld in must_fld_AspahltMaint if fld not in dict_of_fName_vs_fType_AsphaltMaint.items()]
            fields_not_in_CobbleMaint = [fld for fld in must_fld_CobbleMaint if fld not in dict_of_fName_vs_fType_CobbleMaint.items()]
            fields_not_in_EarthMaint = [fld for fld in must_fld_EarthMaint if fld not in dict_of_fName_vs_fType_EarthMaint.items()]
            fields_not_in_GravelMaint = [fld for fld in must_fld_GravelMaint if fld not in dict_of_fName_vs_fType_GravelMaint.items()]
            fields_not_in_LargeMaint = [fld for fld in must_fld_LargeBlockMaint if fld not in dict_of_fName_vs_fType_LargeBlockMaint.items()]
            # The result of the above code , for example of "fields_not_in_AsphaltMaint" the result will be of the
            # this type = [(u'Area_Cracking', u'Double'), (u'Area_Peeling', u'Double'), (u'Area_Potholes', u'Double'), (u'Unit_Cost_Potholes', u'Double'), (u'Unit_Cost_Peeling', u'Double'), (u'Unit_Cost_Cracking', u'Double'), (u'Width_Element', u'Double')]


            lost_fields = [fields_not_in_AsphaltMaint,fields_not_in_CobbleMaint,fields_not_in_EarthMaint,
                           fields_not_in_GravelMaint,fields_not_in_LargeMaint]
            # lost_fields will be list of list of the following type
            #var_lost_fields = [[(), (), ()], [(), (), ()], [(),(),()],[(),()]]

            return lost_fields

        def Find_Deter_NOT_for_SurfaceType(pathParameter):
            '''Finds missing mandatory fields in Child Tables.
            and populated deterioration values not as per standard   '''

            ws = pathParameter[0]
            fc_gps = pathParameter[1]
            arcpy.env.workspace=ws
            # fc_pt_xy_to_line=os.path.join(ws, "Near_5m_dist")

            listFields = arcpy.ListFields(fc_gps)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "COMMENT_SURFACE_VR_DETER"
            if fld not in fNames:
                arcpy.AddField_management(fc_gps, fld, "TEXT")

            fields_fc_pt = ['SURFACE_CODE', 'DETERIORATION', 'COMMENT_SURFACE_VR_DETER']

            cursor = arcpy.da.UpdateCursor(fc_gps, fields_fc_pt)
            for row in cursor:
                if row[0] == 'AR' and row[1] != 'Potholes' and row[1] != 'Cracking' and row[1] != 'Peeling':
                    row[2]= 'DETER_TYPE_REJECTED'
                cursor.updateRow(row)
            del cursor
            cursor = arcpy.da.UpdateCursor(fc_gps, fields_fc_pt)
            for row in cursor:
                if row[0] == 'CR' and row[1] != 'Lifting' and row[1] != 'Depression' and row[1] != 'Edging_Failure':
                    row[2]= 'DETER_TYPE_REJECTED'
                cursor.updateRow(row)
            del cursor

            cursor = arcpy.da.UpdateCursor(fc_gps, fields_fc_pt)
            for row in cursor:
                if row[0] == 'ER' and row[1] != 'Potholes' and row[1] != 'Washing' :
                    row[2]= 'DETER_TYPE_REJECTED'
                cursor.updateRow(row)
            del cursor

            cursor = arcpy.da.UpdateCursor(fc_gps, fields_fc_pt)
            for row in cursor:
                if row[0] == 'GR' and row[1] != 'Potholes' and row[1] != 'Washing' and row[1] != 'Channeling':
                    row[2]= 'DETER_TYPE_REJECTED'
                cursor.updateRow(row)
            del cursor

            cursor = arcpy.da.UpdateCursor(fc_gps, fields_fc_pt)
            for row in cursor:
                if row[0] == 'LR' and row[1] != 'Lifting' and row[1] != 'Depression':
                    row[2]= 'DETER_TYPE_REJECTED'
                cursor.updateRow(row)
            del cursor

            cursor = arcpy.da.UpdateCursor(fc_gps, fields_fc_pt)
            for row in cursor:
                if row[2] != 'DETER_TYPE_REJECTED':
                    row[2]= 'DETER_TYPE_ACCEPTED'
                cursor.updateRow(row)
            del cursor










            # not_for_asphalt_layer="Deter_Not_For_Asphalt"
            # wrc_notfor_asphalt = """ SURFACE_CODE = 'AR' AND DETERIORATION <> 'Potholes' AND DETERIORATION <> 'Cracking' AND DETERIORATION <> 'Peeling' """
            # arcpy.MakeFeatureLayer_management(fc_gps, not_for_asphalt_layer, wrc_notfor_asphalt)




        def main():
            readTime = 2.5  # Pause to read what's written on dialog

            arcpy.SetProgressor("default",
                                "Dire Dawa ULGDP - Road Asset Updating Demo GP Tool    : \n  Developed by : Nur Yahya Kedirkhan ,Mobile:(+251)0982024688")
            arcpy.AddMessage("Dear {0}, You are Running Road Asset Updating Demo GP Tool".format(getpass.getuser()))

            time.sleep(5)

            pp = pathAssignment(parameters)
            f = Find_Missing_Fields(pp) # f is a list of list [[(), (), ()], [(), (), ()], [(),(),()],[(),()]]
            Find_Deter_NOT_for_SurfaceType(pp)
            #f[0] = fields_not_in_AsphaltMaint = [(), (), ()]
            #f[1] = fields_not_in_CobbleMaint = [(), (), ()]
            #f[2] = fields_not_in_EarthMaint = [(), (), ()]
            #f[3] = fields_not_in_GravelMaint = [(), (), ()]
            #f[4] = fields_not_in_LargeMaint = [(), (), ()]
            arcpy.AddMessage("************************************************************")
            if f[0] == []:
                arcpy.AddMessage("All Required Fields are available in Asphalt_Maint Table")
            if f[0] != []:
                messages.addErrorMessage("Fields and/or missed in Asphalt_Maint Table = {0}".format(f[0]))

            if f[1] == []:
                arcpy.AddMessage("All Required Fields are available in Cobble_Maint Table")
            if f[1]!= []:
                messages.addErrorMessage("Fields and/or missed in Cobble_Maint Tablee = {0}".format(f[1]))

            if f[2] == []:
                arcpy.AddMessage("All Required Fields are available in Earth_Maint Table")
            if f[2] != []:
                messages.addErrorMessage("Fields and/or missed in Earth_Maint Table = {0}".format(f[2]))

            if f[3] == []:
                arcpy.AddMessage("All Required Fields are available in Gravel_Maint Table")
            if f[3] != []:
                messages.addErrorMessage("Fields and/or missed in Gravel_Maint Table = {0}".format(f[3]))

            if f[4] == []:
                arcpy.AddMessage("All Required Fields are available in LargeBlock_Maint Table")
            if f[4] != []:
                messages.addErrorMessage("Fields and/or missed in LargeBlock_Maint Table = {0}".format(f[4]))







            arcpy.AddMessage(
                "For further info,contact\n Mr.Yonas Abate ... Mobile:(+251)0933266518 ... Dire ULGDP \n Mr.Binyam G/Tensay ... Mobile:(+251)0930102024 ... DDUPRP \n Mr.Nur Yahya ... Mobile:(+251)0982024688 ... The Developer \n Dire Dawa \n ETHIOPIA")
            time.sleep(5)
            arcpy.AddMessage("Dire ULGDP : All Done")
            arcpy.ResetProgressor()
        main()



class GPS_To_Road_Maintainance(object):
    """ Before executing this tool Run 'Validate_Fields_and_Types'
     Enhanced in Bishoftu ..COVID"""
    def __init__(self):
        self.label="STEP 2 : Load GPS Data To Child Tables"
        self.description="This tool is used to update AMP Road Maintenance condition GDB tables ." + \
                         "The update procedure is inline with the GIS Application Manual " + \
                         "for the revised ULGDP Asset Management Plan."
        self.canRunInBackground=False
        self.category="AMP-ANALYSIS"

    def getParameterInfo(self):
        '''The NNNNNNNNNNNN'''
        # Define parameter definitions

        # Input Features parameter
        gdbFullPath=arcpy.Parameter(
            displayName="ULGDP: AMP File Geodatabase",
            name="in_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input")
        in_features=arcpy.Parameter(
            displayName="ULGDP: AMP Road Feature Class",
            name="in_features_road",
            datatype="Feature Class",
            parameterType="Required",
            direction="Input")

        in_features2=arcpy.Parameter(
            displayName="ULGDP: AMP The GPS Feature Class",
            name="in_features_gps",
            datatype="Feature Class",
            parameterType="Required",
            direction="Input")
        in_features3=arcpy.Parameter(
            displayName="ULGDP: GPS Accuracy Value in Meters",
            name="GPS_Accuracy",
            datatype="Double",
            parameterType="Required",
            direction="Input")

        in_features4=arcpy.Parameter(
            displayName="ULGDP: GeoStat Summary Tables and Graphs",
            name="Stat_sum_plot",
            datatype="Boolean",
            parameterType="Optional",
            direction="Input")

        out_features=arcpy.Parameter(
            displayName="Output Features Road",
            name="out_features_road",
            datatype="Feature Class",
            parameterType="Derived",
            direction="Output")
        out_features2=arcpy.Parameter(
            displayName="Output Features GPS",
            name="out_features_gps",
            datatype="Feature Class",
            parameterType="Derived",
            direction="Output")
        # Required  Vs Output is ---> The user will select the location of the Output
        # Drived Vs Output is ------> Is For Modification
        out_features.parameterDependencies=[in_features.name]
        out_features2.parameterDependencies=[in_features2.name]
        # out_features.schema.clone = True

        parameters=[gdbFullPath, in_features, out_features, in_features2, out_features2, in_features3, in_features4]

        return parameters

    def isLicensed(self):  # optional
        return True

    def updateMessages(self, parameters):  # optional
        return

    def execute(self, parameters, messages):
        readTime=2.5  # Pause to read what's written on dialog

        messages.AddMessage(os.getenv("username") + " Welcome To ArcEthio Tools")
        time.sleep(readTime)

        arcpy.SetProgressorLabel("You are running ArcEthio Dire Toolsets")
        time.sleep(readTime)

        def pathAssignment(parameters):
            gdbFullPath=parameters[0].valueAsText
            fc_ln=parameters[1].valueAsText
            fc_pt=parameters[3].valueAsText
            gps_acc=parameters[5].valueAsText
            I_need_GeoStat=parameters[6].valueAsText

            mytable=gdbFullPath + "/" + "Asphalt_Valuation"
            mytable1=gdbFullPath + "/" + "Asphalt_Maintcondition"
            mytable2=gdbFullPath + "/" + "Cobble_Valuation"
            mytable3=gdbFullPath + "/" + "Cobble_Maintcondition"
            mytable4=gdbFullPath + "/" + "EarthRoad_Valuation"
            mytable5=gdbFullPath + "/" + "Earth_Road_Maintcondition"
            mytable6=gdbFullPath + "/" + "Gravel_Redash_valuation"
            mytable7=gdbFullPath + "/" + "Gravel_Redash_Maintcondition"
            mytable8=gdbFullPath + "/" + "Large_Block_Stone_Valuation"
            mytable9=gdbFullPath + "/" + "Large_Block_Stone_Maintcond"
            mytable10=gdbFullPath + "/" + "Road_Physical"

            dirName=os.path.dirname(gdbFullPath)  # ......... index = 13

            # If u want to create a new file in dirName, FullPath_of _ne = os.path.join(dirName,basename)

            pathParameter=[gdbFullPath, fc_ln, mytable, mytable1, mytable2, mytable3, mytable4, mytable5, mytable6,
                           mytable7, mytable8, mytable9, mytable10, dirName, fc_pt, gps_acc, I_need_GeoStat]
            return pathParameter

        def AccessoryAssignment(pathParameter):  # DETERIORATION Deterioration
            import re

            ws=pathParameter[0]
            arcpy.env.workspace=ws
            arcpy.env.overwriteOutput=True

            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]
            listT1=arcpy.ListFields(Asphalt_Maint)  # ... Asphalt_Maintenance Condition
            listT2=arcpy.ListFields(Cobble_Maint)  # ... Cobble_Maintenance Condition  ###
            listT3=arcpy.ListFields(Earth_Maint)  # ... Earthen_Maintenance Condition
            listT4=arcpy.ListFields(Gravel_Maint)  # ... Gravel_Maintenance Condition
            listT5=arcpy.ListFields(LargeBlock_Maint)  # ... LargeStone_Maintenance Condition  ###
            uneditables1=[f.name for f in listT1 if re.search('^Shape',
                                                              f.name)]  # Uneditable geometry fields name lists  in Asphalt_Maintenance Condition
            uneditables2=[f.name for f in listT2 if re.search('^Shape',
                                                              f.name)]  # Uneditable geometry fields name lists  in Cobble_Maintenance Condition
            uneditables3=[f.name for f in listT3 if re.search('^Shape',
                                                              f.name)]  # Uneditable geometry fields name lists  in Earthen_Maintenance Condition
            uneditables4=[f.name for f in listT4 if re.search('^Shape',
                                                              f.name)]  # Uneditable geometry fields name lists  in Gravel_Maintenance Condition
            uneditables5=[f.name for f in listT5 if re.search('^Shape',
                                                              f.name)]  # Uneditable geometry fields name lists  in LargeStone_Maintenance Condition

            # Assign Default Value = 0 for all Double Fields of all Maintenance Tables except Geometry field
            for f1 in listT1:
                if f1.type == 'Double' and f1.name not in uneditables1:
                    arcpy.AssignDefaultToField_management(Asphalt_Maint, f1.name, default_value=0)
            for f2 in listT2:
                if f2.type == 'Double' and f2.name not in uneditables2:
                    arcpy.AssignDefaultToField_management(Cobble_Maint, f2.name, default_value=0)
            for f3 in listT3:
                if f3.type == 'Double' and f3.name not in uneditables3:
                    arcpy.AssignDefaultToField_management(Earth_Maint, f3.name, default_value=0)
            for f4 in listT4:
                if f4.type == 'Double' and f4.name not in uneditables4:
                    arcpy.AssignDefaultToField_management(Gravel_Maint, f4.name, default_value=0)
            for f5 in listT5:
                if f5.type == 'Double' and f5.name not in uneditables5:
                    arcpy.AssignDefaultToField_management(LargeBlock_Maint, f5.name, default_value=0)

            # Add Field
            listFields1=arcpy.ListFields(Asphalt_Maint)
            fNamesA=[]
            for field in listFields1:
                fNamesA.append(str(field.name))
            fld="DETER_CODE"
            # fld2 = "COUNT_CRACK"
            # fld3 = "COUNT_PEEL"
            # fld4 = "COUNT_POTHOLE"
            # fld5 = "COUNT_ALL_DETER"

            if fld not in fNamesA:
                arcpy.AddField_management(Asphalt_Maint, fld, "TEXT")
            # if fld2 not in fNamesA:
            #     arcpy.AddField_management(Asphalt_Maint, fld2, "DOUBLE")
            # if fld3 not in fNamesA:
            #     arcpy.AddField_management(Asphalt_Maint, fld3, "DOUBLE")
            # if fld4 not in fNamesA:
            #     arcpy.AddField_management(Asphalt_Maint, fld4, "DOUBLE")
            # if fld5 not in fNamesA:
            #     arcpy.AddField_management(Asphalt_Maint, fld5, "DOUBLE")

            # Add field for cobble Road
            listFields2=arcpy.ListFields(Cobble_Maint)
            fNamesB=[]
            for field in listFields2:
                fNamesB.append(str(field.name))
            fld="DETER_CODE"

            if fld not in fNamesB:
                arcpy.AddField_management(Cobble_Maint, fld, "TEXT")

            # Add field for Earth_Maint
            listFields3=arcpy.ListFields(Earth_Maint)
            fNamesC=[]
            for field in listFields3:
                fNamesC.append(str(field.name))
            fld="DETER_CODE"

            if fld not in fNamesC:
                arcpy.AddField_management(Earth_Maint, fld, "TEXT")

            # Add field for Gravel_Maint
            listFields4=arcpy.ListFields(Gravel_Maint)
            fNamesD=[]
            for field in listFields4:
                fNamesD.append(str(field.name))
            fld="DETER_CODE"

            if fld not in fNamesD:
                arcpy.AddField_management(Gravel_Maint, fld, "TEXT")

            # Add field for LargeBlock_Maint
            listFields5=arcpy.ListFields(LargeBlock_Maint)
            fNamesE=[]
            for field in listFields5:
                fNamesE.append(str(field.name))
            fld="DETER_CODE"

            if fld not in fNamesE:
                arcpy.AddField_management(LargeBlock_Maint, fld, "TEXT")

        def GPS_To_Geometry(pathParameter):

            sr=arcpy.SpatialReference(20137)  # Adindan_UTM_Zone37N
            ws=pathParameter[0]
            arcpy.env.workspace=ws
            arcpy.env.overwriteOutput=True
            fc_ln=pathParameter[1]  # The Road Line Input
            fc_pt=pathParameter[14]  # The GPS Point Input
            gps_accuracy=pathParameter[15]  # The GPS Point Input
            fc_pt_xy_to_line=os.path.join(ws, "Near_5m_dist")
            fc_pt_xy_to_line_joined=os.path.join(ws, "Near_5m_dist_joined")
            Maintenance_data=os.path.join(ws, "Maintenance_info")

            # Add  Geoometric Attributes to Both# Road
            arcpy.AddGeometryAttributes_management(fc_ln, Geometry_Properties="LINE_START_MID_END",
                                                   Length_Unit="METERS", Area_Unit="SQUARE_METERS",
                                                   Coordinate_System=sr)
            arcpy.AddGeometryAttributes_management(fc_pt, Geometry_Properties="POINT_X_Y_Z_M", Length_Unit="METERS",
                                                   Area_Unit="SQUARE_METERS", Coordinate_System=sr)

            # Conduct Near Analyis #
            arcpy.Near_analysis(fc_pt, fc_ln, gps_accuracy, location="LOCATION", angle="ANGLE", method="PLANAR")
            # Field list of the input GPS point feature = fields_fc_pt
            fields_fc_pt=['OBJECTID', 'SURFACE_CODE', 'DETERIORATION', 'LENGTH_M', 'WIDTH_M', 'POINT_X', 'POINT_Y',
                          'NEAR_FID', 'NEAR_DIST', 'NEAR_X', 'NEAR_Y']

            listFields=arcpy.ListFields(fc_pt)
            fNames=[]
            for field in listFields:
                fNames.append(field.name)
            fld="ID_TO_ID"

            if fld not in fNames:
                arcpy.AddField_management(fc_pt, "ID_TO_ID", "TEXT")

            fields_fc_pt=['OBJECTID', 'SURFACE_CODE', 'DETERIORATION', 'LENGTH_M', 'WIDTH_M', 'POINT_X', 'POINT_Y',
                          'NEAR_FID', 'NEAR_DIST', 'NEAR_X', 'NEAR_Y', 'ID_TO_ID']
            f=["OBJECTID", "ID_TO_ID"]
            # Populate the ID_TO_ID Field with OBJECTID
            cursor=arcpy.da.UpdateCursor(fc_pt, f)
            for row in cursor:
                row[1]=row[0]
                cursor.updateRow(row)
            del cursor

            # Make Feature Layewr where NEAR_X not equal to -1
            # ie all points that are not within 5 m search radious will be excluded #
            fc_pt_FeatureLayer="fc_pt_within5M"
            wrc=""" NEAR_X <> -1  """
            arcpy.MakeFeatureLayer_management(fc_pt, fc_pt_FeatureLayer, wrc)

            arcpy.XYToLine_management(fc_pt_FeatureLayer, fc_pt_xy_to_line, fields_fc_pt[5], fields_fc_pt[6],
                                      fields_fc_pt[9], fields_fc_pt[10], line_type="NORMAL_SECTION",
                                      id_field=fields_fc_pt[11])

            # match_option = "INTERSECT"  # if not try CLOSEST    BOUNDARY_TOUCHES
            arcpy.SpatialJoin_analysis(target_features=fc_pt_xy_to_line, join_features=fc_ln,
                                       out_feature_class=fc_pt_xy_to_line_joined, join_operation="JOIN_ONE_TO_ONE",
                                       join_type="KEEP_ALL", match_option="INTERSECT")

            # match_option = "INTERSECT"  # if not try CLOSEST    BOUNDARY_TOUCHES
            arcpy.SpatialJoin_analysis(target_features=fc_pt_xy_to_line_joined, join_features=fc_pt,
                                       out_feature_class=Maintenance_data, join_operation="JOIN_ONE_TO_ONE",
                                       join_type="KEEP_ALL", match_option="INTERSECT")

        def Create_AreaFields(pathParameter):
            '''Create Area Fields for each Child Tables '''
            gdb_fullPath=pathParameter[0]
            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]

            arcpy.env.workspace = gdb_fullPath

            #------------------------------------------------------------------

            listFields = arcpy.ListFields(Asphalt_Maint)
            fNames = []
            for field in listFields:
                fNames.append(str(field.name))
            fld = 'Area_Cracking'
            fld2 = 'Area_Peeling'
            fld3 = 'Area_Potholes'

            if fld not in fNames:
                arcpy.AddField_management(Asphalt_Maint, fld, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(Asphalt_Maint, fld2, "DOUBLE")
            if fld3 not in fNames:
                arcpy.AddField_management(Asphalt_Maint, fld3, "DOUBLE")

            #-------------------------------------------------------------------

            listFieldsc = arcpy.ListFields(Cobble_Maint)
            fNamesc = []
            for field in listFieldsc:
                fNamesc.append(str(field.name))
            fldc = 'Area_Lifting'
            fldc2 = 'Area_Depression'
            fldc3 = 'Area_Edging_Failure'

            if fldc not in fNamesc:
                arcpy.AddField_management(Cobble_Maint, fldc, "DOUBLE")
            if fldc2 not in fNamesc:
                arcpy.AddField_management(Cobble_Maint, fldc2, "DOUBLE")
            if fldc3 not in fNamesc:
                arcpy.AddField_management(Cobble_Maint, fldc3, "DOUBLE")

            #-------------------------------------------------------------------
            listFields = arcpy.ListFields(Earth_Maint)
            fNames = []
            for field in listFields:
                fNames.append(str(field.name))
            fld = 'Area_Potholes'
            fld2 = 'Area_Washing'

            if fld not in fNames:
                arcpy.AddField_management(Earth_Maint, fld, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(Earth_Maint, fld2, "DOUBLE")

            #-------------------------------------------------------------------

            listFields = arcpy.ListFields(Gravel_Maint)
            fNames = []
            for field in listFields:
                fNames.append(str(field.name))
            fld = 'Area_Potholes'
            fld2 = 'Area_Washing'
            fld3 = 'Area_Channeling'

            if fld not in fNames:
                arcpy.AddField_management(Gravel_Maint, fld, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(Gravel_Maint, fld2, "DOUBLE")
            if fld3 not in fNames:
                arcpy.AddField_management(Gravel_Maint, fld3, "DOUBLE")
            #-------------------------------------------------------------------

            listFields = arcpy.ListFields(LargeBlock_Maint)
            fNames = []
            for field in listFields:
                fNames.append(str(field.name))
            fld = 'Area_Lifting'
            fld2 = 'Area_Depression'

            if fld not in fNames:
                arcpy.AddField_management(LargeBlock_Maint, fld, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(LargeBlock_Maint, fld2, "DOUBLE")
            #-------------------------------------------------------------------














        def Poulate_AreaFields_To_Zero(pathParameter):

            gdb_fullPath=pathParameter[0]
            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]

            arcpy.env.workspace = gdb_fullPath


            # Poulate zero  ----------------------------------------------------------------------------------

            fieldName= ["Area_Cracking","Area_Peeling","Area_Potholes"]
            with arcpy.da.UpdateCursor(Asphalt_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[0] != 0:
                        row[0]= 0
                    if row[1] != 0:
                        row[1]=0
                    if row[2] != 0:
                        row[2]=0
                    cursor.updateRow(row)


            fieldName= ["Area_Lifting","Area_Depression","Area_Edging_Failure"]
            with arcpy.da.UpdateCursor(Cobble_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[0] != 0:
                        row[0]= 0
                    if row[1] != 0:
                        row[1]=0
                    if row[2] != 0:
                        row[2]=0
                    cursor.updateRow(row)

            fieldName= ["Area_Potholes","Area_Washing"]
            with arcpy.da.UpdateCursor(Earth_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[0] != 0:
                        row[0]= 0
                    if row[1] != 0:
                        row[1]=0
                    cursor.updateRow(row)

            fieldName= ["Area_Potholes","Area_Washing","Area_Channeling"]
            with arcpy.da.UpdateCursor(Gravel_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[0] != 0:
                        row[0]= 0
                    if row[1] != 0:
                        row[1]=0
                    if row[2] != 0:
                        row[2]=0
                    cursor.updateRow(row)

            fieldName= ["Area_Lifting","Area_Depression"]
            with arcpy.da.UpdateCursor(LargeBlock_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[0] != 0:
                        row[0]= 0
                    if row[1] != 0:
                        row[1]=0
                    cursor.updateRow(row)



        def GPS_to_ChildTables(pathParameter):

            sr=arcpy.SpatialReference(20137)  # Adindan_UTM_Zone37N
            ws=pathParameter[0]
            dirPath=pathParameter[13]
            arcpy.env.workspace=ws
            arcpy.env.overwriteOutput=True
            fc_ln=pathParameter[1]  # The Road Line Input
            fc_pt=pathParameter[14]  # The GPS Point Input
            gps_accuracy=pathParameter[15]  # The GPS Point Input
            fc_pt_xy_to_line=os.path.join(ws, "Near_5m_dist")
            fc_pt_xy_to_line_joined=os.path.join(ws, "Near_5m_dist_joined")
            Maintenance_data=os.path.join(ws, "Maintenance_info")

            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]

            wrc_asphalt=""" SURFACE_CODE = 'AR'  """  # Aspahlt
            wrc_cobble=""" SURFACE_CODE = 'CR'  """  # Cobble
            wrc_earth=""" SURFACE_CODE = 'ER'  """  # Earth Compact
            wrc_gravel=""" SURFACE_CODE = 'GR'  """  # Gravel
            wrc_largeblock=""" SURFACE_CODE = 'LR'  """  # Large Block Stone Road

            # Workinw with ASPHALT ONLY POTHOLE,LIFTING,DEPRESSION,CRACKING,CHANNELING,EDGE FAILURE,PEELING
            # WASH AWAY,#

            # ...................................ASPHALT_ONLY.................########################################################....Area_Cracking
            arcpy.MakeFeatureLayer_management(Maintenance_data, "ASPHALT_ONLY", wrc_asphalt)

            # ASPHALT_ONLY ...... Cracking

            Asphalt_cracking=os.path.join(ws,
                                          "Asphalt_only_cracking")  # ======================================================================================================================================== 1
            wrc_cracking_only=""" DETERIORATION = 'Cracking'  """  # Asphalt Only ... Deter Cracking

            arcpy.MakeFeatureLayer_management("ASPHALT_ONLY", "ASPHALT_CRACKING", wrc_cracking_only)

            arcpy.Statistics_analysis("ASPHALT_CRACKING", Asphalt_cracking, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................ASPHALT_ONLY...........................###############################################.....Area_Peeling

            # ASPHALT_ONLY ...... Peeling

            Asphalt_peeling=os.path.join(ws, "Asphalt_only_peeling")
            wrc_peeling_only=""" DETERIORATION = 'Peeling'  """  # Asphalt Only ... Deter Peeling
            wrc_Potholes_only=""" DETERIORATION = 'Potholes'  """  # Asphalt Only ... Deter Potholes

            arcpy.MakeFeatureLayer_management("ASPHALT_ONLY", "ASPHALT_PEELING", wrc_peeling_only)
            arcpy.Statistics_analysis("ASPHALT_PEELING", Asphalt_peeling, [["AREA_SQM", "SUM"]], "Route_id")  # r 212

            # ...................................ASPHALT_ONLY...........................#######################################........Area_Potholes

            # ASPHALT_ONLY ...... Potholes

            Asphalt_potholes=os.path.join(ws, "Asphalt_only_potholes")
            wrc_Potholes_only=""" DETERIORATION = 'Potholes'  """  # Asphalt Only ... Deter Potholes

            arcpy.MakeFeatureLayer_management("ASPHALT_ONLY", "ASPHALT_POTHOLE", wrc_Potholes_only)

            arcpy.Statistics_analysis("ASPHALT_POTHOLE", Asphalt_potholes, [["AREA_SQM", "SUM"]], "Route_id")  # r 212

            # ...................................COBBLE_ONLY...........................CCCCCCCCCCCCCCCCCCCCCCCCCC................... Area_Lifting

            arcpy.MakeFeatureLayer_management(Maintenance_data, "COBBLE_ONLY", wrc_cobble)

            # COBBLE_ONLY ...... Lifting

            Cobble_lifting=os.path.join(ws, "Cobble_only_lifting")
            wrc_lifting_only=""" DETERIORATION = 'Lifting'  """  # Cobble Only ... Deter Lifting

            arcpy.MakeFeatureLayer_management("COBBLE_ONLY", "COBBLE_LIFTING", wrc_lifting_only)

            arcpy.Statistics_analysis("COBBLE_LIFTING", Cobble_lifting, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................COBBLE_ONLY........................... Depression

            # COBBLE_ONLY ...... Depression

            Cobble_Depression=os.path.join(ws, "Cobble_only_Depression")
            wrc_Depression_only=""" DETERIORATION = 'Depression'  """  # Cobble Only ... Deter Depression

            arcpy.MakeFeatureLayer_management("COBBLE_ONLY", "COBBLE_DEP", wrc_Depression_only)

            arcpy.Statistics_analysis("COBBLE_DEP", Cobble_Depression, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................COBBLE_ONLY........................... Edging_Failure EdgF

            # COBBLE_ONLY ...... Edging_Failure

            Cobble_Edging_Failure=os.path.join(ws, "Cobble_only_Edging_Failure")
            wrc_Edging_Failure_only=""" DETERIORATION = 'Edging_Failure'  """  # Cobble Only ... Deter Edging Failure

            arcpy.MakeFeatureLayer_management("COBBLE_ONLY", "COBBLE_EDGINGFAIL", wrc_Edging_Failure_only)

            arcpy.Statistics_analysis("COBBLE_EDGINGFAIL", Cobble_Edging_Failure, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................EARTH_ONLY........................... Potholes

            arcpy.MakeFeatureLayer_management(Maintenance_data, "EARTH_ONLY", wrc_earth)

            # EARTH_ONLY ...... Potholes

            Earth_Pothole=os.path.join(ws, "Earth_only_Pothole")
            wrc_pothole_only=""" DETERIORATION = 'Potholes'  """  # Earth Only ... Deter Lifting

            arcpy.MakeFeatureLayer_management("EARTH_ONLY", "EARTH_POTHOLES", wrc_pothole_only)

            arcpy.Statistics_analysis("EARTH_POTHOLES", Earth_Pothole, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................EARTH_ONLY........................... Washing

            # EARTH_ONLY ...... Washing

            Earth_Washing=os.path.join(ws, "Earth_only_Washing")
            wrc_Washing_only=""" DETERIORATION = 'Washing'  """  # Earth Only ... Deter Washing

            arcpy.MakeFeatureLayer_management("EARTH_ONLY", "EARTH_WASHING", wrc_Washing_only)

            arcpy.Statistics_analysis("EARTH_WASHING", Earth_Washing, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................GRAVEL_ONLY........................... Area_Washing
            # *******************************************************************************8

            arcpy.MakeFeatureLayer_management(Maintenance_data, "GRAVEL_ONLY", wrc_gravel)

            # GRAVEL_ONLY ...... Washing

            Gravel_Washing=os.path.join(ws, "Gravel_only_Washing")
            wrc_Washing_only_G=""" DETERIORATION = 'Washing'  """  # Earth Only ... Deter Washing

            arcpy.MakeFeatureLayer_management("GRAVEL_ONLY", "GRAVEL_WASHING", wrc_Washing_only_G)

            arcpy.Statistics_analysis("GRAVEL_WASHING", Gravel_Washing, [["AREA_SQM", "SUM"]], "Route_id")
            # ...................................GRAVEL_ONLY........................... Area_Potholes
            # GRAVEL_ONLY ...... Washing

            Gravel_Potholes=os.path.join(ws, "Gravel_only_Potholes")
            wrc_Washing_only_P=""" DETERIORATION = 'Potholes'  """  # Earth Only ... Deter Washing

            arcpy.MakeFeatureLayer_management("GRAVEL_ONLY", "GRAVEL_PATHOLE", wrc_Washing_only_P)

            arcpy.Statistics_analysis("GRAVEL_PATHOLE", Gravel_Potholes, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................GRAVEL_ONLY........................... Area_Channeling
            # GRAVEL_ONLY ...... Area_Channeling

            Gravel_Channeling=os.path.join(ws, "Gravel_only_Channeling")
            wrc_CH_only_CC=""" DETERIORATION = 'Channeling'  """  # Gravel ... Deter Area_Channeling

            arcpy.MakeFeatureLayer_management("GRAVEL_ONLY", "GRAVEL_CH", wrc_CH_only_CC)

            arcpy.Statistics_analysis("GRAVEL_CH", Gravel_Channeling, [["AREA_SQM", "SUM"]], "Route_id")

            # ------------------------------------------------------------------------------------------------------

            arcpy.MakeFeatureLayer_management(Maintenance_data, "LARGEBLOCK_ONLY",
                                              wrc_largeblock)  # XXXXXXXXXXXXXXXXXXXXXXXXX

            BargeBlock_Lifting=os.path.join(ws,
                                            "LargeBlock_only_Lifting")  # 00000000000000000000000000000000000000000000000000000000000000000000000000000000000
            wrc_LB_only_CC=""" DETERIORATION = 'Lifting'  """  # Gravel ... Deter Area_Channeling

            arcpy.MakeFeatureLayer_management("LARGEBLOCK_ONLY", "LB_LIFTING", wrc_LB_only_CC)

            arcpy.Statistics_analysis("LB_LIFTING", BargeBlock_Lifting, [["AREA_SQM", "SUM"]], "Route_id")

            # ...................................LARGEBLOCK_ONLY........................... Area_Depression

            BargeBlock_Depression=os.path.join(ws, "LargeBlock_only_Depression")
            wrc_LB_only_DEP=""" DETERIORATION = 'Depression'  """  # Gravel ... Deter Area_Channeling

            arcpy.MakeFeatureLayer_management("LARGEBLOCK_ONLY", "LB_DEPR", wrc_LB_only_DEP)

            arcpy.Statistics_analysis("LB_DEPR", BargeBlock_Depression, [["AREA_SQM", "SUM"]], "Route_id")

            gps_summary_tables_fullPath_list=[Asphalt_cracking, Asphalt_peeling, Asphalt_potholes, Cobble_lifting,
                                              Cobble_Depression,
                                              Cobble_Edging_Failure, Earth_Pothole, Earth_Washing, Gravel_Washing,
                                              Gravel_Potholes,
                                              Gravel_Channeling, BargeBlock_Lifting, BargeBlock_Depression]
            return gps_summary_tables_fullPath_list

        def Add_and_PopulateField(pathParameter, gps_summary_tables_fullPath_list):
            # Add Field to all Tables in   "gps_summary_tables_fullPath_list"
            for table in gps_summary_tables_fullPath_list:
                arcpy.AddField_management(table, "DET_{0}".format(os.path.basename(table)), "DOUBLE")

            # Copy field Values from "SUM_AREA_SQM" to
            for table in gps_summary_tables_fullPath_list:
                fieldName=["DET_{0}".format(os.path.basename(table)), "SUM_AREA_SQM"]
                with arcpy.da.UpdateCursor(table, fieldName) as cursor:
                    for row in cursor:
                        row[0]=row[1]
                        cursor.updateRow(row)

            gdb_fullPath=pathParameter[0]
            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]

            # ASPHALT

            listFields=arcpy.ListFields(Asphalt_Maint)
            fNames=[]
            for field in listFields:
                fNames.append(field.name)
            fld="GPS_CRACK_UP"
            fld1="GPS_PEEL_UP"
            fld2="GPS_POTHOLE_UP"
            if fld not in fNames:
                arcpy.AddField_management(Asphalt_Maint, fld, "DOUBLE")
            if fld1 not in fNames:
                arcpy.AddField_management(Asphalt_Maint, fld1, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(Asphalt_Maint, fld2, "DOUBLE")

            # COBBLE

            listFields=arcpy.ListFields(Cobble_Maint)
            fNames=[]
            for field in listFields:
                fNames.append(field.name)
            fld="GPS_DEPRESSION_UP"
            fld1="GPS_EDGINGFAIL_UP"
            fld2="GPS_LIFTING_UP"
            if fld not in fNames:
                arcpy.AddField_management(Cobble_Maint, fld, "DOUBLE")
            if fld1 not in fNames:
                arcpy.AddField_management(Cobble_Maint, fld1, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(Cobble_Maint, fld2, "DOUBLE")

            # GRAVEL

            listFields=arcpy.ListFields(Gravel_Maint)
            fNames=[]
            for field in listFields:
                fNames.append(field.name)
            fld="GPS_CHANNALING_UP"
            fld1="GPS_POTHOLE_UP"
            fld2="GPS_WASHING_UP"
            if fld not in fNames:
                arcpy.AddField_management(Gravel_Maint, fld, "DOUBLE")
            if fld1 not in fNames:
                arcpy.AddField_management(Gravel_Maint, fld1, "DOUBLE")
            if fld2 not in fNames:
                arcpy.AddField_management(Gravel_Maint, fld2, "DOUBLE")

            # EARTH
            listFields=arcpy.ListFields(Earth_Maint)
            fNames=[]
            for field in listFields:
                fNames.append(field.name)
            fld="GPS_WASHING_UP"
            fld1="GPS_POTHOLE_UP"
            if fld not in fNames:
                arcpy.AddField_management(Earth_Maint, fld, "DOUBLE")
            if fld1 not in fNames:
                arcpy.AddField_management(Earth_Maint, fld1, "DOUBLE")

            # LARGE BLOCK
            listFields=arcpy.ListFields(LargeBlock_Maint)
            fNames=[]
            for field in listFields:
                fNames.append(field.name)
            fld="GPS_DEPRESSION_UP"
            fld1="GPS_LIFTING_UP"
            if fld not in fNames:
                arcpy.AddField_management(LargeBlock_Maint, fld, "DOUBLE")
            if fld1 not in fNames:
                arcpy.AddField_management(LargeBlock_Maint, fld1, "DOUBLE")

        def JoinGPS_To_MaintTables(pathParameter, gps_summary_tables_fullPath_list):

            gdb_fullPath=pathParameter[0]
            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]

            Asphalt_only_cracking=gps_summary_tables_fullPath_list[
                0]  # Full Path String  = 'D://A_YONAS//SCRIPT_TRY_DATA//SCRIPT_TRY.gdb\\Asphalt_only_cracking'
            Asphalt_only_peeling=gps_summary_tables_fullPath_list[1]
            Asphalt_only_pothole=gps_summary_tables_fullPath_list[2]
            Cobble_only_lifting=gps_summary_tables_fullPath_list[3]
            Cobble_only_depression=gps_summary_tables_fullPath_list[4]
            Cobble_only_edgefailure=gps_summary_tables_fullPath_list[5]
            Earth_only_pothole=gps_summary_tables_fullPath_list[6]
            Earth_only_washing=gps_summary_tables_fullPath_list[7]
            Gravel_only_washing=gps_summary_tables_fullPath_list[8]
            Gravel_only_pothole=gps_summary_tables_fullPath_list[9]
            Gravel_only_channeling=gps_summary_tables_fullPath_list[10]
            LargeBlock_only_lifting=gps_summary_tables_fullPath_list[11]
            LargeBlock_only_depression=gps_summary_tables_fullPath_list[12]

            # Join ASPALT_ONLY_CRACK ----------------------------------------------------------------------------------

            arcpy.JoinField_management(Asphalt_Maint, "Route_id", Asphalt_only_cracking, "Route_id")
            fieldName=["Area_Cracking", "DET_{0}".format(os.path.basename(Asphalt_only_cracking)), "GPS_CRACK_UP",
                       "GPS_PEEL_UP", "GPS_POTHOLE_UP"]
            with arcpy.da.UpdateCursor(Asphalt_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=1  # "GPS_CRACK_UP" = 1
                        row[3]=0  # "GPS_PEEL_UP" = 0
                        row[4]=0  # "GPS_POTHOLE_UP" = 0
                    cursor.updateRow(row)

            # Join ASPALT_ONLY_PEEL ------------------------------------------------------------------------------------------

            arcpy.JoinField_management(Asphalt_Maint, "Route_id", Asphalt_only_peeling, "Route_id")
            fieldName=["Area_Peeling", "DET_{0}".format(os.path.basename(Asphalt_only_peeling)), "GPS_CRACK_UP",
                       "GPS_PEEL_UP", "GPS_POTHOLE_UP"]
            with arcpy.da.UpdateCursor(Asphalt_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_CRACK_UP" = 0
                        row[3]=1  # "GPS_PEEL_UP" = 1
                        row[4]=0  # "GPS_POTHOLE_UP" = 0
                    cursor.updateRow(row)

            # Join ASPALT_ONLY_POTHOLE ------------------------------------------------------------------------------------------

            arcpy.JoinField_management(Asphalt_Maint, "Route_id", Asphalt_only_pothole, "Route_id")
            fieldName=["Area_Potholes", "DET_{0}".format(os.path.basename(Asphalt_only_pothole)), "GPS_CRACK_UP",
                       "GPS_PEEL_UP", "GPS_POTHOLE_UP"]
            with arcpy.da.UpdateCursor(Asphalt_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_CRACK_UP" = 0
                        row[3]=0  # "GPS_PEEL_UP" = 0
                        row[4]=1  # "GPS_POTHOLE_UP" = 1
                    cursor.updateRow(row)

            # Delete the joined Tables

            arcpy.DeleteField_management(Asphalt_Maint, "DET_{0}".format(os.path.basename(Asphalt_only_cracking)))
            arcpy.DeleteField_management(Asphalt_Maint, "DET_{0}".format(os.path.basename(Asphalt_only_peeling)))
            arcpy.DeleteField_management(Asphalt_Maint, "DET_{0}".format(os.path.basename(Asphalt_only_pothole)))

            # Join COBBLE ONLY LIFTING --------------------------------------------------------------------------------

            arcpy.JoinField_management(Cobble_Maint, "Route_id", Cobble_only_lifting, "Route_id")
            fieldName=["Area_Lifting", "DET_{0}".format(os.path.basename(Cobble_only_lifting)), "GPS_LIFTING_UP",
                       "GPS_DEPRESSION_UP", "GPS_EDGINGFAIL_UP"]
            with arcpy.da.UpdateCursor(Cobble_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=1  # "GPS_LIFTING_UP" = 1
                        row[3]=0  # "GPS_DEPRESSION_UP" = 0
                        row[4]=0  # "GPS_EDGINGFAIL_UP" = 0
                    cursor.updateRow(row)


            # Join COBBLE ONLY DEPRESSION ----------------------------------------------------------------------------

            arcpy.JoinField_management(Cobble_Maint, "Route_id", Cobble_only_depression, "Route_id")
            fieldName=["Area_Depression", "DET_{0}".format(os.path.basename(Cobble_only_depression)), "GPS_LIFTING_UP",
                       "GPS_DEPRESSION_UP", "GPS_EDGINGFAIL_UP"]
            with arcpy.da.UpdateCursor(Cobble_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_LIFTING_UP" = 0
                        row[3]=1  # "GPS_DEPRESSION_UP" = 1
                        row[4]=0  # "GPS_EDGINGFAIL_UP" = 0
                    cursor.updateRow(row)


            # Join COBBLE ONLY EDGEFAIL -------------------------------------------------------------------------------

            arcpy.JoinField_management(Cobble_Maint, "Route_id", Cobble_only_edgefailure, "Route_id")
            fieldName=["Area_Edging_Failure", "DET_{0}".format(os.path.basename(Cobble_only_edgefailure)),
                       "GPS_LIFTING_UP",
                       "GPS_DEPRESSION_UP", "GPS_EDGINGFAIL_UP"]
            with arcpy.da.UpdateCursor(Cobble_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_LIFTING_UP" = 0
                        row[3]=0  # "GPS_DEPRESSION_UP" = 0
                        row[4]=1  # "GPS_EDGINGFAIL_UP" = 1
                    cursor.updateRow(row)

            arcpy.DeleteField_management(Cobble_Maint, "DET_{0}".format(os.path.basename(Cobble_only_lifting)))
            arcpy.DeleteField_management(Cobble_Maint, "DET_{0}".format(os.path.basename(Cobble_only_depression)))
            arcpy.DeleteField_management(Cobble_Maint, "DET_{0}".format(os.path.basename(Cobble_only_edgefailure)))


            # Join EARTH ONLY POTHOLE ---------------------------------------------------------------------------------

            arcpy.JoinField_management(Earth_Maint, "Route_id", Earth_only_pothole, "Route_id")
            fieldName=["Area_Potholes", "DET_{0}".format(os.path.basename(Earth_only_pothole)), "GPS_POTHOLE_UP",
                       "GPS_WASHING_UP"]
            with arcpy.da.UpdateCursor(Earth_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=1  # "GPS_POTHOLE_UP" = 1
                        row[3]=0  # "GPS_WASHING_UP" = 0
                    cursor.updateRow(row)


            # Join EARTH ONLY WASHING ---------------------------------------------------------------------------------

            arcpy.JoinField_management(Earth_Maint, "Route_id", Earth_only_washing, "Route_id")
            fieldName=["Area_Washing", "DET_{0}".format(os.path.basename(Earth_only_washing)), "GPS_POTHOLE_UP",
                       "GPS_WASHING_UP"]
            with arcpy.da.UpdateCursor(Earth_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_POTHOLE_UP" = 0
                        row[3]=1  # "GPS_WASHING_UP" = 1
                    cursor.updateRow(row)

            arcpy.DeleteField_management(Earth_Maint, "DET_{0}".format(os.path.basename(Earth_only_pothole)))
            arcpy.DeleteField_management(Earth_Maint, "DET_{0}".format(os.path.basename(Earth_only_washing)))



            # Join GRAVEL ONLY WASHING --------------------------------------------------------------------------------

            arcpy.JoinField_management(Gravel_Maint, "Route_id", Gravel_only_washing, "Route_id")
            fieldName=["Area_Washing", "DET_{0}".format(os.path.basename(Gravel_only_washing)), "GPS_WASHING_UP",
                       "GPS_POTHOLE_UP", "GPS_CHANNALING_UP"]
            with arcpy.da.UpdateCursor(Gravel_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=1  # "GPS_WASHING_UP" = 1
                        row[3]=0  # "GPS_POTHOLE_UP" = 0
                        row[4]=0  # "GPS_CHANNALING_UP" = 0
                    cursor.updateRow(row)


            # Join GRAVEL ONLY POTHOLE --------------------------------------------------------------------------------

            arcpy.JoinField_management(Gravel_Maint, "Route_id", Gravel_only_pothole, "Route_id")
            fieldName=["Area_Potholes", "DET_{0}".format(os.path.basename(Gravel_only_pothole)), "GPS_WASHING_UP",
                       "GPS_POTHOLE_UP", "GPS_CHANNALING_UP"]
            with arcpy.da.UpdateCursor(Gravel_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_WASHING_UP" = 0
                        row[3]=1  # "GPS_POTHOLE_UP" = 1
                        row[4]=0  # "GPS_CHANNALING_UP" = 0
                    cursor.updateRow(row)


            # Join GRAVEL ONLY CHANNALING ---------------------------------------------------------------------------

            arcpy.JoinField_management(Gravel_Maint, "Route_id", Gravel_only_channeling, "Route_id")
            fieldName=["Area_Channeling", "DET_{0}".format(os.path.basename(Gravel_only_channeling)), "GPS_WASHING_UP",
                       "GPS_POTHOLE_UP", "GPS_CHANNALING_UP"]
            with arcpy.da.UpdateCursor(Gravel_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_WASHING_UP" = 0
                        row[3]=0  # "GPS_POTHOLE_UP" = 0
                        row[4]=1  # "GPS_CHANNALING_UP" = 1
                    cursor.updateRow(row)


            arcpy.DeleteField_management(Gravel_Maint, "DET_{0}".format(os.path.basename(Gravel_only_washing)))
            arcpy.DeleteField_management(Gravel_Maint, "DET_{0}".format(os.path.basename(Gravel_only_pothole)))
            arcpy.DeleteField_management(Gravel_Maint, "DET_{0}".format(os.path.basename(Gravel_only_channeling)))

            # Join LARGEBLOCK ONLY LIFTING ----------------------------------------------------------------------------

            arcpy.JoinField_management(LargeBlock_Maint, "Route_id", LargeBlock_only_lifting, "Route_id")
            fieldName=["Area_Lifting", "DET_{0}".format(os.path.basename(LargeBlock_only_lifting)), "GPS_LIFTING_UP",
                       "GPS_DEPRESSION_UP"]
            with arcpy.da.UpdateCursor(LargeBlock_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=1  # "GPS_LIFTING_UP" = 1
                        row[3]=0  # "GPS_DEPRESSION_UP" = 0
                    cursor.updateRow(row)

            # Join LARGEBLOCK ONLY DEPRESSION -------------------------------------------------------------------------

            arcpy.JoinField_management(LargeBlock_Maint, "Route_id", LargeBlock_only_depression, "Route_id")
            fieldName=["Area_Depression", "DET_{0}".format(os.path.basename(LargeBlock_only_depression)),
                       "GPS_LIFTING_UP",
                       "GPS_DEPRESSION_UP"]
            with arcpy.da.UpdateCursor(LargeBlock_Maint, fieldName) as cursor:
                for row in cursor:
                    if row[1] != None:
                        row[0]=row[1]
                        row[2]=0  # "GPS_LIFTING_UP" = 0
                        row[3]=1  # "GPS_DEPRESSION_UP" = 1
                    cursor.updateRow(row)
            arcpy.DeleteField_management(LargeBlock_Maint, "DET_{0}".format(os.path.basename(LargeBlock_only_lifting)))
            arcpy.DeleteField_management(LargeBlock_Maint, "DET_{0}".format(os.path.basename(LargeBlock_only_depression)))



        def Clean_Unnecessary(pathParameter):
            ''' Cleans unnecessay intermediate data and fields'''
            # sr = arcpy.SpatialReference(20137)  # Adindan_UTM_Zone37N
            ws=pathParameter[0]
            arcpy.env.workspace=ws
            arcpy.env.overwriteOutput=True
            # fc_ln = pathParameter[1]  # The Road Line Input
            fc_pt=pathParameter[14]  # The GPS Point Input
            # gps_accuracy = pathParameter[15]  # The GPS Point Input
            fc_pt_xy_to_line=os.path.join(ws, "Near_5m_dist")
            fc_pt_xy_to_line_joined=os.path.join(ws, "Near_5m_dist_joined")
            Maintenance_data=os.path.join(ws, "Maintenance_info")

            L=['POINT_X', 'POINT_Y', 'NEAR_FID', 'NEAR_DIST', 'NEAR_X', 'NEAR_Y', 'NEAR_ANGLE']
            arcpy.DeleteField_management(fc_pt, L)
            Lf=['Join_Count', 'TARGET_FID', 'POINT_X', 'POINT_Y', 'NEAR_X', 'NEAR_Y', 'POINT_X_1', 'POINT_Y_1',
                'NEAR_FID', 'NEAR_DIST', 'NEAR_X_1', 'NEAR_Y_1', 'NEAR_ANGLE']
            arcpy.DeleteField_management(Maintenance_data, Lf)
            arcpy.Delete_management(fc_pt_xy_to_line)
            arcpy.Delete_management(fc_pt_xy_to_line_joined)

        def AssignDeteriorationCode(pathParameter):  # DETERIORATION Deterioration

            ws=pathParameter[0]
            arcpy.env.workspace=ws
            arcpy.env.overwriteOutput=True

            Asphalt_Maint=pathParameter[3]
            Cobble_Maint=pathParameter[5]
            Earth_Maint=pathParameter[7]
            Gravel_Maint=pathParameter[9]
            LargeBlock_Maint=pathParameter[11]

            # Assigning DETERIORATION_CODE for Asphalt_Maint Table ........................@ Asphalt_Maint
            fields_Asphalt_Maint=['Area_Cracking', 'Area_Peeling', 'Area_Potholes', 'DETER_CODE']
            # ............................0................1...............2..............3..............4............5.................6.............7
            cursor=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursor:
                if row[0] == 0 and row[1] == 0 and row[2] == 0:
                    row[3]="ND"
                cursor.updateRow(row)
            del cursor
            cursorP=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorP:
                if row[0] == 0 and row[2] == 0 and row[1] == 0:
                    row[3]="ND"
                cursorP.updateRow(row)
            del cursorP
            cursorQ=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorQ:
                if row[1] == 0 and row[0] == 0 and row[2] == 0:
                    row[3]="ND"
                cursorQ.updateRow(row)
            del cursorQ
            cursorRT=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorRT:
                if row[1] == 0 and row[2] == 0 and row[0] == 0:
                    row[3]="ND"
                cursorRT.updateRow(row)
            del cursorRT
            cursorRM=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorRM:
                if row[2] == 0 and row[1] == 0 and row[0] == 0:
                    row[3]="ND"
                cursorRM.updateRow(row)
            del cursorRM
            cursorRZ=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorRZ:
                if row[2] == 0 and row[0] == 0 and row[1] == 0:
                    row[3]="ND"
                cursorRZ.updateRow(row)
            del cursorRZ

            cursorA=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)

            for row in cursorA:
                if row[0] > 0 and row[1] == 0 and row[2] == 0:
                    row[3]="DETCR_CRACKONLY"
                cursorA.updateRow(row)
            del cursorA
            cursorB=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorB:
                if row[0] == 0 and row[1] > 0 and row[2] == 0:
                    row[3]="DETPE_PEELONLY"
                cursorB.updateRow(row)
            del cursorB
            cursorC=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorC:
                if row[0] == 0 and row[1] == 0 and row[2] > 0:
                    row[3]="DETPO_POTHOLEONLY"
                cursorC.updateRow(row)
            del cursorC
            cursorD=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorD:
                if row[0] > 0 and row[1] > 0 and row[2] == 0:
                    row[3]="DETC1_CRACK+PEEL"
                cursorD.updateRow(row)
            del cursorD
            cursorE=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorE:
                if row[0] == 0 and row[1] > 0 and row[2] > 0:
                    row[3]="DETC2_PEEL+POTHOLE"
                cursorE.updateRow(row)
            del cursorE
            cursorG=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorG:
                if row[0] > 0 and row[1] == 0 and row[2] > 0:
                    row[3]="DETC2_CRACK+POTHOLE"
                cursorG.updateRow(row)
            del cursorG

            cursorF=arcpy.da.UpdateCursor(Asphalt_Maint, fields_Asphalt_Maint)
            for row in cursorF:
                if row[0] > 0 and row[1] > 0 and row[2] > 0:
                    row[3]="DETC3_ALL"
                cursorF.updateRow(row)
            del cursorF

            # Assigning DETERIORATION_CODE for Cobble_Maint Table ........................@ Cobble_Maint
            fields_Cobble_Maint=['Area_Lifting', 'Area_Depression', 'Area_Edging_Failure', 'DETER_CODE']
            cursorAAA=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorAAA:
                if row[0] == 0 and row[1] == 0 and row[2] == 0:  # XXXX
                    row[3]="ND"
                cursorAAA.updateRow(row)
            del cursorAAA
            cursorBBB=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorBBB:
                if row[0] == 0 and row[2] == 0 and row[1] == 0:  # XXXX
                    row[3]="ND"
                cursorBBB.updateRow(row)
            del cursorBBB
            cursorCCC=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorCCC:
                if row[1] == 0 and row[0] == 0 and row[2] == 0:  # XXXX
                    row[3]="ND"
                cursorCCC.updateRow(row)
            del cursorCCC
            cursorDDD=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorDDD:
                if row[1] == 0 and row[2] == 0 and row[0] == 0:  # XXXX
                    row[3]="ND"
                cursorDDD.updateRow(row)
            del cursorDDD
            cursorEEE=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorEEE:
                if row[2] == 0 and row[1] == 0 and row[0] == 0:  # XXXX
                    row[3]="ND"
                cursorEEE.updateRow(row)
            del cursorEEE
            cursorFFF=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorFFF:
                if row[2] == 0 and row[0] == 0 and row[1] == 0:  # XXXX
                    row[3]="ND"
                cursorFFF.updateRow(row)
            del cursorFFF
            cursorGGG=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorGGG:
                if row[0] > 0 and row[1] == 0 and row[2] == 0:  # XXXX
                    row[3]="DETCL_LIFTINGONLY"
                cursorGGG.updateRow(row)
            del cursorGGG
            cursorHHH=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorHHH:
                if row[0] == 0 and row[1] > 0 and row[2] == 0:  # XXXX
                    row[3]="DETCD_DEPRESSIONONLY"
                cursorHHH.updateRow(row)
            del cursorHHH
            cursorIII=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorIII:
                if row[0] == 0 and row[1] == 0 and row[2] > 0:  # XXXX
                    row[3]="DEEF_EDGEFAILUREONLY"
                cursorIII.updateRow(row)
            del cursorIII
            cursorJJJ=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorJJJ:
                if row[0] > 0 and row[1] > 0 and row[2] == 0:  # XXXX
                    row[3]="DELD_LIFTING+DEPRESSION"
                cursorJJJ.updateRow(row)
            del cursorJJJ
            # ['Area_Lifting', 'Area_Depression', 'Area_Edging_Failure', 'DETER_CODE']
            cursorKKK=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorKKK:
                if row[0] == 0 and row[1] > 0 and row[2] > 0:  # XXXX
                    row[3]="DEDE_DEPRESSION+EDGF"
                cursorKKK.updateRow(row)
            del cursorKKK
            cursorLLL=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorLLL:
                if row[0] > 0 and row[1] == 0 and row[2] > 0:  # XXXX
                    row[3]="DELE_LIFTING+EDGF"
                cursorLLL.updateRow(row)
            del cursorLLL
            cursorMMM=arcpy.da.UpdateCursor(Cobble_Maint, fields_Cobble_Maint)
            for row in cursorMMM:
                if row[0] > 0 and row[1] > 0 and row[2] > 0:  # XXXX
                    row[3]="DEAL_ALL"
                cursorMMM.updateRow(row)
            del cursorMMM

            # Assigning DETERIORATION_CODE for Earth_Maint Table ........................@ Earth_Maint..not clear
            fields_Earth_Maint=['Area_Potholes', 'Area_Washing', 'DETER_CODE']
            cursor10=arcpy.da.UpdateCursor(Earth_Maint, fields_Earth_Maint)
            for row in cursor10:
                if row[0] == 0 and row[1] == 0:  # XXXX
                    row[2]="ND"
                cursor10.updateRow(row)
            del cursor10
            cursor11=arcpy.da.UpdateCursor(Earth_Maint, fields_Earth_Maint)
            for row in cursor11:
                if row[1] == 0 and row[0] == 0:  # XXXX
                    row[2]="ND"
                cursor11.updateRow(row)
            del cursor11
            cursor12=arcpy.da.UpdateCursor(Earth_Maint, fields_Earth_Maint)
            for row in cursor12:
                if row[0] > 0 and row[1] == 0:  # XXXX
                    row[2]="PE_POTHOLEONLY"
                cursor12.updateRow(row)
            del cursor12
            cursor13=arcpy.da.UpdateCursor(Earth_Maint, fields_Earth_Maint)
            for row in cursor13:
                if row[0] == 0 and row[1] > 0:  # XXXX
                    row[2]="WA_WASHINGONLY"
                cursor13.updateRow(row)
            del cursor13
            # ['Area_Potholes', 'Area_Washing', 'DETER_CODE']
            cursor14=arcpy.da.UpdateCursor(Earth_Maint, fields_Earth_Maint)
            for row in cursor14:
                if row[0] > 0 and row[1] > 0:  # XXXX
                    row[2]="PEWA_POTHOLE+WASHING_ALL"
                cursor14.updateRow(row)
            del cursor14

            # Assigning DETERIORATION_CODE for Gravel_Maint Table ........................@ Gravel_Maint..
            fields_Gravel_Maint=['Area_Potholes', 'Area_Washing', 'Area_Channeling', 'DETER_CODE']

            cursor20=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursor20:
                if row[0] == 0 and row[1] == 0 and row[2] == 0:  # XXXX
                    row[3]="ND"
                cursor20.updateRow(row)
            del cursor20
            cursor21=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursor21:
                if row[0] == 0 and row[2] == 0 and row[1] == 0:  # XXXX
                    row[3]="ND"
                cursor21.updateRow(row)
            del cursor21
            cursorCCCC=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorCCCC:
                if row[1] == 0 and row[0] == 0 and row[2] == 0:  # XXXX
                    row[3]="ND"
                cursorCCCC.updateRow(row)
            del cursorCCCC
            cursorDDDD=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorDDDD:
                if row[1] == 0 and row[2] == 0 and row[0] == 0:  # XXXX
                    row[3]="ND"
                cursorDDDD.updateRow(row)
            del cursorDDDD
            cursorEEEE=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorEEEE:
                if row[2] == 0 and row[1] == 0 and row[0] == 0:  # XXXX
                    row[3]="ND"
                cursorEEEE.updateRow(row)
            del cursorEEEE
            cursorFFFF=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorFFFF:
                if row[2] == 0 and row[0] == 0 and row[1] == 0:  # XXXX
                    row[3]="ND"
                cursorFFFF.updateRow(row)
            del cursorFFFF
            cursorGGGG=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorGGGG:
                if row[0] > 0 and row[1] == 0 and row[2] == 0:  # XXXX
                    row[3]="PE_POTHOLEONLY"
                cursorGGGG.updateRow(row)
            del cursorGGGG
            cursorHHHH=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorHHHH:
                if row[0] == 0 and row[1] > 0 and row[2] == 0:  # XXXX
                    row[3]="WA_WASHINGONLY"
                cursorHHHH.updateRow(row)
            del cursorHHHH
            cursorIIII=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorIIII:
                if row[0] == 0 and row[1] == 0 and row[2] > 0:  # XXXX
                    row[3]="CH_CHANNELINGONLY"
                cursorIIII.updateRow(row)
            del cursorIIII
            cursorJJJJ=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorJJJJ:
                if row[0] > 0 and row[1] > 0 and row[2] == 0:  # XXXX
                    row[3]="PEWA_POTHOLE+WASHING"
                cursorJJJJ.updateRow(row)
            del cursorJJJJ
            # ['Area_Potholes', 'Area_Washing', 'Area_Channeling', 'DETER_CODE']
            cursorKKKK=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorKKKK:
                if row[0] == 0 and row[1] > 0 and row[2] > 0:  # XXXX
                    row[3]="WACH_WASHING+CHANNELING"
                cursorKKKK.updateRow(row)
            del cursorKKKK
            cursorLLLL=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorLLLL:
                if row[0] > 0 and row[1] == 0 and row[2] > 0:  # XXXX
                    row[3]="CHPE_POTHOLE+CHANNELING"
                cursorLLLL.updateRow(row)
            del cursorLLLL
            cursorMMMM=arcpy.da.UpdateCursor(Gravel_Maint, fields_Gravel_Maint)
            for row in cursorMMMM:
                if row[0] > 0 and row[1] > 0 and row[2] > 0:  # XXXX
                    row[3]="PEWACH_ALL"
                cursorMMMM.updateRow(row)
            del cursorMMMM

            # Assigning DETERIORATION_CODE for LargeBlock_Maint Table ........................@ LargeBlock_Maint..
            fields_LargeBlock_Maint=['Area_Lifting', 'Area_Depression', 'DETER_CODE']

            cursor101=arcpy.da.UpdateCursor(LargeBlock_Maint, fields_LargeBlock_Maint)
            for row in cursor101:
                if row[0] == 0 and row[1] == 0:  # XXXX
                    row[2]="ND"
                cursor101.updateRow(row)
            del cursor101
            cursor112=arcpy.da.UpdateCursor(LargeBlock_Maint, fields_LargeBlock_Maint)
            for row in cursor112:
                if row[1] == 0 and row[0] == 0:  # XXXX
                    row[2]="ND"
                cursor112.updateRow(row)
            del cursor112
            cursor123=arcpy.da.UpdateCursor(LargeBlock_Maint, fields_LargeBlock_Maint)
            for row in cursor123:
                if row[0] > 0 and row[1] == 0:  # XXXX
                    row[2]="DLI_LIFTINGONLY"
                cursor123.updateRow(row)
            del cursor123
            # ['Area_Lifting', 'Area_Depression', 'DETER_CODE']
            cursor134=arcpy.da.UpdateCursor(LargeBlock_Maint, fields_LargeBlock_Maint)
            for row in cursor134:
                if row[0] == 0 and row[1] > 0:  # XXXX
                    row[2]="DDE_DEPRESSIONONLY"
                cursor134.updateRow(row)
            del cursor134
            # ['Area_Potholes', 'Area_Washing', 'DETER_CODE']
            cursor145=arcpy.da.UpdateCursor(LargeBlock_Maint, fields_LargeBlock_Maint)
            for row in cursor145:
                if row[0] > 0 and row[1] > 0:  # XXXX
                    row[2]="PEWA_LIFTING+DEPRESSION_ALL"
                cursor145.updateRow(row)
            del cursor145

        def Summarize_and_Plot(pathParameter):
            pass

        def GetExpiryTime(t_initial_fixed):
            import time
            now=time.time()
            expiry_tics=now - t_initial_fixed
            expiry_inMinutes=expiry_tics / 60
            expiry_inHr=expiry_tics / 3600
            expiry_inDays=expiry_tics / 86400
            expiry_parameter=[expiry_inMinutes, expiry_inHr, expiry_inDays]
            return expiry_parameter

        def main():
            readTime=2.5  # Pause to read what's written on dialog

            arcpy.SetProgressor("default",
                                "Dire Dawa ULGDP - Road Asset Updating Demo GP Tool    : \n  Developed by : Nur Yahya Kedirkhan ,Mobile:(+251)0982024688")
            arcpy.AddMessage("Dear {0}, You are Running Road Asset Updating Demo GP Tool".format(getpass.getuser()))

            time.sleep(5)
            timeBegin=1589389815.82  # Now I was in Bishoftu home REMEDAN... COVID
            t=GetExpiryTime(timeBegin)
            expiry_inDays=t[2]
            # parameters = [gdbFullPath, in_features, out_features, in_features2, out_features2, in_features3,
            #               in_features4]
            if expiry_inDays < 300:

                pp=pathAssignment(parameters)
                Create_AreaFields(pp)
                Poulate_AreaFields_To_Zero(pp) # NEW ... COVID
                AccessoryAssignment(pp)
                GPS_To_Geometry(pp)
                t=GPS_to_ChildTables(pp)
                Add_and_PopulateField(pp, t)
                JoinGPS_To_MaintTables(pp, t)
                AssignDeteriorationCode(pp)
                if pp[16] == True:
                    Summarize_and_Plot(pp)

                Clean_Unnecessary(pp)

                arcpy.AddMessage(
                    "For further info,contact\n Mr.Yonas Abate ... Mobile:(+251)0933266518 ... Dire ULGDP \n Mr.Binyam G/Tensay ... Mobile:(+251)0930102024 ... DDUPRP \n Mr.Nur Yahya ... Mobile:(+251)0982024688 ... The Developer \n Dire Dawa \n ETHIOPIA")
                time.sleep(5)
                arcpy.AddMessage("Dire ULGDP : All Done")
                arcpy.ResetProgressor()
            else:
                raise IOError("The Tool is Expired\nPlease,contact Nur Yahya")

        main()


class CalculateTotalMaintainance(object): # First
    ''' Further enhanced during covid-19 in Bishoft
    Further enhancement on'''

    def __init__(self):
        self.label = "STEP 3 : Calculate Total Maintainance"
        self.description = "Road Asset Data Processing Tool." + \
                           "It used to update Road Asset Data as per GIS Application Manual " + \
                           "for the revised ULGDP Asset Management Plan."
        self.canRunInBackground = False
        self.category = "AMP-ANALYSIS"

    def getParameterInfo(self):
        # Define parameter definitions

        # Input Features parameter
        gdbFullPath = arcpy.Parameter(
            displayName="ULGDP:AMP File Geodatabase",
            name="in_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input")

        parameters = [gdbFullPath]

        return parameters

    def isLicensed(self):  # optional
        return True


    def updateMessages(self, parameters):  # optional
        return

    def execute(self, parameters, messages):
        readTime = 2.5  # Pause to read what's written on dialog

        messages.AddMessage(os.getenv("username") + " welcome to ArcEthio Tools")
        time.sleep(readTime)

        arcpy.SetProgressorLabel("You are running ArcEthio Dire Toolsets")
        time.sleep(readTime)

        def pathAssignment(parameters):

            gdbFullPath = parameters[0].valueAsText
            fc = "parameters[1].valueAsText"

            mytable = gdbFullPath + "/" + "Asphalt_Valuation"
            mytable1 = gdbFullPath + "/" + "Asphalt_Maintcondition"
            mytable2 = gdbFullPath + "/" + "Cobble_Valuation"
            mytable3 = gdbFullPath + "/" + "Cobble_Maintcondition"
            mytable4 = gdbFullPath + "/" + "EarthRoad_Valuation"
            mytable5 = gdbFullPath + "/" + "Earth_Road_Maintcondition"
            mytable6 = gdbFullPath + "/" + "Gravel_Redash_valuation"
            mytable7 = gdbFullPath + "/" + "Gravel_Redash_Maintcondition"
            mytable8 = gdbFullPath + "/" + "Large_Block_Stone_Valuation"
            mytable9 = gdbFullPath + "/" + "Large_Block_Stone_Maintcond"
            mytable10 = gdbFullPath + "/" + "Road_Physical"

            dirName = os.path.dirname(gdbFullPath)  # ......... index = 13


            pathParameter = [gdbFullPath, fc, mytable, mytable1, mytable2, mytable3, mytable4, mytable5, mytable6,
                             mytable7, mytable8, mytable9, mytable10, dirName]
            return pathParameter

        def GetCalculaationField(pathParameter):

            gdbFullPath = pathParameter[0]
            AsphaltMaint = pathParameter[3]
            CobbleMaint = pathParameter[5]
            EarthMaint= pathParameter[7]
            GravelMaint= pathParameter[9]
            LargeBlockMaint= pathParameter[11]




            arcpy.env.workspace = gdbFullPath

            listFields = arcpy.ListFields(AsphaltMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Total_Cost_Cracking"
            fld_name = "Total_Cost_Potholes"  # Carriage_Width Replica
            fld_lname = "Total_Cost_Peeling"
            fld_report = "Tot_Maint_Cost_Bn_Nodes"
            if fld not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_report, "DOUBLE")




            #-----------------------------------------------------------------------------------------------------



            listField_AspahltMaint = ["Area_Cracking","Area_Peeling","Area_Potholes","Unit_Cost_Potholes","Unit_Cost_Peeling","Unit_Cost_Cracking","Total_Cost_Cracking","Total_Cost_Potholes","Total_Cost_Peeling","Tot_Maint_Cost_Bn_Nodes"]


                                          #0              #1              #2                 #3                  #4                   #5                  #6                      #7                  #8                      #9

            cursor = arcpy.da.UpdateCursor(AsphaltMaint,listField_AspahltMaint)
            for row in cursor:
                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                # if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                # if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                # if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                # if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                if row[0]!=0 and   row[0]!= None and row[5]!=0 and   row[5]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[6] = row[0] * row[5] # Total_Cost_Cracking = Area_Cracking * Unit_Cost_Cracking
                if row[1]!=0 and   row[1]!= None and row[4]!=0 and   row[4]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[8] = row[1] * row[4] # Total_Cost_Peeling  = Area_Peeling  * Unit_Cost_Peeling
                if row[2]!=0 and   row[2]!= None and row[3]!=0 and   row[3]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[7] = row[2] * row[3] # Total_Cost_Potholes = Area_Potholes * Unit_Cost_Potholes
                if (row[6] != 0 or row[8] != 0 or row[7] != 0) and (row[6] != None and row[8] != None and row[7] != None):  # ........ SAMPLE SUM..1st
                    row[9] = row[6] + row[8] + row[7]  # Tot_Maint_Cost_Bn_Nodes  =  Total_Cost_Cracking  + Total_Cost_Peeling  + Total_Cost_Potholes
                cursor.updateRow(row)
            del cursor




            listFields = arcpy.ListFields(CobbleMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Total_Cost_Depression"
            fld_name = "Total_Cost_Lifting"  # Carriage_Width Replica
            fld_lname = "Total_Cost_Edgefailour"
            fld_report = "Tot_Maint_Cost_BNnod"
            if fld not in fNames:
                arcpy.AddField_management(CobbleMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_report, "DOUBLE")




            # CobbleMaint_Fields = ["Area_Lifting","Area_Depression","Area_Edging_Failure","Unit_Cost_Lifting",
            #                       "Unit_Cost_Depression","Unit_Cost_Cobedging","Total_Cost_Depression",
            #                       "Total_Cost_Lifting","Total_Cost_Edgefailour","Tot_Maint_Cost_BNnod",
            #                       "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
            #                       "Tot_Deter_Leng_edg_BNnod", "Tot_Leng_dg_BNnod", "Perc_Deter_Edg",
            #                       "Condition_Edgecobble"]

            CobbleMaint_Fields = ["Area_Lifting","Area_Depression","Area_Edging_Failure","Unit_Cost_Lifting",
                                  "Unit_Cost_Depression","Unit_Cost_Cobedging","Total_Cost_Depression",
                                  "Total_Cost_Lifting","Total_Cost_Edgefailour","Tot_Maint_Cost_BNnod"]








            #Tot_Leng_dg_BNnod = Total Edge Length       .... input
            # Tot_Deter_Leng_edg_BNnod = Total Deteriroted edge lengthg..................|
            # Perc_Deter_Edg = deteriroted percentage of edge
            # Condition_Edgecobble = The condition of cobble edge

                                     #0                  #1              #2                    #3                     #4                  #5                       #6                    #7                    #8                     #9
            cursor = arcpy.da.UpdateCursor(CobbleMaint,CobbleMaint_Fields)
            for row in cursor:

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                # if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                # if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                # if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                # if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------


                if row[1]!=0 and   row[1]!= None and row[4]!=0 and   row[4]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[6] = row[1] * row[4]  #            Total_Cost_Depression = Area_Depression * Unit_Cost_Depression
                if row[0]!=0 and   row[0]!= None and row[3]!=0 and   row[3]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[7] = row[0] * row[3]  #            Total_Cost_Lifting  = Area_Lifting * Unit_Cost_Lifting
                if row[2]!=0 and   row[2]!= None and row[5]!=0 and   row[5]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[8] = row[2] * row[5]  #            Total_Cost_Edgefailour = Area_Edging_Failure  *  Unit_Cost_Cobedging
                if (row[6] != 0 or row[7] != 0 or row[8] != 0) and (row[6] != None and row[7] != None and row[8] != None):  # ........ SAMPLE SUM..1st
                    row[9] =  row[6] +  row[7] +  row[8] # Tot_Maint_Cost_BNnod = Total_Cost_Depression + Total_Cost_Lifting + Total_Cost_Edgefailour
                cursor.updateRow(row)
            del cursor



            listFields = arcpy.ListFields(EarthMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Total_Cost_Potholes"
            fld_name = "Total_Cost_Washing"
            fld_lname = "Tot_Maint_Cost_Bn_Nodes"
            if fld not in fNames:
                arcpy.AddField_management(EarthMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(EarthMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(EarthMaint, fld_lname, "DOUBLE")




            EarthMaint_Fields = ["Area_Potholes","Area_Washing","Unit_Cost_Potholes","Unit_Cost_Washing","Total_Cost_Potholes","Total_Cost_Washing","Tot_Maint_Cost_Bn_Nodes"]
                                    #0               #1                    #2              # 3                # 4                   # 5                     #6
            cursor = arcpy.da.UpdateCursor(EarthMaint,EarthMaint_Fields)
            for row in cursor:

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                # if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                # if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                # if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                # if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------


                if row[0]!=0 and   row[0]!= None and row[2]!=0 and   row[2]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[4] = row[0] * row[2]  # Total_Cost_Potholes
                if row[1]!=0 and   row[1]!= None and row[3]!=0 and   row[3]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[5] = row[1] * row[3]  # Total_Cost_Washing

                if (row[4] != 0 or row[5] != 0 ) and (row[4] != None and row[5] != None ):  # ........ SAMPLE SUM..1st
                    row[6] = row[4] + row[5]  # Tot_Maint_Cost_Bn_Nodes
                cursor.updateRow(row)
            del cursor



            listFields = arcpy.ListFields(GravelMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Total_Cost_Washing"
            fld_name = "Total_Cost_Channeling"  # Carriage_Width Replica
            fld_lname = "Total_Cost_Potholes"
            fld_report = "Tot_Maint_Cost_Bn_Nodes"
            if fld not in fNames:
                arcpy.AddField_management(GravelMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(GravelMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(GravelMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(GravelMaint, fld_report, "DOUBLE")






            GravelMaint_Fields = ["Area_Potholes","Area_Washing","Area_Channeling","Unit_Cost_Channeling","Unit_Cost_Washing","Unit_Cost_Potholes","Total_Cost_Washing","Total_Cost_Channeling","Total_Cost_Potholes","Tot_Maint_Cost_Bn_Nodes"]
                                      #0              #1             #2                 #3                     #4                      #5                 #6                  #7                      #8                     #9

            cursor = arcpy.da.UpdateCursor(GravelMaint,GravelMaint_Fields)
            for row in cursor:

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                # if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                # if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                # if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                # if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                if row[1]!=0 and   row[1]!= None and row[4]!=0 and   row[4]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[6] = row[1] * row[4]  # Total_Cost_Washing
                if row[2]!=0 and   row[2]!= None and row[3]!=0 and   row[3]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[7] = row[2] * row[3]  # Total_Cost_Channeling
                if row[0]!=0 and   row[0]!= None and row[5]!=0 and   row[5]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[8] = row[0] * row[5]  # Total_Cost_Potholes
                if (row[6] != 0 or row[7] != 0 or row[8] != 0) and (row[6] != None and row[7] != None and row[8] != None):  # ........ SAMPLE SUM..1st
                    row[9] =  row[6] + row[7] + row[8] # Tot_Maint_Cost_Bn_Nodes
                cursor.updateRow(row)
            del cursor



            listFields = arcpy.ListFields(LargeBlockMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Total_Cost_Lifting"
            fld_name = "Total_Cost_Depression"
            fld_lname = "Tot_Maint_Cost_BNnod"
            if fld not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld_lname, "DOUBLE")





            LargeBlockMaint_Fields = ["Area_Lifting","Area_Depression","Unit_Cost_Lifting","Unit_Cost_Depression","Total_Cost_Lifting","Total_Cost_Depression","Tot_Maint_Cost_BNnod"]
                                         #0             #1                  #2                    #3                      #4                   #5                    #6

            cursor = arcpy.da.UpdateCursor(LargeBlockMaint,LargeBlockMaint_Fields)
            for row in cursor:

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                # if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                # if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                # if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                # if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                if row[0]!=0 and   row[0]!= None and row[2]!=0 and   row[2]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[4] = row[0] * row[2]  # Total_Cost_Lifting
                if row[1]!=0 and   row[1]!= None and row[3]!=0 and   row[3]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[5] = row[1] * row[3]  # Total_Cost_Depression
                if (row[4] != 0 or row[5] != 0 ) and (row[4] != None and row[5] != None ):  # ........ SAMPLE SUM..1st
                    row[6] = row[4] + row[5]  # Tot_Maint_Cost_BNnod
                cursor.updateRow(row)
            del cursor

        def main():
            readTime = 2.5  # Pause to read what's written on dialog

            arcpy.SetProgressor("default",
                                "Dire Dawa ULGDP - Road Asset Updating Demo GP Tool    : \n  Developed by : Nur Yahya Kedirkhan ,Mobile:(+251)0982024688")
            arcpy.AddMessage("Dear {0}, You are Running Road Asset Updating Demo GP Tool".format(getpass.getuser()))

            time.sleep(5)

            pp = pathAssignment(parameters)
            GetCalculaationField(pp)

            arcpy.AddMessage(
                "For further info,contact\n Mr.Yonas Abate ... Mobile:(+251)0933266518 ... Dire ULGDP \n Mr.Binyam G/Tensay ... Mobile:(+251)0930102024 ... DDUPRP \n Mr.Nur Yahya ... Mobile:(+251)0982024688 ... The Developer \n Dire Dawa \n ETHIOPIA")
            time.sleep(5)
            arcpy.AddMessage("Dire ULGDP : All Done")
            arcpy.ResetProgressor()
        main()


class ValuateDeteriorationAndCondition(object): # Second
    ''' Further enhanced during covid-19 in Bishoft
    Further enhancement on '''
    def __init__(self):
        self.label="STEP 4 : Valuate Deterioration and Condition"
        self.description="Road Asset Data Processing Tool." + \
                         "It used to update Road Asset Data as per GIS Application Manual " + \
                         "for the revised ULGDP Asset Management Plan."
        self.canRunInBackground=False
        self.category="AMP-ANALYSIS"

    def getParameterInfo(self):
        # Define parameter definitions

        # Input Features parameter
        gdbFullPath=arcpy.Parameter(
            displayName="ULGDP:AMP File Geodatabase",
            name="in_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input")
        # in_features=arcpy.Parameter(
        #     displayName="ULGDP:AMP Road Feature Class",
        #     name="in_features",
        #     datatype="Feature Class",
        #     parameterType="Required",
        #     direction="Input")
        #
        # out_features=arcpy.Parameter(
        #     displayName="Output Features",
        #     name="out_features",
        #     datatype="Feature Class",
        #     parameterType="Derived",
        #     direction="Output")
        # # Required  Vs Output is ---> The user will select the location of the Output
        # # Drived Vs Output is ------> Is For Modification
        # out_features.parameterDependencies=[in_features.name]
        # out_features.schema.clone = True

        parameters=[gdbFullPath]

        return parameters

    def isLicensed(self):  # optional
        return True

    def updateMessages(self, parameters):  # optional
        return

    def execute(self, parameters, messages):
        readTime=2.5  # Pause to read what's written on dialog

        messages.AddMessage(os.getenv("username") + " welcome to ArcEthio Tools")
        time.sleep(readTime)

        arcpy.SetProgressorLabel("You are running ArcEthio Dire Toolsets")
        time.sleep(readTime)

        def pathAssignment(parameters):

            gdbFullPath=parameters[0].valueAsText
            fc="parameters[1].valueAsText"

            mytable=gdbFullPath + "/" + "Asphalt_Valuation"
            mytable1=gdbFullPath + "/" + "Asphalt_Maintcondition"
            mytable2=gdbFullPath + "/" + "Cobble_Valuation"
            mytable3=gdbFullPath + "/" + "Cobble_Maintcondition"
            mytable4=gdbFullPath + "/" + "EarthRoad_Valuation"
            mytable5=gdbFullPath + "/" + "Earth_Road_Maintcondition"
            mytable6=gdbFullPath + "/" + "Gravel_Redash_valuation"
            mytable7=gdbFullPath + "/" + "Gravel_Redash_Maintcondition"
            mytable8=gdbFullPath + "/" + "Large_Block_Stone_Valuation"
            mytable9=gdbFullPath + "/" + "Large_Block_Stone_Maintcond"
            mytable10=gdbFullPath + "/" + "Road_Physical"

            dirName=os.path.dirname(gdbFullPath)  # ......... index = 13

            pathParameter=[gdbFullPath, fc, mytable, mytable1, mytable2, mytable3, mytable4, mytable5, mytable6,
                           mytable7, mytable8, mytable9, mytable10, dirName]
            return pathParameter


        def GetPercentDeter(pathParameter):

            gdbFullPath = pathParameter[0]
            AsphaltMaint=pathParameter[3]
            CobbleMaint=pathParameter[5]
            EarthMaint=pathParameter[7]
            GravelMaint=pathParameter[9]
            LargeBlockMaint=pathParameter[11]

            # -----------------------------------------------------------------------------------------------------

            arcpy.env.workspace = gdbFullPath

            listFields = arcpy.ListFields(AsphaltMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Tot_Deterior_Area_BNnodes"
            fld_name = "Tot_Area_BNNodes"
            fld_lname = "Percent_Deterioration"
            fld_report = "Condition"
            fld_actual_length = "Actual_Length" # # Actual_Length = Element_Start- Element_End
            if fld not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_report, "TEXT")
            if fld_actual_length not in fNames:
                arcpy.AddField_management(AsphaltMaint, fld_actual_length, "DOUBLE")



            listField_AspahltMaint=["Area_Cracking", "Area_Peeling", "Area_Potholes", "Unit_Cost_Potholes",
                                    "Unit_Cost_Peeling", "Unit_Cost_Cracking", "Total_Cost_Cracking",
                                    "Total_Cost_Potholes", "Total_Cost_Peeling", "Tot_Maint_Cost_Bn_Nodes",
                                    "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration",
                                    "Condition","Actual_Length","Element_Start","Element_End","Width_Element"]
            # 0              #1              #2                 #3                  #4                   #5                  #6                      #7                  #8                      #9                    #### 10                   #### 11              #### 12              ###13

            cursor=arcpy.da.UpdateCursor(AsphaltMaint, listField_AspahltMaint)
            for row in cursor:
                # row[6] = row[0] * row[5] # Total_Cost_Cracking
                # row[8] = row[1] * row[4] # Total_Cost_Peeling
                # row[7] = row[2] * row[3] # Total_Cost_Potholes
                # row[9] = row[6] + row[8] + row[7]

                #UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU
                # BELOW THIS DO SOMETHING ........................ IF NOT NONE

                # All Fields -->("Area_Cracking", "Area_Peeling", "Area_Potholes") must not be ZERO At the same time
                # <Null> Value is not accepted in All Fields -->("Area_Cracking", "Area_Peeling", "Area_Potholes")
                # All Must be populated with numbres
                if (row[0]!=0 or row[1]!=0 or row[2]!=0) and (row[0]!= None and row[1]!= None and row[2]!= None): #........ SAMPLE SUM..1st
                    row[10]=row[0] + row[1] + row[2]  # Tot_Deterior_Area_BNnodes    # "Tot_Deterior_Area_BNnodes"

                # Both "Element_Start" and "Element_End" must not be ZERO at the same time
                if (row[15]!= 0 or row[16]!= 0) and (row[15]!= None and row[16]!= 0): #------------------------------------------SAMPLE MINUS..1st
                    row[14] = abs(row[15] - row[16])  # Actual_Length = Element_Start - Element_End

                if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[11]= row[14]* row[17] # Tot_Area_BNNodes = Actual_Length * Width_Element
                # Since row[11] or  Tot_Area_BNNodes must not be ZERO , the followinf code isneeded
                if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st
                    row[12]=float(row[10] / row[11]) * 100 # Percent_Deterioration =  (Tot_Deterior_Area_BNnodes/Tot_Area_BNNodes)*100
                cursor.updateRow(row)
            del cursor
            # UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU

            listFields = arcpy.ListFields(CobbleMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Tot_Deterior_Area_BNnodes"
            fld_name = "Tot_Area_BNNodes"
            fld_lname = "Percent_Deterioration"
            fld_report = "Condition"
            fld_actual_length = "Actual_Length" # # Actual_Length = Element_Start- Element_End
            f = "Tot_Leng_dg_BNnod" # This is equal to Actual_Length , Actually Unnecessary
            f2 = "Perc_Deter_Edg"
            f3 = "Condition_Edgecobble"
            if fld not in fNames:
                arcpy.AddField_management(CobbleMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_report, "TEXT")
            if fld_actual_length not in fNames:
                arcpy.AddField_management(CobbleMaint, fld_actual_length, "DOUBLE")
            # Tot_Deter_Leng_edg_BNnod      in Cobble ment
            if f not in fNames:
                arcpy.AddField_management(CobbleMaint, f, "DOUBLE")
            if f2 not in fNames:
                arcpy.AddField_management(CobbleMaint, f2, "DOUBLE")
            if f3 not in fNames:
                arcpy.AddField_management(CobbleMaint, f3, "TEXT")

            CobbleMaint_Fields=["Area_Lifting", "Area_Depression", "Area_Edging_Failure", "Unit_Cost_Lifting",
                                "Unit_Cost_Depression", "Unit_Cost_Cobedging", "Total_Cost_Depression",
                                "Total_Cost_Lifting", "Total_Cost_Edgefailour", "Tot_Maint_Cost_BNnod",
                                "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
                                "Tot_Deter_Leng_edg_BNnod","Tot_Leng_dg_BNnod","Perc_Deter_Edg","Condition_Edgecobble",
                                "Actual_Length", "Element_Start", "Element_End", "Width_Element"]
            # 0                  #1              #2                    #3                     #4                  #5                       #6                    #7                    #8                     #9                         ### 10                #### 11              ### 12               ###13
            cursor=arcpy.da.UpdateCursor(CobbleMaint, CobbleMaint_Fields)
            for row in cursor:
                # row[6] = row[1] * row[4]  # Total_Cost_Depression
                # row[7] = row[0] * row[3]  # Total_Cost_Lifting
                # row[8] = row[2] * row[5]  # Total_Cost_Edgefailour
                # row[9] =  row[6] +  row[7] +  row[8] # Tot_Maint_Cost_BNnod
                if (row[19]!= 0 or row[20]!= 0) and (row[19]!= None and row[20]!= 0): #------------------------------------------SAMPLE MINUS
                    row[15] = abs(row[19]-row[20]) # Tot_Leng_dg_BNnod = Element_Start - Element_End  = Actual_Length

                if row[14] != 0 and row[14] != None and row[15]!=0 and row[15]!=None:  # -----------------------------------------------SAMPLE DIVIDE
                    row[16] = float(row[14] / row[15])*100 # Perc_Deter_Edg = Tot_Deter_Leng_edg_BNnod/Tot_Leng_dg_BNnod * 100

                if (row[19]!= 0 or row[20]!= 0) and (row[19]!= None and row[20]!= 0): #------------------------------------------SAMPLE MINUS
                    row[18] = abs(row[19]-row[20]) # Actual_Length = Element_Start - Element_End  = Tot_Leng_dg_BNnod
                if row[18]!= 0 and row[18]!= None and row[21]!= 0 and row[21]!= None :
                    row[11] = row[18] * row[21] # Tot_Area_BNNodes = Actual_Length * Width_Element

                if (row[0]!=0 or row[1]!=0 or row[2]!=0) and (row[0]!= None and row[1]!= None and row[2]!= None): #........ SAMPLE SUM
                    row[10]=row[0] + row[1] + row[2]  # Tot_Deterior_Area_BNnodes

                if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE
                    row[12]=float(row[10] / row[11]) * 100
                cursor.updateRow(row)
            del cursor


            listFields = arcpy.ListFields(EarthMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Tot_Deterior_Area_BNnodes"
            fld_name = "Tot_Area_BNNodes"
            fld_lname = "Percent_Deterioration"
            fld_report = "Condition"
            fld_actual_length = "Actual_Length" # # Actual_Length = Element_Start- Element_End
            if fld not in fNames:
                arcpy.AddField_management(EarthMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(EarthMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(EarthMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(EarthMaint, fld_report, "TEXT")
            if fld_actual_length not in fNames:
                arcpy.AddField_management(EarthMaint, fld_actual_length, "DOUBLE")





            EarthMaint_Fields=["Area_Potholes", "Area_Washing", "Unit_Cost_Potholes", "Unit_Cost_Washing",
                               "Total_Cost_Potholes", "Total_Cost_Washing", "Tot_Maint_Cost_Bn_Nodes",
                               "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
                               "Actual_Length", "Element_Start", "Element_End", "Width_Element"]
            # 0               #1                    #2              # 3                # 4                   # 5                     #6
            cursor=arcpy.da.UpdateCursor(EarthMaint, EarthMaint_Fields)
            for row in cursor:
                # row[4] = row[0] * row[2]  # Total_Cost_Potholes
                # row[5] = row[1] * row[3]  # Total_Cost_Washing
                # row[6] = row[4] + row[5]  # Tot_Maint_Cost_Bn_Nodes
                if (row[0]!=0 or row[1]!=0 ) and (row[0]!= None and row[1]!= None): #........ SAMPLE SUM..1st
                    row[7]=row[0] + row[1]  # Tot_Deterior_Area_BNnodes

                if (row[12]!= 0 or row[13]!= 0) and (row[12]!= None and row[13]!= 0): #------------------------------------------SAMPLE MINUS..1st
                    row[11]=abs(row[12]-row[13]) # Actual_Length = Element_Start - Element_End

                if row[11]!=0 and   row[11]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[8] = row[11]* row[14] # Tot_Area_BNNodes = Actual_Length * Width_Element

                if row[7] != 0 and row[7] != None and row[8]!=0 and row[8]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st
                    row[9]=float(row[7] / row[8]) * 100 # Percent_Deterioration = Tot_Deterior_Area_BNnodes/Tot_Area_BNNodes * 100
                cursor.updateRow(row)
            del cursor



            listFields = arcpy.ListFields(GravelMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Tot_Deterior_Area_BNnodes"
            fld_name = "Tot_Area_BNNodes"
            fld_lname = "Percent_Deterioration"
            fld_report = "Condition"
            fld_actual_length = "Actual_Length" # # Actual_Length = Element_Start- Element_End
            if fld not in fNames:
                arcpy.AddField_management(GravelMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(GravelMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(GravelMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(GravelMaint, fld_report, "TEXT")
            if fld_actual_length not in fNames:
                arcpy.AddField_management(GravelMaint, fld_actual_length, "DOUBLE")



            GravelMaint_Fields=["Area_Potholes", "Area_Washing", "Area_Channeling", "Unit_Cost_Channeling",
                                "Unit_Cost_Washing", "Unit_Cost_Potholes", "Total_Cost_Washing",
                                "Total_Cost_Channeling", "Total_Cost_Potholes", "Tot_Maint_Cost_Bn_Nodes",
                                "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
                                "Actual_Length", "Element_Start", "Element_End", "Width_Element"]
            # 0              #1             #2                 #3                     #4                      #5                 #6                  #7                      #8                     #9                      ####10


            cursor=arcpy.da.UpdateCursor(GravelMaint, GravelMaint_Fields)
            for row in cursor:
                # row[6] = row[1] * row[4]  # Total_Cost_Washing
                # row[7] = row[2] * row[3]  # Total_Cost_Channeling
                # row[8] = row[0] * row[5]  # Total_Cost_Potholes
                # row[9] =  row[6] + row[7] + row[8] # Tot_Maint_Cost_Bn_Nodes

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                #if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                #if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                #if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                #if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                    row[10]=row[0] + row[1] + row[2]  # Tot_Deterior_Area_BNnodes
                if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                    row[14] = abs(row[15]-row[16]) # Actual_Length = Element_Start - Element_End
                if row[14]!=0 and   row[14]!= None and row[17]!=0 and   row[17]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[11] = row[14]* row[17] # Tot_Area_BNNodes = Actual_Length * Width_Element

                if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st
                    row[12]=float(row[10] / row[11]) * 100
                cursor.updateRow(row)
            del cursor



            listFields = arcpy.ListFields(LargeBlockMaint)
            fNames = []
            for field in listFields:
                fNames.append(field.name)
            fld = "Tot_Deterior_Area_BNnodes"
            fld_name = "Tot_Area_BNNodes"
            fld_lname = "Percent_Deterioration"
            fld_report = "Condition"
            fld_actual_length = "Actual_Length" # # Actual_Length = Element_Start- Element_End
            if fld not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld, "DOUBLE")
            if fld_name not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld_name, "DOUBLE")
            if fld_lname not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld_lname, "DOUBLE")
            if fld_report not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld_report, "TEXT")
            if fld_actual_length not in fNames:
                arcpy.AddField_management(LargeBlockMaint, fld_actual_length, "DOUBLE")



            LargeBlockMaint_Fields=["Area_Lifting", "Area_Depression", "Unit_Cost_Lifting", "Unit_Cost_Depression",
                                    "Total_Cost_Lifting", "Total_Cost_Depression", "Tot_Maint_Cost_BNnod",
                                    "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration",
                                    "Condition","Actual_Length", "Element_Start", "Element_End", "Width_Element"]
            # 0             #1                  #2                    #3                      #4                   #5                    #6

            cursor=arcpy.da.UpdateCursor(LargeBlockMaint, LargeBlockMaint_Fields)
            for row in cursor:
                # row[4] = row[0] * row[2]  # Total_Cost_Lifting
                # row[5] = row[1] * row[3]  # Total_Cost_Depression
                # row[6] = row[4] + row[5]  # Tot_Maint_Cost_BNnod

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------

                # if (row[0] != 0 or row[1] != 0 or row[2] != 0) and (row[0] != None and row[1] != None and row[2] != None):  # ........ SAMPLE SUM..1st
                # if (row[15] != 0 or row[16] != 0) and (row[15] != None and row[16] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                # if row[17]!=0 and   row[17]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                # if row[11] != 0 and row[11] != None and row[10]!=0 and row[10]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st

                # ----------- SAMPLE IFs---------------------------------------------------------------------------------------------


                if (row[0] != 0 or row[1] != 0 ) and (row[0] != None and row[1] != None ):  # ........ SAMPLE SUM..1st
                    row[7]=row[0] + row[1]  # Tot_Deterior_Area_BNnodes
                if (row[12] != 0 or row[13] != 0) and (row[12] != None and row[13] != 0):  # ------------------------------------------SAMPLE MINUS..1st
                    row[11] = abs(row[12]-row[13]) # Actual_Length  = Element_Start - Element_End
                if row[11]!=0 and   row[11]!= None and row[14]!=0 and   row[14]!= None:  #.......................................SAMPLE MULTIPLY.1st
                    row[8] = row[11] * row[14] # Tot_Area_BNNodes = Actual_Length * Width_Element

                if row[7] != 0 and row[7] != None and row[8]!=0 and row[8]!=None:  # ----------------------------------------SAMPLE DEVIDE.1st
                    row[9]=float(row[7] / row[8]) * 100 # Percent_Deterioration = Tot_Deterior_Area_BNnodes/Tot_Area_BNNodes * 100
                cursor.updateRow(row)
            del cursor

        def GetDecision(pathParameter):

            AsphaltMaint=pathParameter[3]
            CobbleMaint=pathParameter[5]
            EarthMaint=pathParameter[7]
            GravelMaint=pathParameter[9]
            LargeBlockMaint=pathParameter[11]

            # -----------------------------------------------------------------------------------------------------

            listField_AspahltMaint=["Area_Cracking", "Area_Peeling", "Area_Potholes", "Unit_Cost_Potholes",
                                    "Unit_Cost_Peeling", "Unit_Cost_Cracking", "Total_Cost_Cracking",
                                    "Total_Cost_Potholes", "Total_Cost_Peeling", "Tot_Maint_Cost_Bn_Nodes",
                                    "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration",
                                    "Condition","Actual_Length","Element_Start","Element_End","Width_Element"]








            # listField_AspahltMaint=["Area_Cracking", "Area_Peeling", "Area_Potholes", "Unit_Cost_Potholes",
            #                         "Unit_Cost_Peeling", "Unit_Cost_Cracking", "Total_Cost_Cracking",
            #                         "Total_Cost_Potholes", "Total_Cost_Peeling", "Tot_Maint_Cost_Bn_Nodes",
            #                         "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration",
            #                         "Condition"]
            # 0              #1              #2                 #3                  #4                   #5                  #6                      #7                  #8                      #9                    #### 10                   #### 11              #### 12              ###13

            cursor=arcpy.da.UpdateCursor(AsphaltMaint, listField_AspahltMaint)
            for row in cursor:
                # row[6] = row[0] * row[5] # Total_Cost_Cracking
                # row[8] = row[1] * row[4] # Total_Cost_Peeling
                # row[7] = row[2] * row[3] # Total_Cost_Potholes
                # row[9] = row[6] + row[8] + row[7]

                # row[10] = row[0]+row[1] + row[2] # Tot_Deterior_Area_BNnodes
                # row[12] = float(row[10]/row[11])*100

                if row[12] == 0:
                    row[13]="Very Good"
                elif row[12] > 0 and row[12] <= 5:
                    row[13]="Good"
                elif row[12] > 5 and row[12] <= 20:
                    row[13]="Moderate"
                elif row[12] > 20 and row[12] <= 50:
                    row[13]="Poor"
                elif row[12] > 50:
                    row[13]="Very Poor"
                else:
                    row[13]="Contact Yonas"
                cursor.updateRow(row)
            del cursor

            CobbleMaint_Fields=["Area_Lifting", "Area_Depression", "Area_Edging_Failure", "Unit_Cost_Lifting",
                                "Unit_Cost_Depression", "Unit_Cost_Cobedging", "Total_Cost_Depression",
                                "Total_Cost_Lifting", "Total_Cost_Edgefailour", "Tot_Maint_Cost_BNnod",
                                "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
                                "Tot_Deter_Leng_edg_BNnod","Tot_Leng_dg_BNnod","Perc_Deter_Edg","Condition_Edgecobble",
                                "Actual_Length", "Element_Start", "Element_End", "Width_Element"]



            # CobbleMaint_Fields=["Area_Lifting", "Area_Depression", "Area_Edging_Failure", "Unit_Cost_Lifting",
            #                     "Unit_Cost_Depression", "Unit_Cost_Cobedging", "Total_Cost_Depression",
            #                     "Total_Cost_Lifting", "Total_Cost_Edgefailour", "Tot_Maint_Cost_BNnod",
            #                     "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition","Tot_Deter_Leng_edg_BNnod","Tot_Leng_dg_BNnod","Perc_Deter_Edg","Condition_Edgecobble"]
            # 0                  #1              #2                    #3                     #4                  #5                       #6                    #7                    #8                     #9                         ### 10                #### 11              ### 12               ###13
            cursor=arcpy.da.UpdateCursor(CobbleMaint, CobbleMaint_Fields)
            for row in cursor:
                # row[6] = row[1] * row[4]  # Total_Cost_Depression
                # row[7] = row[0] * row[3]  # Total_Cost_Lifting
                # row[8] = row[2] * row[5]  # Total_Cost_Edgefailour
                # row[9] =  row[6] +  row[7] +  row[8] # Tot_Maint_Cost_BNnod

                # row[10] = row[0]+row[1] + row[2] # Tot_Deterior_Area_BNnodes
                # row[12] = float(row[10]/row[11])*100

                if row[12] == 0:
                    row[13]="Very Good"
                elif row[12] > 0 and row[12] <= 5:
                    row[13]="Good"
                elif row[12] > 5 and row[12] <= 20:
                    row[13]="Moderate"
                elif row[12] > 20 and row[12] <= 50:
                    row[13]="Poor"
                elif row[12] > 50:
                    row[13]="Very Poor"
                else:
                    row[13]="Contact Yonas"

                cursor.updateRow(row)
            del cursor
            # cursor=arcpy.da.UpdateCursor(CobbleMaint, CobbleMaint_Fields)
            # for row in cursor:
            #     row[16] = float(row[14]/row[15])*100
            #     cursor.updateRow(row)
            # del cursor

            cursor=arcpy.da.UpdateCursor(CobbleMaint, CobbleMaint_Fields)
            for row in cursor:
                if row[16] == 0:
                    row[17]="Very Good"
                elif row[16] > 0 and row[16] <= 5:
                    row[17]="Good"
                elif row[16] > 5 and row[16] <= 20:
                    row[17]="Moderate"
                elif row[16] > 20 and row[16] <= 50:
                    row[17]="Poor"
                elif row[16] > 50:
                    row[17]="Very Poor"
                else:
                    row[17]="Contact Yonas"
                cursor.updateRow(row)
            del cursor

            EarthMaint_Fields=["Area_Potholes", "Area_Washing", "Unit_Cost_Potholes", "Unit_Cost_Washing",
                               "Total_Cost_Potholes", "Total_Cost_Washing", "Tot_Maint_Cost_Bn_Nodes",
                               "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
                               "Actual_Length", "Element_Start", "Element_End", "Width_Element"]



            # EarthMaint_Fields=["Area_Potholes", "Area_Washing", "Unit_Cost_Potholes", "Unit_Cost_Washing",
            #                    "Total_Cost_Potholes", "Total_Cost_Washing", "Tot_Maint_Cost_Bn_Nodes",
            #                    "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition"]
            # 0               #1                    #2              # 3                # 4                   # 5                     #6
            cursor=arcpy.da.UpdateCursor(EarthMaint, EarthMaint_Fields)
            for row in cursor:
                # row[4] = row[0] * row[2]  # Total_Cost_Potholes
                # row[5] = row[1] * row[3]  # Total_Cost_Washing
                # row[6] = row[4] + row[5]  # Tot_Maint_Cost_Bn_Nodes

                # row[7] = row[0]+row[1]  # Tot_Deterior_Area_BNnodes
                # row[9] = float(row[7]/row[8])*100

                if row[9] == 0:
                    row[10]="Very Good"
                elif row[9] > 0 and row[9] <= 5:
                    row[10]="Good"
                elif row[9] > 5 and row[9] <= 20:
                    row[10]="Moderate"
                elif row[9] > 20 and row[9] <= 50:
                    row[10]="Poor"
                elif row[9] > 50:
                    row[10]="Very Poor"
                else:
                    row[10]="Contact Yonas"

                cursor.updateRow(row)
            del cursor

            GravelMaint_Fields=["Area_Potholes", "Area_Washing", "Area_Channeling", "Unit_Cost_Channeling",
                                "Unit_Cost_Washing", "Unit_Cost_Potholes", "Total_Cost_Washing",
                                "Total_Cost_Channeling", "Total_Cost_Potholes", "Tot_Maint_Cost_Bn_Nodes",
                                "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition",
                                "Actual_Length", "Element_Start", "Element_End", "Width_Element"]






            # GravelMaint_Fields=["Area_Potholes", "Area_Washing", "Area_Channeling", "Unit_Cost_Channeling",
            #                     "Unit_Cost_Washing", "Unit_Cost_Potholes", "Total_Cost_Washing",
            #                     "Total_Cost_Channeling", "Total_Cost_Potholes", "Tot_Maint_Cost_Bn_Nodes",
            #                     "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration", "Condition"]
            # 0              #1             #2                 #3                     #4                      #5                 #6                  #7                      #8                     #9                      ####10

            cursor=arcpy.da.UpdateCursor(GravelMaint, GravelMaint_Fields)
            for row in cursor:
                # row[6] = row[1] * row[4]  # Total_Cost_Washing
                # row[7] = row[2] * row[3]  # Total_Cost_Channeling
                # row[8] = row[0] * row[5]  # Total_Cost_Potholes
                # row[9] =  row[6] + row[7] + row[8] # Tot_Maint_Cost_Bn_Nodes

                # row[10] = row[0]+row[1] + row[2] # Tot_Deterior_Area_BNnodes
                # row[12] = float(row[10]/row[11])*100

                if row[12] == 0:
                    row[13]="Very Good"
                elif row[12] > 0 and row[12] <= 5:
                    row[13]="Good"
                elif row[12] > 5 and row[12] <= 20:
                    row[13]="Moderate"
                elif row[12] > 20 and row[12] <= 50:
                    row[13]="Poor"
                elif row[12] > 50:
                    row[13]="Very Poor"
                else:
                    row[13]="Contact Yonas"

                cursor.updateRow(row)
            del cursor

            LargeBlockMaint_Fields=["Area_Lifting", "Area_Depression", "Unit_Cost_Lifting", "Unit_Cost_Depression",
                                    "Total_Cost_Lifting", "Total_Cost_Depression", "Tot_Maint_Cost_BNnod",
                                    "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration",
                                    "Condition","Actual_Length", "Element_Start", "Element_End", "Width_Element"]










            # LargeBlockMaint_Fields=["Area_Lifting", "Area_Depression", "Unit_Cost_Lifting", "Unit_Cost_Depression",
            #                         "Total_Cost_Lifting", "Total_Cost_Depression", "Tot_Maint_Cost_BNnod",
            #                         "Tot_Deterior_Area_BNnodes", "Tot_Area_BNNodes", "Percent_Deterioration",
            #                         "Condition"]
            # 0             #1                  #2                    #3                      #4                   #5                    #6

            cursor=arcpy.da.UpdateCursor(LargeBlockMaint, LargeBlockMaint_Fields)
            for row in cursor:
                # row[4] = row[0] * row[2]  # Total_Cost_Lifting
                # row[5] = row[1] * row[3]  # Total_Cost_Depression
                # row[6] = row[4] + row[5]  # Tot_Maint_Cost_BNnod

                # row[7] = row[0]+row[1]  # Tot_Deterior_Area_BNnodes
                # row[9] = float(row[7]/row[8])*100

                if row[9] == 0:
                    row[10]="Very Good"
                elif row[9] > 0 and row[9] <= 5:
                    row[10]="Good"
                elif row[9] > 5 and row[9] <= 20:
                    row[10]="Moderate"
                elif row[9] > 20 and row[9] <= 50:
                    row[10]="Poor"
                elif row[9] > 50:
                    row[10]="Very Poor"
                else:
                    row[10]="Contact Yonas"

                cursor.updateRow(row)
            del cursor

        def main():
            readTime=2.5  # Pause to read what's written on dialog

            arcpy.SetProgressor("default",
                                "Dire Dawa ULGDP - Road Asset Updating Demo GP Tool    : \n  Developed by : Nur Yahya Kedirkhan ,Mobile:(+251)0982024688")
            arcpy.AddMessage("Dear {0}, You are Running Road Asset Updating Demo GP Tool".format(getpass.getuser()))

            time.sleep(5)

            pp=pathAssignment(parameters)
            GetPercentDeter(pp)
            GetDecision(pp)

            arcpy.AddMessage(
                "For further info,contact\n Mr.Yonas Abate ... Mobile:(+251)0933266518 ... Dire ULGDP \n Mr.Binyam G/Tensay ... Mobile:(+251)0930102024 ... DDUPRP \n Mr.Nur Yahya ... Mobile:(+251)0982024688 ... The Developer \n Dire Dawa \n ETHIOPIA")
            time.sleep(5)
            arcpy.AddMessage("Dire ULGDP : All Done")
            arcpy.ResetProgressor()

        main()
        
        
        
        
#---------------------------------------------------------------------








