# Author: silentfamiliar@matrix

def keyTo128BitAddress(key):
    key260bits = int("1" + key, 16) # "1" to avoid trimming leading 0s
    source_cursor = 4 # skip the "1"

    # loop over each bit while NOT(bit) is 1
    while (1 & ~(key260bits >> (260 - source_cursor - 1))) == 1:
        source_cursor = source_cursor + 1

    ones_count = source_cursor - 4 # 1s to count minus 4 which was our initial offset
    source_cursor = source_cursor + 1 # skipping trailing 0

    dest = (0x2 << 8) | ones_count # set header
    bitsToAdd = 128 - 16 # header was 2 bytes which is 16 bit

    # append needed amount of NOT key starting from source_cursor
    dest = (dest << bitsToAdd) | ((2**bitsToAdd - 1) & ~(key260bits >> (260 - source_cursor - bitsToAdd)))

    # the long addr
    dest_hex = "0" + hex(dest)[2:]
    # format ipv6 128bit addr

    addr = ""
    for i in range(8):
        piece = int(dest_hex[i*4:i*4+4], 16)
        if (len(addr) != 0) and not (addr[len(addr)-2:len(addr)] == "::"):
            addr += ":"
        if (piece != 0):
            addr += hex(piece)[2:]

    return addr
