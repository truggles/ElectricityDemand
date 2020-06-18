
# Demand data

The raw demand files from NYISO and ERCOT are located in my Carnegie
gDrive:
 * `Reliability/Inputs/ERCOT_DEMAND_1998-2020.zip`
 * `Reliability/Inputs/NYISO_All_Data_2002-2019.zip`

## NYISO

data is fetched using `NYISO_download_and_unzip.sh`

## ERCOT 

see: `ERCOT_demand_prep.ipynb`

data is from http://www.ercot.com/gridinfo/load/load_hist
 * The 2001 data year is missing
 * 1993-2000 uses a .txt format...
 * 1996 is from http://www.ercot.com/content/gridinfo/load/load_hist/96load.txt
 * 1995 is a crazy format
 * 1997 is poor format
 * 1998 is workable
 * 1999
    * deleted row for y1999	m4	d4	h3 and added the few totals there to previous hour (DST)
    * had to interpolate for a subregion for y1999	m3	d21	h24
 * 2000
    * deleted row for y2000	m4	d2	h3, it was fully zero (DST)
    * had to change the repeat hour for DST from 3am in Oct 31 to 2am to get picked up by code


# PJM

data is from https://dataminer2.pjm.com/feed/hrl_load_metered

historical data guide: https://www.pjm.com/-/media/etools/data-miner-2/data-miner-2-historic-data-guide.ashx?la=en

I exported the csv files in 1 year chuncks from the data viewer.  I could not get the API registration email to work.

PJM reports timestamps based on: `datetime_beginning_utc`, I could not find documentation on this. However, I took
a PJM demand time series and plotted it against EIA's which uses the time at the end of the hour. The profiles
were 1 hour shifted. I will add 1 hour to all PJM timestamps to align with MEM and other BAs.

There are a few missing hours in the 1993-2019 data record (where idx is based on
stitching all these together and time is UTC):
Gap at idx 7273 for times 1993-10-31 05:00:00 --> 1993-10-31 07:00:00
Gap at idx 16008 for times 1994-10-30 05:00:00 --> 1994-10-30 07:00:00
Gap at idx 24743 for times 1995-10-29 05:00:00 --> 1995-10-29 07:00:00
Gap at idx 33478 for times 1996-10-27 05:00:00 --> 1996-10-27 07:00:00
Gap at idx 42213 for times 1997-10-26 05:00:00 --> 1997-10-26 07:00:00
Gap at idx 50948 for times 1998-10-25 05:00:00 --> 1998-10-25 07:00:00
Gap at idx 59851 for times 1999-10-31 05:00:00 --> 1999-10-31 07:00:00
Gap at idx 77322 for times 2001-10-28 05:00:00 --> 2001-10-28 07:00:00
Gap at idx 79631 for times 2002-02-01 11:00:00 --> 2002-02-01 13:00:00
Gap at idx 80294 for times 2002-03-01 03:00:00 --> 2002-03-01 05:00:00
Gap at idx 80932 for times 2002-03-27 18:00:00 --> 2002-03-28 05:00:00
Gap at idx 89926 for times 2003-04-06 22:00:00 --> 2003-04-07 00:00:00
Gap at idx 89949 for times 2003-04-07 22:00:00 --> 2003-04-08 00:00:00
Gap at idx 95262 for times 2003-11-15 08:00:00 --> 2003-11-15 10:00:00
Gap at idx 103681 for times 2004-10-31 04:00:00 --> 2004-10-31 07:00:00
Gap at idx 147527 for times 2009-11-01 04:00:00 --> 2009-11-01 07:00:00

Because PJM's demand significantly changed between 2004 and 2006, from mean of approx 30GW to 80GW
we will ignore demand prior to 2006.  Therefore, I fix the last mentioned demand gap in 2009 only
where the PJM RTO demand is missing for 2 hours. Linearly interpolate between
UTC end time    demand (MW)
11/1/09 5:00	58086.021
11/1/09 8:00	53372.809

(58086.021 - 53372.809) / 3. = 1571.071

UTC end time    demand (MW)
11/1/09 5:00	58086.021
11/1/09 6:00	58086.021 - 1 * 1571.071 = 56514.95
11/1/09 7:00	58086.021 - 2 * 1571.071 = 54943.879
11/1/09 8:00	53372.809

# Regarding GeoPandas and Zane's geometry files:

This set of geometries also covers all the FERC 714 years back to 2006, instead of just 2010. We've got all the EIA 861 data working as far back as 2001 now (and so can generate geometries going back as far as 2001 too).

See file planning_areas_ferc714.gpkg.gz in gDrive/Reliability/Inputs
