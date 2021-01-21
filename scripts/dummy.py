#
# The Autobentifier
#
# Copyright (c) 2020, Arm Limited. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#

from llvmlite import binding
binding.initialize()
binding.initialize_all_targets()
binding.initialize_all_asmprinters()
with open("demo.elf.ll") as fp:
    x = fp.read()
xl = binding.parse_assembly(x)
