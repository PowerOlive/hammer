#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  generate_properties.py
#  
#  Copyright 2017 Edward Wang <edward.c.wang@compdigitec.com>
#  Helper script to generate properties for hammer-vlsi tool classes.

from collections import namedtuple
import sys

InterfaceVar = namedtuple("InterfaceVar", 'name type desc')

Interface = namedtuple("Interface", 'module inputs outputs')

def generate_from_list(template, lst):
    def format_var(var):
        if var.type.startswith("Iterable"):
            var_type_instance_check = "Iterable"
        else:
            var_type_instance_check = var.type
        return template.format(var_name=var.name, var_type=var.type, var_desc=var.desc, var_type_instance_check=var_type_instance_check)
    return map(format_var, lst)

def generate_interface(interface: Interface):
    template = """
@property
def {var_name}(self) -> {var_type}:
    \"""
    Get the {var_desc}.

    :return: The {var_desc}.
    \"""
    try:
        return self._{var_name}
    except AttributeError:
        raise ValueError("Nothing set for the {var_desc} yet")

@{var_name}.setter
def {var_name}(self, value: {var_type}) -> None:
    \"""Set the {var_desc}.\"""
    if not isinstance(value, {var_type_instance_check}):
        raise TypeError("{var_name} must be a {var_type}")
    self._{var_name} = value # type: {var_type}
"""

    output = []
    output.append("### Generated interface %s ###" % (interface.module))
    output.append("### Inputs ###")
    output.extend(generate_from_list(template, interface.inputs))
    output.append("")
    output.append("### Outputs ###")
    output.extend(generate_from_list(template, interface.outputs))
    return output

def main(args):
    HammerSynthesisTool = Interface(module="HammerSynthesisTool",
        inputs=[
            InterfaceVar("input_files", "Iterable[str]", "input collection of source RTL files (e.g. *.v)"),
            InterfaceVar("top_module", "str", "top-level module")
        ],
        outputs=[
            InterfaceVar("output_files", "Iterable[str]", "output collection of mapped (post-synthesis) RTL files")
            # TODO: model CAD junk
        ]
    )

    HammerPlaceAndRouteTool = Interface(module="HammerPlaceAndRouteTool",
        inputs=[
            InterfaceVar("input_files", "Iterable[str]", "input post-synthesis netlist files"),
            InterfaceVar("top_module", "str", "top RTL module")
        ],
        outputs=[
            # TODO: model CAD junk
        ]
    )

    output = []
    output.extend(generate_interface(HammerSynthesisTool))
    output.append("")
    output.extend(generate_interface(HammerPlaceAndRouteTool))
    print("\n".join(output))
 
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))