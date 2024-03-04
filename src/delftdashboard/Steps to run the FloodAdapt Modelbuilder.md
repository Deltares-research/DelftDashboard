## Steps to run the FloodAdapt Modelbuilders

# 1. Download & extract source code
    P:/11207949-dhs-phaseii-floodadapt/Model-builder/FloodAdaptModelBuilder.zip 
    (You should now have a folder with an executable 'FloodAdaptModelBuilder.exe' and a folder '_internals')

# 2. Download & extract data
    P:/11207949-dhs-phaseii-floodadapt/Data/TestingData_SiteVisit_2024 
    (There are 2 folders: 1 for SFINCS (Data.zip) and 1 for DELFTDASHBOARD & FIAT (MB_testing_files.zip))

# 3. Move the data & edit data_catalogs
    SFINCS: 
    - path TestingData_SiteVisit_2024/Data
    - contains: sfincs data + data_catalog
        a)  extract and put the contents of 'Data' into FloodAdaptModelbuilder/_internal/data
        b)  @Roel edit needed? : put 'data_catalog.yml' in FloodAdaptModeBuilders/_internals/delftdashboard/config 
    
    DELFTDASHBOARD: (TestingData_SiteVisit_2024/MB_testing_files/Installation)
    - contains: template data catalogs and 'delftdashboard.ini' (also mapbox_token and census key, but I left those in the executable so they can be ignored)
    - When editing the paths, make sure to point to data_catalogs or data inside '/_internals/'
    - follow the steps in 'Installation/readme.txt' to edit the paths in the data catalog correctly.
    - paste updated 'delftdashboard.ini' in 'FloodAdaptModeBuilders/_internals/delftdashboard/config'

    FIAT: 
    - path: TestingData_SiteVisit_2024/MB_testing_files/Installation & more @Sarah?
    - contains: FIAT data, data_catalog
        c)  @Sarah: where/if to paste hydromt_fiat_data_catalog.yml, Hazus_IWR_curves & JRC_damage_functions

# 4. Run the executable by double clicking on it