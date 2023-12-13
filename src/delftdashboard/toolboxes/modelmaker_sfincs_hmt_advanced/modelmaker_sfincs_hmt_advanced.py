from delftdashboard.toolboxes.modelmaker_sfincs_hmt.modelmaker_sfincs_hmt import Toolbox as simpleToolbox

from delftdashboard.toolboxes.modelmaker_sfincs_hmt_advanced.domain import SfincsHmtDomainAdvanced
from delftdashboard.toolboxes.modelmaker_sfincs_hmt_advanced.mask_active_cells import SfincsHmtCellMaskAdvanced
from delftdashboard.toolboxes.modelmaker_sfincs_hmt_advanced.mask_boundary_cells import SfincsHmtBoundaryMaskAdvanced

class Toolbox(simpleToolbox):
    long_name = "Model Maker Advanced"
    group = "modelmaker_sfincs_hmt_advanced"

    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self._set_init_variables()
        self.domain = SfincsHmtDomainAdvanced()
        self.cell_mask = SfincsHmtCellMaskAdvanced()
        self.boundary_mask = SfincsHmtBoundaryMaskAdvanced()
