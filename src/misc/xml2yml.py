# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 10:04:20 2023

@author: mvano
"""

import os
from cht.misc import fileops as fo
import cht.misc.xmlkit as xml
import yaml

def dict2yaml(file_name, dct, sort_keys=False):
    yaml_string = yaml.dump(dct, sort_keys=sort_keys)    
    file = open(file_name, "w")  
    file.write(yaml_string)
    file.close()

def yaml2dict(file_name):
    file = open(file_name,"r")
    dct = yaml.load(file, Loader=yaml.FullLoader)
    return dct


def read_xml_elements(element):
    elds = []
    for el in element:
        eld = {}
        if el.style[0].value == "tabpanel":
            eld["style"] = "tabpanel"            
            lst = el.position[0].value.split()
            eld["position"] = {}
            eld["position"]["x"]      = int(lst[0])
            eld["position"]["y"]      = int(lst[1])
            eld["position"]["width"]  = int(lst[2])
            eld["position"]["height"] = int(lst[3])
            eld["tab"] = []
            for tab in el.tab:
                tb = {}
                tb["string"]   = tab.string[0].value
                if hasattr(tab, "callback"):
                    tb["module"] = "models.sfincs." + tab.callback[0].value
                
                if hasattr(tab, "element"):    
                    if hasattr(tab.element[0], "value"):
                        ff = tab.element[0].value
                        ff = ff.replace('.xml','.yml')
                        tb["element"]  = ff
                    else:                        
                        tb["element"]  = read_xml_elements(tab.element)
                else:
                    tb["element"] = []
                eld["tab"].append(tb)
        elif el.style[0].value == "panel":    
            eld["style"] = "panel"            
            lst = el.position[0].value.split()
            eld["position"] = {}
            eld["position"]["x"]      = int(lst[0])
            eld["position"]["y"]      = int(lst[1])
            eld["position"]["width"]  = int(lst[2])
            eld["position"]["height"] = int(lst[3])
            eld["element"] = read_xml_elements(el.element)
        else:
            keys = el.__dict__.keys()
            for key in keys:
                if key == "dependency":
                    deps = getattr(el, key)
                    eld["dependency"] = []
                    for dep in deps:
                        dpd = {}
                        dpd["action"] = dep.action[0].value
                        dpd["checkfor"] = dep.checkfor[0].value

                        chs = []
                        for chk in dep.check:
                            ch = {}
                            if hasattr(chk, "variable"):
                                ch["variable"]  = chk.variable[0].value
                            if hasattr(chk, "varname"):
                                ch["variable"]  = chk.varname[0].value
                            if hasattr(chk, "vargroup"):
                                ch["variable_group"]  = chk.vargroup[0].value
                            ch["operator"] = chk.operator[0].value
                            ch["value"]    = chk.value[0].value
                            chs.append(ch)

                        dpd["check"] = chs

                        eld["dependency"].append(dpd)
                elif key == "position":
                    lst = el.position[0].value.split()
                    eld["position"] = {}
                    eld["position"]["x"]      = int(lst[0])
                    eld["position"]["y"]      = int(lst[1])
                    if len(lst)>2:
                        eld["position"]["width"]  = int(lst[2])
                    if len(lst)>3:
                        eld["position"]["height"] = int(lst[3])                    
                elif key == "callback":
                    eld["method"] = el.callback[0].value
                elif key == "varname":
                    eld["variable"] = el.varname[0].value
                elif key == "vargroup":
                    eld["variable_group"] = el.vargroup[0].value
                elif key == "listtext":
                    txt = []
                    for tx in el.listtext:
                        txt.append(tx.value)
                    eld["option_string"] = txt    
                elif key == "listvalue":
                    txt = []
                    for tx in el.listvalue:
                        txt.append(tx.value)
                    eld["option_value"] = txt    
                elif key == "type":
                    pass
                elif key == "column":
                    pass
                elif key == "option1":
                    pass
                else:    
                    v = getattr(el, key)
                    eld[key] = v[0].value
        elds.append(eld)                    
    return elds    



pth = "c:\\work\\checkouts\\git\\DelftDashboard\\src\\models\\sfincs\\config"

files = fo.list_files(os.path.join(pth, "*.xml"))

for file in files:
    name = os.path.basename(file)[0:-4]
    xml_obj = xml.xml2obj(file)
    element = xml_obj.element
    dct = {}
    dct["element"] = read_xml_elements(element)

    fout = os.path.join(pth, name + ".yml")    
    dict2yaml(fout, dct)
