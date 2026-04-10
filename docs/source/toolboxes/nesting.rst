Nesting
=======

The Nesting toolbox (``nesting``) supports one-way nesting between a
coarser overall model and a finer detail model. The workflow consists of
two steps: Nest 1 creates observation points in the overall model at the
detail model boundary locations, and Nest 2 extracts boundary conditions
from the overall model output.

Nest 1
------

Add observation points from the detail model boundaries to the overall
model.

Parameters
^^^^^^^^^^

Detail Model Type (listbox)
   Select the type of the detail model (e.g. SFINCS, HurryWave).

Select Detail Model
   Browse and load a detail model folder.

Obs Point Prefix
   Prefix for observation point names (e.g. ``nest_``). Only enabled after
   a detail model is loaded.

Actions
^^^^^^^

Make Observation Points
   Create observation points in the currently active (overall) model at
   the boundary locations of the loaded detail model. These points ensure
   that the overall model writes output at the locations needed for
   nesting.


Nest 2
------

Extract boundary conditions from the overall model output and apply them
to the detail model.

Parameters
^^^^^^^^^^

Overall Model Type (listbox)
   Select the type of the overall model (e.g. SFINCS, Delft3D-FM).

Select Overall Model
   Browse and load an overall model folder (which must contain completed
   simulation output).

Obs Point Prefix
   Prefix used to identify the nesting observation points in the overall
   model output.

Water Level Correction (m)
   Constant offset (in metres) applied to the extracted water levels. Can
   be used to correct for datum differences between models.

Actions
^^^^^^^

Get Boundary Conditions
   Extract time series from the overall model output at the observation
   points and write boundary condition files for the detail model.
