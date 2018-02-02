#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  nop.py
#  No-op place and route tool.
#
#  Copyright 2018 Edward Wang <edward.c.wang@compdigitec.com>

from hammer_vlsi import HammerPlaceAndRouteTool


class Nop(HammerPlaceAndRouteTool):
    def do_run(self) -> bool:
        # Do nothing
        return True


tool = Nop()
