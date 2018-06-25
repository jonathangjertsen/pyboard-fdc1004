from pyb import I2C
import pyb
import sys

DELAY_BETWEEN_SAMPLES = 0
DO_SCAN = False
FDC_ADDR = 80
CAP_CFG = [0x0C, 0x0d, 0xff]
ALL_REGISTERS = list(range(0x15)) + [0xFE, 0xFF]

data_in = bytearray(2)

i2c = I2C(1, I2C.MASTER)

def data_bin():
    msb = bin(data_in[0])[2:]
    lsb = bin(data_in[1])[2:]
    msb = "0" * (8-len(msb)) + msb
    lsb = "0" * (8-len(lsb)) + lsb
    return msb + " " + lsb

def data_hex():
    msb = hex(data_in[0])[2:]
    lsb = hex(data_in[1])[2:]
    msb = "0" * (2-len(msb)) + msb
    lsb = "0" * (2-len(lsb)) + lsb
    return "0x" + msb + lsb

def data_dec():
    return data_in[0] * 256 + data_in[1]

def read_reg(reg):
    try:
        i2c.send(reg, addr=FDC_ADDR)
        i2c.recv(data_in, addr=FDC_ADDR)
    except OSError:
        print("FAILED reading from register " + hex(reg))
        raise

def regscan(registers=None, do_print=False):
    if registers is None:
        registers = ALL_REGISTERS
    for idx, pointerregister in enumerate(registers):
        read_reg(pointerregister)
        if do_print:
            print("\t" + str(hex(pointerregister)) + ": " + data_bin() + " = " + data_hex() + " = " + str(data_dec()))

def get_cap_code(channel):
    the_bytes = [0, 0, 0, 0]
    msb_reg = channel << 1
    lsb_reg = msb_reg + 1
    read_reg(msb_reg)
    the_bytes[0:2] = list(data_in)
    read_reg(lsb_reg)
    the_bytes[2:4] = list(data_in)
    return the_bytes[0] * (2**24) + the_bytes[1] * (2**16) + the_bytes[2] * (2**8) + the_bytes[3]

def get_cap(channel):
    code = get_cap_code(channel)

    # Discard 8 lowest bits
    code >>= 8

    # Get two's complement for the remaining 24-bit value
    mask = 2 ** (24 - 1)
    twos_comp = -(code & mask) + (code & ~mask)

    # That value divided by 2^19 is the capacitance in pF
    return twos_comp / (2**19)

setup_sequence = (
    ("Reset", [0x0C, 0x80, 0x00]),
    ("Measurement 1", [0x08, 0x1c, 0x00]),
    ("Measurement 2", [0x09, 0x3c, 0x00]),
    ("Measurement 3", [0x0a, 0x5c, 0x00]),
    ("Measurement 4", [0x0b, 0x7c, 0x00]),
    ("Cap config", CAP_CFG),
)

# Make sure it is ready
while True:
    check_ready = True
    if DO_SCAN:
        slaves = i2c.scan()
        print("I2C device addresses: " + ", ".join([str(slave) for slave in slaves]))
        if not FDC_ADDR in slaves:
            check_ready = False
    if check_ready:
        if (i2c.is_ready(FDC_ADDR)):
            print("Ready!")
            break
        else:
            print("FDC is not ready.")
    pyb.delay(1000)

# Setup
print("Starting setup:")
for cmd in setup_sequence:
    print("\t" + cmd[0])
    i2c.send(bytearray(cmd[1]), addr=FDC_ADDR)
print("Setup done")

# Do checks
print("Starting checks")
regscan(do_print=True)

if __name__ == "__main__":
    print("Starting streaming")
    while True:
        if DELAY_BETWEEN_SAMPLES:
            pyb.delay(DELAY_BETWEEN_SAMPLES)
        print(str(int(get_cap(0)*1000)) + " fF")
