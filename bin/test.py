from binascii import unhexlify, hexlify
seconds = 520
   # comfoconnect.cmd_rmi_request(CMD_FAN_MODE_HIGH)  # Set fan speed to 3
    #print ("{0:12b}".format(seconds))
#print(  )

# s = str("{:012x}".format(seconds))
# print(s)
# sx = r"\x" + r"\x".join(s[n : n+2] for n in range(0, len(s), 2))


# bytestring = sx

# print("Bytestring to send to zehnder: " + bytestring)

# s_new: bytes = (b'\x84\x15\x01\x06' + bytes(bytestring, encoding="raw_unicode_escape") + b'\x00\x00\x03')

# print("s_new: " +str( s_new))

# hx = unhexlify(s)


# print(hx)
# print(sx)
# print('\x84\x15\x01\x06' + sx + '\x00\x00\x03')

    # 8415 0106 0000 0000 5802 0000 03	
    # Boost mode: start for 10m (= 600 seconds = 0x0258)

boostbytes: bytes = bytes('\x84\x15\x01\x06', encoding="raw_unicode_escape")
#boostbytes = boostbytes.append(bytes(format(seconds, '012b'), 'utf-8')
s = str("{:012x}".format(seconds))
boostbytes = boostbytes.join(hex('\x00', encoding="raw_unicode_escape"))
# boostbytes += b'\x00\x00\x03'

print(boostbytes)