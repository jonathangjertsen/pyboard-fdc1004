# pyboard-fdc1004
PyBoard driver for the Texas Instruments FDC1004 Capacitance-to-Digital converter. I ended up not using the FDC1004 very much, so I have no idea if it works in its current state! Pull requests welcome :)

## Usage
Drop `fdc1004stream.py` into the PyBoard filesystem and `import fdc1004stream` in `main.py`. The FDC1004 will be initialized at import time (TODO: refactor to use an initialization function instead). Use `fdc1004stream.get_cap(0)` to get the capacitance of channel 0, `fdc1004stream.get_cap(1)` to get the capacitance of channel 1, etc. The unit is pF.
