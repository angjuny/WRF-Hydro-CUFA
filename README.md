# WRF-Hydro-CUFA (Coastal-Urban Flood Applications)
## Description
Here, I have modified the WRF-Hydro® v5.2.0 (https://github.com/NCAR/wrf_hydro_nwm_public/releases/tag/v5.2.0) codes to study the floodwater interactions with a water boundary, surface and subsurface hydrologic processes, and stormwater drainage in coastal-urban systems. With the channel routing module set off, water levels can be imposed with respect to time and space, particularly along water boundaries such as coasts/rivers/creeks (as surface heads on grounds). In addition, I have coupled with the SWMM (https://www.epa.gov/water-research/storm-water-management-model-swmm) model to include the effects of stormwater drainage on floods.


## Documentation
For more details about the model implementation and validations, we encourage you to read the following reference that is currently in preparation for publication:
  - Son, Y., Di Lorenzo, E., & Luo, J. (2023). WRF-Hydro-CUFA: A scalable and adaptable coastal-urban flood model based on the WRF-Hydro and SWMM models. Manuscript in preparation.


## Code Usage
  1. The uploaded codes in this repository should be added/replaced at the corresponding source directories before compiling the WRF-Hydro® v5.2.0 codes.
  2. The SWMM executable that is compiled in the same Linux system should be added in the following paths:
  3. The additional input folders/files should be provided as shown in '':


## Notice
The WRF-Hydro modeling system was developed at the National Center for Atmospheric Research (NCAR) through grants from the National Aeronautics and Space Administration (NASA) and the National Oceanic and Atmospheric Administration (NOAA). NCAR is sponsored by the United States National Science Foundation.
