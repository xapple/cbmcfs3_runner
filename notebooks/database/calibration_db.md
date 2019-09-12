---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.1'
      jupytext_version: 1.1.7
  kernelspec:
    display_name: Python 3
    language: python
    name: python3
---

```python
import sys, pandas
# Catch database related errors
from pyodbc import Error
from pandas.io.sql import DatabaseError

# Project modules
# Load the cbm_runner package from 'repos/' (instead of 'deploy/') #
sys.path.insert(0, "/repos/cbmcfs3_runner/")
from cbmcfs3_runner.core.continent import continent

# Choose  a country
# country = 'LU'
country = 'AT'
runner = continent[('calibration', country, 0)]
db = runner.post_processor.database
list_all_column_names = True
# List to be used with .iloc[] to select the first two and last two rows of a data frame
f2l2 = [0,1,-2,-1]
```

# Introduction

List all tables and show part of the content of some tables from the calibration database. 
Press on the table of contents icon to see the table of content. 
Some tables are in fact storred queries. The ODBC engine we use to read Access tables doesn't distinguish between tables and storred queries. Note also the Query section, which gives the SQL content of the storred queries.


# List all tables 

```python
db.tables
```

# List all column names
The list above contains tables and stored queries. 
MS Acces databases contains tables and storred SQL queries.
From the ODBC driver perspectives tables and queries are the same but queries take a longuer time to load (especially if there are nested queries underneath).

The following code is a little bit innefficient since it loads the content of all tables, 
just to display the column name. 
But most time is spend in the queries anyway, not in fetching the tables. 

```python
if list_all_column_names:
    for table in db.tables:
        print("")
        print(table)
        try:
            print(db[table].columns)
        except (Error, DatabaseError) as error:
            print(error)
```

## Catch errors
The following is only needed in case we have trouble figuring out 
from which module the error is coming from. 
For example `DatabaseError` can come from the pyodbc module or from pandas. This command helps us figure out the origin of the error. 


```python
import inspect
try:
    db['harvest fire']
except Exception as e:
    frm = inspect.trace()[-1]
    mod = inspect.getmodule(frm[0])
    modname = mod.__name__ if mod else frm[1]
    print('Thrown from', modname)
```

# Display


## back_inventory

```python
db['back_inventory']#.head(2)
```

## dist_events_const

```python
db['dist_events_const'].head(2)
```

## reversed_disturbance_events

```python
db['reversed_disturbance_events'].iloc[f2l2]
```

## selected_current_yts

```python
db['selected_current_yts'].head(2)
```

## selected_historical_yts

```python
db['selected_historical_yts'].head(2)
```

## tblfluxindicators

```python
db['tblfluxindicators'].head(2)
```

## tblpoolindicators

```python
db['tblpoolindicators'].head(2)
```

## tot_harvest_clearcut_disturbances

```python
db['tot_harvest_clearcut_disturbances'].head(2)

```

# SQL querries


|~sq_fInventory_CBM_Original:
SELECT DISTINCTROW *
FROM Inventory_CBM_Original;

|AG_VOLUME_ha:
SELECT Tot_Vol_ha_FT.TimeStep, Sum(Tot_Vol_ha_FT.Tot_AG_Vol_II) AS Tot_AG_Vol_II, Sum(Tot_Vol_ha_FT.Tot_Area_FT) AS Tot_Area_FT, [Tot_AG_Vol_II]/[Tot_Area_FT] AS AG_Vol_ha
FROM Tot_Vol_ha_FT
GROUP BY Tot_Vol_ha_FT.TimeStep;

|Area_FT:
SELECT qryTotalArea.TimeStep, User_Def_Class_Set_Translation_check.FT, Sum(qryTotalArea.SumOfArea) AS Area_FT
FROM qryTotalArea LEFT JOIN User_Def_Class_Set_Translation_check ON qryTotalArea.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID
WHERE (((qryTotalArea.LandClassID)=0))
GROUP BY qryTotalArea.TimeStep, User_Def_Class_Set_Translation_check.FT;

|Ave_Age_Evolution_qry:
SELECT User_Def_Class_Set_Translation_check.Status, User_Def_Class_Set_Translation_check.FT AS _2, User_Def_Class_Set_Translation_check.Reg AS _3, User_Def_Class_Set_Translation_check.MT AS _4, User_Def_Class_Set_Translation_check.MS AS _5, User_Def_Class_Set_Translation_check.CLU AS _6, User_Def_Class_Set_Translation_check.Con_Br AS _7, BACK_Inventory.UsingID, 'AGEID' & (Round([AveAge]/10)) AS Age, tblAgeIndicators.Area, BACK_Inventory.Delay, BACK_Inventory.UNFCCCL, BACK_Inventory.HistDist, BACK_Inventory.LastDist, tblAgeIndicators.Biomass AS Biomass_Carbon_ha, BEF_FTs.BEF_Tot, ([Biomass_Carbon_ha]/[BEF_Tot]) AS Merch_C_ha, ([Merch_C_ha]*2)/[DB] AS Merch_Vol_ha, Coefficients.DB, tblAgeIndicators.TimeStep
FROM ((tblAgeClasses INNER JOIN ((tblAgeIndicators LEFT JOIN User_Def_Class_Set_Translation_check ON tblAgeIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID) LEFT JOIN BACK_Inventory ON (User_Def_Class_Set_Translation_check.FT = BACK_Inventory.[_2]) AND (User_Def_Class_Set_Translation_check.Reg = BACK_Inventory.[_3]) AND (User_Def_Class_Set_Translation_check.Con_Br = BACK_Inventory.[_7])) ON tblAgeClasses.AgeClassID = tblAgeIndicators.AgeClassID) LEFT JOIN BEF_FTs ON User_Def_Class_Set_Translation_check.FT = BEF_FTs.FT) LEFT JOIN Coefficients ON User_Def_Class_Set_Translation_check.FT = Coefficients.Species
WHERE (((tblAgeIndicators.LandClassID)=0))
GROUP BY User_Def_Class_Set_Translation_check.Status, User_Def_Class_Set_Translation_check.FT, User_Def_Class_Set_Translation_check.Reg, User_Def_Class_Set_Translation_check.MT, User_Def_Class_Set_Translation_check.MS, User_Def_Class_Set_Translation_check.CLU, User_Def_Class_Set_Translation_check.Con_Br, BACK_Inventory.UsingID, 'AGEID' & (Round([AveAge]/10)), tblAgeIndicators.Area, BACK_Inventory.Delay, BACK_Inventory.UNFCCCL, BACK_Inventory.HistDist, BACK_Inventory.LastDist, tblAgeIndicators.Biomass, BEF_FTs.BEF_Tot, Coefficients.DB, tblAgeIndicators.TimeStep, tblAgeIndicators.AveAge
HAVING (((tblAgeIndicators.TimeStep)=17));

|Avg_WD:
SELECT Tot_Vol_ha_FT.FT, Avg(Tot_Vol_ha_FT.WD_CBM_FT) AS WD_CBM, Avg(Tot_Vol_ha_FT.DB) AS WD_Exp
FROM Tot_Vol_ha_FT
GROUP BY Tot_Vol_ha_FT.FT;

|Avg_Wood_Density:
SELECT Sum(Weight_Wood_density.Tot_Area) AS Tot_Area, Sum(Weight_Wood_density.DB_Area) AS DB_Area, [DB_Area]/[Tot_Area] AS Avg_WD
FROM Weight_Wood_density;

|BEF_Equations:
SELECT tblSpeciesType.SpeciesTypeName, tblBioTotalStemwood.A, tblBioTotalStemwood.B
FROM tblBioTotalStemwood LEFT JOIN tblSpeciesType ON tblBioTotalStemwood.SpeciesTypeID = tblSpeciesType.SpeciesTypeID
GROUP BY tblSpeciesType.SpeciesTypeName, tblBioTotalStemwood.A, tblBioTotalStemwood.B;

|BEF_FTs:
SELECT User_Def_Class_Set_Translation_check.FT, Sum(tblPoolIndicators.SW_Merch) AS SW_Merch, Sum(tblPoolIndicators.SW_Foliage) AS SW_Foliage, Sum(tblPoolIndicators.SW_Other) AS SW_Other, Sum(tblPoolIndicators.HW_Merch) AS HW_Merch, Sum(tblPoolIndicators.HW_Foliage) AS HW_Foliage, Sum(tblPoolIndicators.HW_Other) AS HW_Other, [SW_Merch]+[HW_Merch] AS Tot_Merch, [SW_Merch]+[HW_Merch]+[SW_Foliage]+[HW_Foliage]+[HW_Other]+[SW_Other] AS Tot_ABG, [Tot_ABG]/[Tot_Merch] AS BEF, Sum(tblPoolIndicators.SW_Coarse) AS SW_Coarse, Sum(tblPoolIndicators.SW_Fine) AS SW_Fine, Sum(tblPoolIndicators.HW_Coarse) AS HW_Coarse, Sum(tblPoolIndicators.HW_Fine) AS HW_Fine, [SW_Coarse]+[SW_Fine]+[HW_Coarse]+[HW_Fine] AS BG_Biomass, ([Tot_ABG]+[BG_Biomass])/[Tot_Merch] AS BEF_Tot
FROM tblPoolIndicators LEFT JOIN User_Def_Class_Set_Translation_check ON tblPoolIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID
GROUP BY User_Def_Class_Set_Translation_check.FT;

|Classifer_1_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_1
FROM (tblUserDefdClassSets LEFT JOIN tblUserDefdClassSetValues ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID) LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=1));

|Classifer_2_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_2
FROM (tblUserDefdClassSets LEFT JOIN tblUserDefdClassSetValues ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID) LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=2));

|Classifer_3_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_3
FROM (tblUserDefdClassSets LEFT JOIN tblUserDefdClassSetValues ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID) LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=3));

|Classifer_4_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_4
FROM tblUserDefdClassSets LEFT JOIN (tblUserDefdClassSetValues LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)) ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=4));

|Classifer_5_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_5
FROM (tblUserDefdClassSets LEFT JOIN tblUserDefdClassSetValues ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID) LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=5));

|Classifer_6_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_6
FROM (tblUserDefdClassSets LEFT JOIN tblUserDefdClassSetValues ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID) LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=6));

|Classifer_7_check:
SELECT tblUserDefdClassSets.UserDefdClassSetID, tblUserDefdClassSets.Name, tblUserDefdSubclasses.UserDefdSubClassName AS CL_7
FROM (tblUserDefdClassSets LEFT JOIN tblUserDefdClassSetValues ON tblUserDefdClassSets.UserDefdClassSetID = tblUserDefdClassSetValues.UserDefdClassSetID) LEFT JOIN tblUserDefdSubclasses ON (tblUserDefdClassSetValues.UserDefdSubclassID = tblUserDefdSubclasses.UserDefdSubclassID) AND (tblUserDefdClassSetValues.UserDefdClassID = tblUserDefdSubclasses.UserDefdClassID)
WHERE (((tblUserDefdSubclasses.UserDefdClassID)=7));

|Copy Of Harvest summay check:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Tot_Merch_Vol, Sum([Harvest analysis check].Vol_Snags) AS Tot_Snag_Vol, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_SubMerch_Vol, Sum([Harvest analysis check].Forest_residues_Vol) AS Tot_Res_Vol, Sum([Harvest analysis check].TC) AS SumOfTC, [Tot_Merch_Vol]+[Tot_Snag_Vol]+[Tot_SubMerch_Vol] AS TOT_VOL, tblDisturbanceType.DistTypeName, [Harvest analysis check].FT
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
GROUP BY [Harvest analysis check].TimeStep, tblDisturbanceType.DistTypeName, [Harvest analysis check].FT;

|DIST COMPONENTS Analysis DETAILES:
SELECT [DISTURBANCE COMPONENTS analysis].FT, [DISTURBANCE COMPONENTS analysis].DistTypeName, Sum([DISTURBANCE COMPONENTS analysis].Tot_Merch_Vol) AS MERCH_VOL, Sum([DISTURBANCE COMPONENTS analysis].Tot_Snag_Vol) AS SNAGS_VOL, Sum([DISTURBANCE COMPONENTS analysis].Tot_SubMerch_Vol) AS SUBM_VOL, Sum([DISTURBANCE COMPONENTS analysis].Tot_Res_Vol) AS RES_VOL, [SUBM_VOL]/[MERCH_VOL] AS SUBMERCH_Fraction, [SNAGS_VOL]/[MERCH_VOL] AS SNAGS_Fraction, [RES_VOL]/[MERCH_VOL] AS RES_Fraction
FROM [DISTURBANCE COMPONENTS analysis]
GROUP BY [DISTURBANCE COMPONENTS analysis].FT, [DISTURBANCE COMPONENTS analysis].DistTypeName
ORDER BY [DISTURBANCE COMPONENTS analysis].FT, [DISTURBANCE COMPONENTS analysis].DistTypeName;

|DISTURBANCE COMPONENTS analysis:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Tot_Merch_Vol, Sum([Harvest analysis check].Vol_Snags) AS Tot_Snag_Vol, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_SubMerch_Vol, Sum([Harvest analysis check].Forest_residues_Vol) AS Tot_Res_Vol, Sum([Harvest analysis check].TC) AS SumOfTC, [Tot_Merch_Vol]+[Tot_Snag_Vol]+[Tot_SubMerch_Vol] AS TOT_VOL, tblDisturbanceType.DistTypeName, [Harvest analysis check].FT
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
GROUP BY [Harvest analysis check].TimeStep, tblDisturbanceType.DistTypeName, [Harvest analysis check].FT;

|FW_B_Analysis:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Vol_Merch_FW_B, Sum([Harvest analysis check].Vol_SubMerch) AS Vol_SubMerch_FW_B, Sum([Harvest analysis check].Vol_Snags) AS Vol_Snags_FW_B, Sum([Harvest analysis check].TC) AS TC_FW_B, SILV_TRETMENTS_AT.HWP
FROM [Harvest analysis check] LEFT JOIN SILV_TRETMENTS_AT ON ([Harvest analysis check].MS = SILV_TRETMENTS_AT.[_5]) AND ([Harvest analysis check].MT = SILV_TRETMENTS_AT.[_4]) AND ([Harvest analysis check].FT = SILV_TRETMENTS_AT.[_2]) AND ([Harvest analysis check].DistTypeName = SILV_TRETMENTS_AT.Dist_Type_ID)
GROUP BY [Harvest analysis check].TimeStep, SILV_TRETMENTS_AT.HWP
HAVING (((SILV_TRETMENTS_AT.HWP)="FW_B"));

|FW_B_Total:
SELECT IRW_B_Analysis.TimeStep, FW_B_Analysis.Vol_Merch_FW_B, FW_B_Analysis.Vol_SubMerch_FW_B, FW_B_Analysis.Vol_Snags_FW_B, IRW_B_Analysis.Vol_SubMerch_IRW_B, IRW_B_Analysis.Vol_Snags_IRW_B, IIf([Vol_Merch_FW_B]>0,[Vol_Merch_FW_B]+[Vol_SubMerch_FW_B]+[Vol_Snags_FW_B]+[Vol_SubMerch_IRW_B]+[Vol_Snags_IRW_B],[Vol_SubMerch_IRW_B]+[Vol_Snags_IRW_B]) AS TOT_Vol_FW_B
FROM FW_B_Analysis RIGHT JOIN IRW_B_Analysis ON FW_B_Analysis.TimeStep = IRW_B_Analysis.TimeStep;

|FW_C_Analysis:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Vol_Merch_FW_C, Sum([Harvest analysis check].Vol_SubMerch) AS Vol_SubMerch_FW_C, Sum([Harvest analysis check].Vol_Snags) AS Vol_Snags_FW_C, Sum([Harvest analysis check].TC) AS TC_FW_C, SILV_TRETMENTS_AT.HWP
FROM [Harvest analysis check] LEFT JOIN SILV_TRETMENTS_AT ON ([Harvest analysis check].MS = SILV_TRETMENTS_AT.[_5]) AND ([Harvest analysis check].MT = SILV_TRETMENTS_AT.[_4]) AND ([Harvest analysis check].FT = SILV_TRETMENTS_AT.[_2]) AND ([Harvest analysis check].DistTypeName = SILV_TRETMENTS_AT.Dist_Type_ID)
GROUP BY [Harvest analysis check].TimeStep, SILV_TRETMENTS_AT.HWP
HAVING (((SILV_TRETMENTS_AT.HWP)="FW_C"));

|FW_C_Total:
SELECT IRW_C_Analysis.TimeStep, FW_C_Analysis.Vol_Merch_FW_C, FW_C_Analysis.Vol_SubMerch_FW_C, FW_C_Analysis.Vol_Snags_FW_C, IRW_C_Analysis.Vol_SubMerch_IRW_C, IRW_C_Analysis.Vol_Snags_IRW_C, IIf([Vol_Merch_FW_C]>0,[Vol_Merch_FW_C]+[Vol_SubMerch_FW_C]+[Vol_Snags_FW_C]+[Vol_SubMerch_IRW_C]+[Vol_Snags_IRW_C],[Vol_SubMerch_IRW_C]+[Vol_Snags_IRW_C]) AS TOT_Vol_FW_C
FROM FW_C_Analysis RIGHT JOIN IRW_C_Analysis ON FW_C_Analysis.TimeStep = IRW_C_Analysis.TimeStep;

|Harvest analysis check:
SELECT tblFluxIndicators.DistTypeID, tblFluxIndicators.TimeStep, Sum(tblFluxIndicators.SoftProduction) AS TS, Sum(tblFluxIndicators.HardProduction) AS TH, User_Def_Class_Set_Translation_check.FT, Coefficients.C, Coefficients.DB, [TS]+[TH] AS TC, ([TC]*2)/[DB] AS Vol_Merch, User_Def_Class_Set_Translation_check.MT, User_Def_Class_Set_Translation_check.MS, tblFluxIndicators.DOMProduction, User_Def_Class_Set_Translation_check.Reg, tblFluxIndicators.CO2Production, ([CO2Production]*2)/[DB] AS Vol_SubMerch, ([DOMProduction]*2)/[DB] AS Vol_Snags, User_Def_Class_Set_Translation_check.Con_Br, (([MerchLitterInput]+[OthLitterInput])*2)/[DB] AS Forest_residues_Vol, tblFluxIndicators.MerchLitterInput, tblFluxIndicators.OthLitterInput, tblDisturbanceType.DistTypeName, User_Def_Class_Set_Translation_check.CLU
FROM tblDisturbanceType INNER JOIN (tblFluxIndicators LEFT JOIN (User_Def_Class_Set_Translation_check LEFT JOIN Coefficients ON User_Def_Class_Set_Translation_check.FT = Coefficients.Species) ON tblFluxIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID) ON tblDisturbanceType.DistTypeID = tblFluxIndicators.DistTypeID
GROUP BY tblFluxIndicators.DistTypeID, tblFluxIndicators.TimeStep, User_Def_Class_Set_Translation_check.FT, Coefficients.C, Coefficients.DB, User_Def_Class_Set_Translation_check.MT, User_Def_Class_Set_Translation_check.MS, tblFluxIndicators.DOMProduction, User_Def_Class_Set_Translation_check.Reg, tblFluxIndicators.CO2Production, User_Def_Class_Set_Translation_check.Con_Br, tblFluxIndicators.MerchLitterInput, tblFluxIndicators.OthLitterInput, tblDisturbanceType.DistTypeName, User_Def_Class_Set_Translation_check.Con_Br, tblFluxIndicators.MerchLitterInput, tblFluxIndicators.OthLitterInput, User_Def_Class_Set_Translation_check.CLU
HAVING (((tblFluxIndicators.DistTypeID)<>0));

|Harvest FIRE:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Tot_Merch_Vol, Sum([Harvest analysis check].Forest_residues_Vol) AS Tot_Res_Vol, Sum([Harvest analysis check].TC) AS SumOfTC, [Harvest analysis check].Con_Br
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
WHERE (((tblDisturbanceType.DistTypeName)="DISTID11"))
GROUP BY [Harvest analysis check].TimeStep, [Harvest analysis check].Con_Br;

|Harvest summay check:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Tot_Merch_Vol, Sum([Harvest analysis check].Vol_Snags) AS Tot_Snag_Vol, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_SubMerch_Vol, Sum([Harvest analysis check].Forest_residues_Vol) AS Tot_Res_Vol, Sum([Harvest analysis check].TC) AS SumOfTC, [Harvest analysis check].MT, [Tot_Merch_Vol]+[Tot_Snag_Vol]+[Tot_SubMerch_Vol] AS TOT_VOL, [Harvest analysis check].FT
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
GROUP BY [Harvest analysis check].TimeStep, [Harvest analysis check].MT, [Harvest analysis check].FT;

|Harvest_expected_provided:
SELECT Dist_Events_Const.Step, Dist_Events_Const.[_2], Dist_Events_Const.Dist_Type_ID, Sum(Dist_Events_Const.Amount) AS Exp, Sum([Copy Of Harvest summay check].SumOfTC) AS Prov, (([Prov]-[Exp])/[Exp])*100 AS Delta
FROM Dist_Events_Const LEFT JOIN [Copy Of Harvest summay check] ON (Dist_Events_Const.[_2] = [Copy Of Harvest summay check].FT) AND (Dist_Events_Const.Dist_Type_ID = [Copy Of Harvest summay check].DistTypeName) AND (Dist_Events_Const.Step = [Copy Of Harvest summay check].TimeStep)
GROUP BY Dist_Events_Const.Step, Dist_Events_Const.[_1], Dist_Events_Const.[_2], Dist_Events_Const.[_4], Dist_Events_Const.[_5], Dist_Events_Const.Dist_Type_ID;

|HWP_ANALYSIS:
SELECT IRW_C_Analysis.TimeStep, IRW_C_Analysis.Vol_Merch_IRW_C, IRW_B_Analysis.Vol_Merch_IRW_B, FW_C_Total.TOT_Vol_FW_C, FW_B_Total.TOT_Vol_FW_B, Tot_Area_TS.Tot_Area, ([Vol_Merch_IRW_C]+[Vol_Merch_IRW_B]+[TOT_Vol_FW_C]+[TOT_Vol_FW_B])/[Tot_Area] AS Tot_Harvest_ha
FROM (((IRW_C_Analysis INNER JOIN IRW_B_Analysis ON IRW_C_Analysis.TimeStep = IRW_B_Analysis.TimeStep) INNER JOIN FW_B_Total ON IRW_B_Analysis.TimeStep = FW_B_Total.TimeStep) INNER JOIN FW_C_Total ON FW_B_Total.TimeStep = FW_C_Total.TimeStep) INNER JOIN Tot_Area_TS ON IRW_C_Analysis.TimeStep = Tot_Area_TS.TimeStep;

|HWP_Ha:
SELECT IRW_C_Analysis.TimeStep, IRW_C_Analysis.Vol_Merch_IRW_C, IRW_B_Analysis.Vol_Merch_IRW_B, FW_C_Total.Vol_Merch_FW_C, FW_B_Total.Vol_Merch_FW_B, Tot_Area_TS.Tot_Area, IIf([Vol_Merch_FW_C]>0,[Vol_Merch_IRW_C]+[Vol_Merch_IRW_B]+[Vol_Merch_FW_C]+[Vol_Merch_FW_B],[Vol_Merch_IRW_C]+[Vol_Merch_IRW_B]+[Vol_Merch_FW_B]) AS Tot_Merch_Harvest, [Tot_Merch_Harvest]/[Tot_Area] AS Merch_Harvest_ha, ([Vol_Merch_IRW_C]+[Vol_Merch_IRW_B]+[Vol_Merch_FW_C]+[Vol_Merch_FW_B])/[Tot_Area] AS Tot_Harvest_ha
FROM (((IRW_C_Analysis INNER JOIN IRW_B_Analysis ON IRW_C_Analysis.TimeStep = IRW_B_Analysis.TimeStep) INNER JOIN FW_B_Total ON IRW_B_Analysis.TimeStep = FW_B_Total.TimeStep) INNER JOIN FW_C_Total ON FW_B_Total.TimeStep = FW_C_Total.TimeStep) INNER JOIN Tot_Area_TS ON IRW_B_Analysis.TimeStep = Tot_Area_TS.TimeStep;

|IRW_B_Analysis:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Vol_Merch_IRW_B, Sum([Harvest analysis check].Vol_SubMerch) AS Vol_SubMerch_IRW_B, Sum([Harvest analysis check].Vol_Snags) AS Vol_Snags_IRW_B, Sum([Harvest analysis check].TC) AS TC_IRW_B, SILV_TRETMENTS_AT.HWP
FROM [Harvest analysis check] LEFT JOIN SILV_TRETMENTS_AT ON ([Harvest analysis check].MS = SILV_TRETMENTS_AT.[_5]) AND ([Harvest analysis check].MT = SILV_TRETMENTS_AT.[_4]) AND ([Harvest analysis check].FT = SILV_TRETMENTS_AT.[_2]) AND ([Harvest analysis check].DistTypeName = SILV_TRETMENTS_AT.Dist_Type_ID)
GROUP BY [Harvest analysis check].TimeStep, SILV_TRETMENTS_AT.HWP
HAVING (((SILV_TRETMENTS_AT.HWP)="IRW_B"));

|IRW_C_Analysis:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].Vol_Merch) AS Vol_Merch_IRW_C, Sum([Harvest analysis check].Vol_SubMerch) AS Vol_SubMerch_IRW_C, Sum([Harvest analysis check].Vol_Snags) AS Vol_Snags_IRW_C, Sum([Harvest analysis check].TC) AS TC_IRW_C, SILV_TRETMENTS_AT.HWP
FROM [Harvest analysis check] LEFT JOIN SILV_TRETMENTS_AT ON ([Harvest analysis check].MS = SILV_TRETMENTS_AT.[_5]) AND ([Harvest analysis check].MT = SILV_TRETMENTS_AT.[_4]) AND ([Harvest analysis check].FT = SILV_TRETMENTS_AT.[_2]) AND ([Harvest analysis check].DistTypeName = SILV_TRETMENTS_AT.Dist_Type_ID)
GROUP BY [Harvest analysis check].TimeStep, SILV_TRETMENTS_AT.HWP
HAVING (((SILV_TRETMENTS_AT.HWP)="IRW_C"));

|LANDMARK_Query:
SELECT tblPoolIndicators.TimeStep, User_Def_Class_Set_Translation_check.FT, User_Def_Class_Set_Translation_check.Reg, User_Def_Class_Set_Translation_check.MT, User_Def_Class_Set_Translation_check.MS, User_Def_Class_Set_Translation_check.CLU, User_Def_Class_Set_Translation_check.Con_Br, Sum(tblPoolIndicators.SW_Merch) AS SumOfSW_Merch, Sum(tblPoolIndicators.SW_Foliage) AS SumOfSW_Foliage, Sum(tblPoolIndicators.SW_Other) AS SumOfSW_Other, Sum(tblPoolIndicators.VFastAG) AS SumOfVFastAG, Sum(tblPoolIndicators.VFastBG) AS SumOfVFastBG, Sum(tblPoolIndicators.FastAG) AS SumOfFastAG, Sum(tblPoolIndicators.FastBG) AS SumOfFastBG, Sum(tblPoolIndicators.Medium) AS SumOfMedium, Sum(tblPoolIndicators.SlowAG) AS SumOfSlowAG, Sum(tblPoolIndicators.SlowBG) AS SumOfSlowBG, Sum(tblPoolIndicators.SWStemSnag) AS SumOfSWStemSnag, Sum(tblPoolIndicators.SWBranchSnag) AS SumOfSWBranchSnag, Sum(tblPoolIndicators.HWStemSnag) AS SumOfHWStemSnag, Sum(tblPoolIndicators.HWBranchSnag) AS SumOfHWBranchSnag, Sum(tblPoolIndicators.SW_subMerch) AS SumOfSW_subMerch, Sum(tblPoolIndicators.SW_Coarse) AS SumOfSW_Coarse, Sum(tblPoolIndicators.SW_Fine) AS SumOfSW_Fine, Sum(tblPoolIndicators.HW_Merch) AS SumOfHW_Merch, Sum(tblPoolIndicators.HW_Foliage) AS SumOfHW_Foliage, Sum(tblPoolIndicators.HW_Other) AS SumOfHW_Other, Sum(tblPoolIndicators.HW_subMerch) AS SumOfHW_subMerch, Sum(tblPoolIndicators.HW_Coarse) AS SumOfHW_Coarse, Sum(tblPoolIndicators.HW_Fine) AS SumOfHW_Fine, [SumOfSW_Merch]+[SumOfSW_Foliage]+[SumOfSW_Other]+[SumOfHW_Merch]+[SumOfHW_Foliage]+[SumOfHW_Other] AS AG_Biomass, [SumOfSW_Coarse]+[SumOfSW_Fine]+[SumOfHW_Coarse]+[SumOfHW_Fine] AS BG_Biomass, [SumOfSlowBG]+[SumOfVFastBG] AS SOIL, [SumOfVFastAG]+[SumOfFastAG]+[SumOfFastBG]+[SumOfMedium]+[SumOfSlowAG]+[SumOfSWStemSnag]+[SumOfSWBranchSnag]+[SumOfHWStemSnag]+[SumOfHWBranchSnag] AS DOM, qryTotalArea.SumOfArea AS Area
FROM (tblPoolIndicators INNER JOIN User_Def_Class_Set_Translation_check ON tblPoolIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID) LEFT JOIN qryTotalArea ON (tblPoolIndicators.TimeStep = qryTotalArea.TimeStep) AND (tblPoolIndicators.UserDefdClassSetID = qryTotalArea.UserDefdClassSetID)
GROUP BY tblPoolIndicators.TimeStep, User_Def_Class_Set_Translation_check.FT, User_Def_Class_Set_Translation_check.Reg, User_Def_Class_Set_Translation_check.MT, User_Def_Class_Set_Translation_check.MS, User_Def_Class_Set_Translation_check.CLU, User_Def_Class_Set_Translation_check.Con_Br, qryTotalArea.SumOfArea
HAVING (((tblPoolIndicators.TimeStep)>0));

|Merch_Incr_ha_FINAL:
SELECT Vol_ha_II.TimeStep, Vol_ha_II.Vol_ha_II, Vol_ha_II_1.Vol_ha_II_1, [Vol_ha_II]-[Vol_ha_II_1] AS NAI, HWP_Ha.Merch_Harvest_ha, [NAI]+[Merch_Harvest_ha] AS GAI
FROM Vol_ha_II_1 RIGHT JOIN (Vol_ha_II LEFT JOIN HWP_Ha ON Vol_ha_II.TimeStep = HWP_Ha.TimeStep) ON Vol_ha_II_1.TimeStep_1 = Vol_ha_II.TimeStep;

|Merch_Stock:
SELECT tblPoolIndicators.TimeStep, User_Def_Class_Set_Translation_check.FT, Sum(tblPoolIndicators.SW_Merch) AS SW_Merch_Tot, Sum(tblPoolIndicators.HW_Merch) AS HW_Merch_Tot, Coefficients.DB, Coefficients.Harvest_Gr, ([SW_Merch_Tot]+[HW_Merch_Tot])*2/[DB] AS Merch_Vol, Sum(tblPoolIndicators.SW_Foliage) AS SW_Foliage, Sum(tblPoolIndicators.SW_Other) AS SW_Other, Sum(tblPoolIndicators.HW_Foliage) AS HW_Foliage, Sum(tblPoolIndicators.HW_Other) AS HW_Other, [SW_Merch_Tot]+[HW_Merch_Tot] AS Tot_C_Merch, [Tot_C_Merch]+[SW_Foliage]+[SW_Other]+[HW_Foliage]+[HW_Other] AS Tot_AG
FROM (tblPoolIndicators LEFT JOIN User_Def_Class_Set_Translation_check ON tblPoolIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID) LEFT JOIN Coefficients ON User_Def_Class_Set_Translation_check.FT = Coefficients.Species
GROUP BY tblPoolIndicators.TimeStep, User_Def_Class_Set_Translation_check.FT, Coefficients.DB, Coefficients.Harvest_Gr;

|Merchantable_C_TS0:
SELECT Sum(tblPoolIndicators.SW_Merch) AS SumOfSW_Merch, Sum(tblPoolIndicators.HW_Merch) AS SumOfHW_Merch, User_Def_Class_Set_Translation_check.Con_Br
FROM tblPoolIndicators LEFT JOIN User_Def_Class_Set_Translation_check ON tblPoolIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID
WHERE (((tblPoolIndicators.TimeStep)=0))
GROUP BY User_Def_Class_Set_Translation_check.Con_Br;

|Net_Gross_Growth:
SELECT tblFluxIndicators.TimeStep, Sum(tblFluxIndicators.DeltaBiomass_AG) AS Tot_DeltaBiomass_AG, Sum(tblFluxIndicators.DeltaBiomass_BG) AS Tot_DeltaBiomass_BG, Sum(tblFluxIndicators.GrossGrowth_AG) AS Tot_GrossGrowth_AG, Sum(tblFluxIndicators.GrossGrowth_BG) AS Tot_GrossGrowth_BG, tblFluxIndicators.UserDefdClassSetID, User_Def_Class_Set_Translation_check.FT, Sum(tblFluxIndicators.MerchLitterInput) AS Tot_MerchLitterInput
FROM tblFluxIndicators LEFT JOIN User_Def_Class_Set_Translation_check ON tblFluxIndicators.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID
GROUP BY tblFluxIndicators.TimeStep, tblFluxIndicators.UserDefdClassSetID, User_Def_Class_Set_Translation_check.FT;

|Net_Gross_Growth_Area:
|Net_Gross_Growth_FINAL:
SELECT Net_Gross_Growth_Area.TimeStep, Sum(Net_Gross_Growth_Area.DeltaVol_AG) AS DeltaVol_AG, Sum(Net_Gross_Growth_Area.T_Area) AS T_Area, [DeltaVol_AG]/[T_Area] AS DeltaVol_AG_ha, Avg(Net_Gross_Growth_Area.WD_CBM_FT) AS AvgOfWD_CBM_FT, Sum(Net_Gross_Growth_Area.Tot_MerchLitterInput_Vol) AS Tot_MerchLitterInput_Vol, [Tot_MerchLitterInput_Vol]/[T_Area] AS MerchLitt_Input_ha
FROM Net_Gross_Growth_Area
GROUP BY Net_Gross_Growth_Area.TimeStep;

|Query1:
SELECT *
FROM MsysObjects
WHERE (Left$([Name],1)<>"~") AND 
(MSysObjects.Type)=5
ORDER BY MSysObjects.Name;

|Query2:
SELECT *
FROM AllQueries;

|Tot_area:
SELECT Sum(Back_Inventory.Area) AS Tot_area, Back_Inventory.[_2]
FROM Back_Inventory
GROUP BY Back_Inventory.[_2];

|Tot_Area_Output:
SELECT qryTotalArea.TimeStep, Sum(qryTotalArea.SumOfArea) AS Tot_Area, qryTotalArea.UserDefdClassSetID, qryTotalArea.LandClassID, User_Def_Class_Set_Translation_check.FT
FROM qryTotalArea LEFT JOIN User_Def_Class_Set_Translation_check ON qryTotalArea.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID
GROUP BY qryTotalArea.TimeStep, qryTotalArea.UserDefdClassSetID, qryTotalArea.LandClassID, User_Def_Class_Set_Translation_check.FT
HAVING (((qryTotalArea.LandClassID)=0));

|Tot_Area_TS:
SELECT qryTotalArea.TimeStep, Sum(qryTotalArea.SumOfArea) AS Tot_Area
FROM qryTotalArea LEFT JOIN User_Def_Class_Set_Translation_check ON qryTotalArea.UserDefdClassSetID = User_Def_Class_Set_Translation_check.UserDefdClassSetID
WHERE (((qryTotalArea.LandClassID)=0))
GROUP BY qryTotalArea.TimeStep;

|TOT_Harvest:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].TC) AS Tot_C, Sum([Harvest analysis check].Vol_Merch) AS Tot_V_Merch, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_V_SubMerch, Sum([Harvest analysis check].Vol_Snags) AS Tot_V_Snags, [Tot_V_Merch]+[Tot_V_SubMerch]+[Tot_V_Snags] AS TOT_Vol
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
GROUP BY [Harvest analysis check].TimeStep;

|TOT_Harvest_Clearcut_Disturbances:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].TC) AS Tot_C, Sum([Harvest analysis check].Vol_Merch) AS Tot_V_Merch, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_V_SubMerch, Sum([Harvest analysis check].Vol_Snags) AS Tot_V_Snags, [Tot_V_Merch]+[Tot_V_SubMerch]+[Tot_V_Snags] AS TOT_Vol, [Harvest analysis check].FT, [Harvest analysis check].MT, [Harvest analysis check].MS, tblDisturbanceType.DistTypeName
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
GROUP BY [Harvest analysis check].TimeStep, [Harvest analysis check].FT, [Harvest analysis check].MT, [Harvest analysis check].MS, tblDisturbanceType.DistTypeName
HAVING (((tblDisturbanceType.DistTypeName)='DISTID1' Or (tblDisturbanceType.DistTypeName)='DISTID10'));

|TOT_Harvest_Distribution:
SELECT [Harvest analysis check].TimeStep, Sum([Harvest analysis check].TC) AS Tot_C, Sum([Harvest analysis check].Vol_Merch) AS Tot_V_Merch, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_V_SubMerch, Sum([Harvest analysis check].Vol_Snags) AS Tot_V_Snags, [Tot_V_Merch]+[Tot_V_SubMerch]+[Tot_V_Snags] AS TOT_Vol, [Harvest analysis check].FT, [Harvest analysis check].Reg, [Harvest analysis check].CLU
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
GROUP BY [Harvest analysis check].TimeStep, [Harvest analysis check].FT, [Harvest analysis check].Reg, [Harvest analysis check].CLU;

|TOT_Harvest_Share:
SELECT Sum([Harvest analysis check].TC) AS Tot_C, Sum([Harvest analysis check].Vol_Merch) AS Tot_V_Merch, Sum([Harvest analysis check].Vol_SubMerch) AS Tot_V_SubMerch, Sum([Harvest analysis check].Vol_Snags) AS Tot_V_Snags, [Tot_V_Merch]+[Tot_V_SubMerch]+[Tot_V_Snags] AS TOT_Vol, tblDisturbanceType.DistTypeName
FROM [Harvest analysis check] INNER JOIN tblDisturbanceType ON [Harvest analysis check].DistTypeID = tblDisturbanceType.DistTypeID
WHERE ((([Harvest analysis check].TimeStep)<=16))
GROUP BY tblDisturbanceType.DistTypeName;

|Tot_Merch_Vol:
SELECT Merch_Stock.TimeStep, Sum(Merch_Stock.Merch_Vol) AS SumOfMerch_Vol, Coefficients.Harvest_Gr
FROM Merch_Stock LEFT JOIN Coefficients ON Merch_Stock.FT = Coefficients.Species
GROUP BY Merch_Stock.TimeStep, Coefficients.Harvest_Gr;

|Tot_Stock:
SELECT Merch_Stock.TimeStep, Sum(Merch_Stock.[SW_Foliage]) AS SW_Foliage, Sum(Merch_Stock.[SW_Other]) AS SW_Other, Sum(Merch_Stock.[HW_Foliage]) AS HW_Foliage, Sum(Merch_Stock.[HW_Other]) AS HW_Other, Sum(Merch_Stock.[Tot_C_Merch]) AS Tot_C_Merch, Sum(Merch_Stock.[Tot_AG]) AS Tot_AG, [SW_Foliage]+[HW_Foliage] AS Tot_Foliages, [SW_Other]+[HW_Other] AS Tot_OWCs, Sum(Net_Gross_Growth_Area.[T_DeltaBiomass_AG]) AS T_DeltaBiomass_AG
FROM Merch_Stock INNER JOIN Net_Gross_Growth_Area ON (Merch_Stock.FT = Net_Gross_Growth_Area.FT) AND (Merch_Stock.TimeStep = Net_Gross_Growth_Area.TimeStep)
GROUP BY Merch_Stock.TimeStep;

|Tot_Vol_Check:
SELECT Tot_Vol_ha_FT.TimeStep, Sum(Tot_Vol_ha_FT.Vol_Area_II) AS Tot_Merch_Vol, Sum(Tot_Vol_ha_FT.Tot_Area_FT) AS SumOfTot_Area_FT, Coefficients.Harvest_Gr
FROM Tot_Vol_ha_FT LEFT JOIN Coefficients ON Tot_Vol_ha_FT.FT = Coefficients.Species
GROUP BY Tot_Vol_ha_FT.TimeStep, Coefficients.Harvest_Gr;

|Tot_Vol_ha_FT:
SELECT Merch_Stock.TimeStep, Merch_Stock.FT, Sum(Area_FT.Area_FT) AS Tot_Area_FT, Sum(Merch_Stock.Tot_C_Merch) AS Tot_C_Merch, [Tot_C_Merch]/[Tot_Area_FT] AS Tot_C_Merch_ha, BEF_Equations.A, BEF_Equations.B, ([Tot_C_Merch_ha]*2/[A])^(1/[B]) AS Tot_Merch_Vol_II, [Tot_Merch_Vol_II]*[Tot_Area_FT] AS Vol_Area_II, BEF_FTs.BEF, [Vol_Area_II]*[BEF] AS Tot_AG_Vol_II, Sum(Merch_Stock.Tot_AG) AS Tot_AG, [Tot_AG]/[Tot_Area_FT] AS AG_ha_FT, [AG_ha_FT]*2/[Tot_Merch_Vol_II] AS BCEF_FT, [Tot_C_Merch_ha]*2/[Tot_Merch_Vol_II] AS WD_CBM_FT, Merch_Stock.DB
FROM (((Merch_Stock LEFT JOIN Area_FT ON (Merch_Stock.TimeStep = Area_FT.TimeStep) AND (Merch_Stock.FT = Area_FT.FT)) LEFT JOIN BEF_FTs ON Merch_Stock.FT = BEF_FTs.FT) LEFT JOIN Classifiers ON Merch_Stock.FT = Classifiers.ClassifierValueID) LEFT JOIN BEF_Equations ON Classifiers.Name = BEF_Equations.SpeciesTypeName
GROUP BY Merch_Stock.TimeStep, Merch_Stock.FT, BEF_Equations.A, BEF_Equations.B, BEF_FTs.BEF, Merch_Stock.DB;

|User_Def_Class_Set_Translation_check:
SELECT Classifer_1_check.UserDefdClassSetID, Classifer_1_check.Name, Classifer_1_check.CL_1 AS Status, Classifer_2_check.CL_2 AS FT, Classifer_3_check.CL_3 AS Reg, Classifer_4_check.CL_4 AS MT, Classifer_5_check.CL_5 AS MS, Classifer_6_check.CL_6 AS CLU, Classifer_7_check.CL_7 AS Con_Br
FROM (((((Classifer_1_check INNER JOIN Classifer_2_check ON Classifer_1_check.UserDefdClassSetID = Classifer_2_check.UserDefdClassSetID) INNER JOIN Classifer_3_check ON Classifer_2_check.UserDefdClassSetID = Classifer_3_check.UserDefdClassSetID) INNER JOIN Classifer_4_check ON Classifer_3_check.UserDefdClassSetID = Classifer_4_check.UserDefdClassSetID) INNER JOIN Classifer_5_check ON Classifer_4_check.UserDefdClassSetID = Classifer_5_check.UserDefdClassSetID) INNER JOIN Classifer_6_check ON Classifer_5_check.UserDefdClassSetID = Classifer_6_check.UserDefdClassSetID) INNER JOIN Classifer_7_check ON Classifer_6_check.UserDefdClassSetID = Classifer_7_check.UserDefdClassSetID;

|Vol_ha_II:
SELECT Tot_Vol_ha_FT.TimeStep, Sum(Tot_Vol_ha_FT.Tot_Area_FT) AS Area_sum, Sum(Tot_Vol_ha_FT.Vol_Area_II) AS Vol_Area_II, Sum(Tot_Vol_ha_FT.Tot_AG_Vol_II) AS Tot_AG_Vol_II, [Vol_Area_II]/[Area_sum] AS Vol_ha_II, [Tot_AG_Vol_II]/[Area_sum] AS AG_Vol_ha_II
FROM Tot_Vol_ha_FT
GROUP BY Tot_Vol_ha_FT.TimeStep;

|Vol_ha_II_1:
SELECT [TimeStep]+1 AS TimeStep_1, Vol_ha_II.Vol_ha_II AS Vol_ha_II_1, Vol_ha_II.AG_Vol_ha_II AS AG_Vol_ha_II_1, Vol_ha_II.TimeStep
FROM Vol_ha_II
GROUP BY Vol_ha_II.Vol_ha_II, Vol_ha_II.AG_Vol_ha_II, Vol_ha_II.TimeStep;

|VOLINC_Summary:
SELECT Merch_Incr_ha_FINAL.TimeStep, Merch_Incr_ha_FINAL.Vol_ha_II.Vol_ha_II AS Vol_ha, Merch_Incr_ha_FINAL.Vol_ha_II_1, Merch_Incr_ha_FINAL.NAI AS Merch_Stock_Change, Merch_Incr_ha_FINAL.Merch_Harvest_ha, Merch_Incr_ha_FINAL.GAI AS Merch_NAI, Net_Gross_Growth_FINAL.DeltaVol_AG_ha AS AG_CAI, Net_Gross_Growth_FINAL.AvgOfWD_CBM_FT AS Avg_CBM_WD, Net_Gross_Growth_FINAL.MerchLitt_Input_ha, [Merch_NAI]+[MerchLitt_Input_ha] AS YTs_Incr
FROM Merch_In

```python

```

```python

```
