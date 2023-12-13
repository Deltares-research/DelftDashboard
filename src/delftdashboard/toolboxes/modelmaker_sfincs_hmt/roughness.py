from delftdashboard.app import app
from delftdashboard.operations import map

class SfincsHmtRoughness():
    long_name = "modelmaker_sfincs_hmt"

    def select(self, *args):
        # De-activate existing layers
        map.update()
        app.map.layer["sfincs_hmt"].layer["grid"].activate()


    def select_roughness_method(self, *args):
        pass


    def add_selected_manning_dataset(self, *args):
        group = self.long_name
        index = app.gui.getvar(group, "roughness_methods_index")

        if index == 1:
            lulc = app.gui.getvar(group, "lulc_dataset_names")[
                app.gui.getvar(group, "lulc_dataset_index")
            ]
            reclass_table = app.gui.getvar(group, "lulc_reclass_table")
            if lulc not in app.gui.getvar(group, "selected_manning_dataset_names"):
                dataset = {"lulc": lulc, "reclass_table": reclass_table}
                # if reclass_table is the default value, set to None
                if reclass_table == f"{lulc}_mapping.csv":
                    dataset.pop("reclass_table")
                app.toolbox[self.long_name].selected_manning_datasets.append(
                    dataset
                )
        elif index == 2:
            manning = app.gui.getvar(group, "manning_dataset_names")[
                app.gui.getvar(group, "manning_dataset_index")
            ]
            if manning not in app.gui.getvar(group, "selected_manning_dataset_names"):
                dataset = {"manning": manning}
                app.toolbox[self.long_name].selected_manning_datasets.append(
                    dataset
                )

        app.gui.setvar(
            group,
            "selected_manning_dataset_index",
            len(app.toolbox[self.long_name].selected_manning_datasets) - 1,
        )
        self.update()


    def remove_selected_manning_dataset(self, *args):
        if len(app.toolbox[self.long_name].selected_manning_datasets) == 0:
            return
        group = self.long_name
        index = app.gui.getvar(group, "selected_manning_dataset_index")
        app.toolbox[self.long_name].selected_manning_datasets.pop(index)
        self.update()


    def select_selected_manning_dataset(self, *args):
        self.update()


    def select_manning_dataset(self, *args):
        pass


    def select_lulc_dataset(self, *args):
        group = self.long_name
        index = app.gui.getvar(group, "lulc_dataset_index")
        landuse_names = app.gui.getvar(group, "lulc_dataset_names")

        if len(landuse_names) > 0:
            name = landuse_names[index]
            app.gui.setvar(
                self.long_name, "lulc_reclass_table", f"{name}_mapping.csv"
            )


    def select_reclass_table(self, *args):
        fname = app.gui.window.dialog_open_file(
            "Select mapping file to convert landuse/ladncover to Mannings' n",
            filter="*.csv",
        )
        if fname[0]:
            app.gui.setvar(self.long_name, "lulc_reclass_table", fname[0])


    def move_up_selected_manning_dataset(self, *args):
        group = self.long_name
        index = app.gui.getvar(group, "selected_manning_dataset_index")

        # if there is only one dataset, do nothing
        if len(app.toolbox[self.long_name].selected_manning_datasets) < 2:
            return
        # if the index is the first one, do nothing
        if index == 0:
            return
        # if "Constant values", do nothing
        if (
            app.toolbox[self.long_name].selected_manning_datasets[index]
            == "Constant values"
        ):
            return

        i0 = index
        i1 = index - 1
        (
            app.toolbox[self.long_name].selected_manning_datasets[i0],
            app.toolbox[self.long_name].selected_manning_datasets[i1],
        ) = (
            app.toolbox[self.long_name].selected_manning_datasets[i1],
            app.toolbox[self.long_name].selected_manning_datasets[i0],
        )
        app.gui.setvar(group, "selected_manning_dataset_index", index - 1)
        self.update()


    def move_down_selected_manning_dataset(self, *args):
        group = self.long_name
        index = app.gui.getvar(group, "selected_manning_dataset_index")
        # if there is only one dataset, do nothing
        if len(app.toolbox[self.long_name].selected_manning_datasets) < 2:
            return
        # if the index is the last one, do nothing
        if index == len(app.toolbox[self.long_name].selected_manning_datasets) - 1:
            return
        # if "Constant values" is below, do nothing
        if (
            app.toolbox[self.long_name].selected_manning_datasets[index + 1]
            == "Constant values"
        ):
            return

        i0 = index
        i1 = index + 1
        (
            app.toolbox[self.long_name].selected_manning_datasets[i0],
            app.toolbox[self.long_name].selected_manning_datasets[i1],
        ) = (
            app.toolbox[self.long_name].selected_manning_datasets[i1],
            app.toolbox[self.long_name].selected_manning_datasets[i0],
        )
        app.gui.setvar(group, "selected_manning_dataset_index", index + 1)
        self.update()


    def update(self):
        group = self.long_name
        selected_names = []
        nrd = len(app.toolbox[self.long_name].selected_manning_datasets)
        if nrd > 0:
            for dataset in app.toolbox[self.long_name].selected_manning_datasets:
                if "lulc" in dataset:
                    selected_names.append(dataset["lulc"])
                elif "manning" in dataset:
                    selected_names.append(dataset["manning"])
            # also add "Constant values" to the list
            selected_names.append("Constant values")
            app.gui.setvar(group, "selected_manning_dataset_names", selected_names)
            index = app.gui.getvar(group, "selected_manning_dataset_index")
            if index > nrd - 1:
                index = nrd - 1
            dataset = app.toolbox[self.long_name].selected_manning_datasets[index]

        else:
            app.gui.setvar(group, "selected_manning_dataset_names", ["Constant values"])
            app.gui.setvar(group, "selected_manning_dataset_index", 0)

        app.gui.setvar(group, "nr_selected_manning_datasets", nrd)


    def generate_manning(self, *args):
        app.toolbox[self.long_name].generate_manning()
