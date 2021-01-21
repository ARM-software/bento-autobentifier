#
# The Autobentifier
#
# Copyright (c) 2020, Arm Limited. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#

import glob
import importlib
import os
import shutil
import sys

#Make sure retdec path is added to PYTHONPATH
rd_decompiler = importlib.import_module('retdec-decompiler')

#python ~/bin/bin/retdec-decompiler.py --arch arm -o dump.ll ~/git/research/device-provisioning/dpp/whd/BUILD/CY8CPROTO_062_4343W/GCC_ARM/mbed-os/experimental/briareus/briareus.o
#retdec-decompiler.py --backend-emit-cg demo.elf

class Decompiler:
  def __init__(self, input_file, bb_dir="bb", no_memory_limit=False, cleanup=False):
    self.input_file_path = input_file
    self.intput_file_dir = os.path.dirname(input_file)
    self.input_file = os.path.basename(input_file)
    self.bb_dir = bb_dir
    self.no_memory_limit = no_memory_limit
    self.cleanup = cleanup
    self.default_args = [ "--backend-emit-cg", "--backend-keep-library-funcs", "--backend-no-var-renaming" ]

  def decompile(self):
    os.makedirs(self.bb_dir, exist_ok=True)
    shutil.copy2(self.input_file_path, self.bb_dir)
    input_file = os.path.join(self.bb_dir, self.input_file)
    args = self.default_args
    if self.cleanup:
      args.append("--cleanup")
    if self.no_memory_limit:
      args.append("--no-memory-limit")
    args.append(input_file)
    retdec_decompiler = rd_decompiler.Decompiler(args)
    return retdec_decompiler.decompile()


if __name__ == "__main__":
    #decompiler = rd_decompiler.Decompiler(sys.argv[1:])
    decompiler = Decompiler(sys.argv[1])
    sys.exit(decompiler.decompile())

