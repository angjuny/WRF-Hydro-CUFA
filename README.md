# WRF-Hydro-CUFA (Coastal-Urban Flood Applications)
## Description
Here, I have modified the WRF-Hydro® v5.2.0 (https://github.com/NCAR/wrf_hydro_nwm_public/releases/tag/v5.2.0) codes to study the floodwater interactions with a water boundary, surface and subsurface hydrologic processes, and stormwater drainage in coastal-urban systems. With the channel routing module set off, water levels can be imposed with respect to time and space, particularly along water boundaries such as coasts/rivers/creeks (as surface heads on grounds). In addition, I have coupled with the SWMM (https://www.epa.gov/water-research/storm-water-management-model-swmm) model to include the effects of stormwater drainage on floods.


## Code Usage
  1. The uploaded codes in this repository should be added/replaced at the corresponding source directories before compiling the WRF-Hydro® v5.2.0 codes.
  2. The SWMM Shared Object (.so) and Executable files should be placed in the following paths:  
     /(Working Directory)/CPL_SWMM5/00###/libswmm5.so & runswmm5
  3. The additional input folders/files should be provided with a structure in that 'input' folder:  
     /BCHEAD                            : input directory for water levels
     
     > /BCHEAD/YYYYMMDDHH.BCHEAD_DOMAIN1  
     >> var HEADMASK(y, x): 1 = controlled boundary, otherwise 0,  
     >> var HEAD(y, x): water levels (as surface heads on grounds) at HEADMASK(y, x) = 1
     
     /CPL_SWMM5/                        : input directory for stormwater drainage
     
     > /CPL_SWMM5/CPL_SWMM5.INPFORM       : SWMM5 input that includes all stormwater drainage components
     
     > /CPL_SWMM5/CPL_SWMM5.nc
     >> var ELEVOFFSET: offset in datum between TOPOGRAPHY(y, x) in Fulldom_hires.nc and Elevations in CPL_SWMM.INPFROM,  
     >> var N_NODELAYER: maximum number of stormwater junctions (inlets & outfalls) in one grid cell,  
     >> var NODEMASK#(y, x): 1 = coupled grid cell, otherwise 0,  
     >> var NODEINDEX#(y, x): i = i-th stormwater junction (inlets & outfalls)
     
     > /CPL_SWMM5/00###/CPL_SWMM5.INPFORM : SWMM5 input partition that will be assigned to solve with Processor 00###


## Documentation
For more details about the model implementation and validations, we encourage you to read the following reference that is currently in preparation for publication:
  - Son, Y., Di Lorenzo, E., & Luo, J. (2023). WRF-Hydro-CUFA: A scalable and adaptable coastal-urban flood model based on the WRF-Hydro and SWMM models. *Manuscript in preparation*.


## Notice
The WRF-Hydro modeling system was developed at the National Center for Atmospheric Research (NCAR) through grants from the National Aeronautics and Space Administration (NASA) and the National Oceanic and Atmospheric Administration (NOAA). NCAR is sponsored by the United States National Science Foundation.
