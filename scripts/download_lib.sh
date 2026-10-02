#!/usr/bin/env bash
mkdir -p lib vcd netlist
echo "Downloading NanGate 45nm Open Cell Library..."
wget -q -O lib/NangateOpenCellLibrary_typical.lib \
  [https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib](https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/lib/NangateOpenCellLibrary_typical.lib)
wget -q -O lib/NangateOpenCellLibrary.v \
  [https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/verilog/NangateOpenCellLibrary.v](https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/nangate45/verilog/NangateOpenCellLibrary.v)
echo "Done!"
