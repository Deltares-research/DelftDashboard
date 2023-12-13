from delftdashboard.app import app
from delftdashboard.operations import map

class SfincsHmtSubgrid():
    long_name = "modelmaker_sfincs_hmt"

    def select(*args):
        # De-activate existing layers
        map.update()
        app.map.layer["sfincs_hmt"].layer["grid"].activate()
        app.map.layer["sfincs_hmt"].layer["bed_levels"].show()
        app.map.layer["sfincs_hmt"].layer["bed_levels"].activate()    


    def edit_nr_subgrid_pixels(self, *args):
        subgrid_buffer_cells = app.gui.getvar(
            self.long_name, "nr_subgrid_pixels"
        ) * app.gui.getvar(self.long_name, "bathymetry_dataset_buffer_cells")
        app.gui.setvar(
            self.long_name, "subgrid_buffer_cells", subgrid_buffer_cells
        )


    def generate_subgrid(self, *args):
        app.toolbox[self.long_name].generate_subgrid()
