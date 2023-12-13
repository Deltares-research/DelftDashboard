from delftdashboard.app import app
from delftdashboard.operations import map

class SfincsHmtInfiltration():
    long_name = "modelmaker_sfincs_hmt"
    def select(*args):
        # De-activate existing layers
        map.update()
        app.map.layer["sfincs_hmt"].layer["grid"].activate()


    def select_infiltration_method(*args):
        pass

    def select_cn_method(*args):
        pass

    def select_qinf_method(*args):
        pass


    def generate_infiltration(self, *args):
        app.toolbox[self.long_name].generate_infiltration()
