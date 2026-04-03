Model Database
==============

The Model Database toolbox (``model_database``) manages collections of
pre-configured model domains. Users can browse existing domains, view them
on the map, and register new domains.

View Domain Database
--------------------

Browse and display model domains organized by collection.

Parameters
^^^^^^^^^^

Available Collections (listbox)
   List of all available model collections.

Selected Collections (listbox)
   Collections currently shown on the map.

Available Domains (listbox)
   List of domains in the selected collections.

SFINCS (checkbox)
   Toggle visibility of SFINCS domains on the map.

HurryWave (checkbox)
   Toggle visibility of HurryWave domains on the map.

Actions
^^^^^^^

Show ->
   Add the selected collection to the displayed list.

<- Hide
   Remove the selected collection from the displayed list.

Load Domain
   Load the selected domain into the application as the active model.


Add Domain
----------

Register a new model domain in the database.

Parameters
^^^^^^^^^^

Name
   Domain name.

Type
   Model type (e.g. sfincs, hurrywave).

EPSG
   Coordinate reference system EPSG code.

Station
   Associated station name.

Flow nested
   Flow nesting relationship identifier.

Spinup time
   Flow model spin-up time.

Flood map (checkbox)
   Enable flood map generation for this domain.

Water level map (checkbox)
   Enable water level map generation.

Precipitation map (checkbox)
   Enable precipitation map generation.

Choose collection (dropdown)
   Select the collection to add the domain to.

Actions
^^^^^^^

Write model.toml
   Write the domain configuration to a TOML file in the model directory.
