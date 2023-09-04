import struct


class ByteBuffer:
    def __init__(self, length: int):
        self.data = bytearray(length)
        self.position = 0

    @staticmethod
    def fromOther(data):
        buffer = ByteBuffer(0)
        buffer.data = data
        buffer.position = 0
        return buffer

    def read24_bit_int(self):
        return (self.read_unsigned_byte() << 16) + (self.read_unsigned_byte() << 8) + self.read_unsigned_byte()

    def read_int(self):
        self.position += 4
        return ((self.data[self.position - 3] & 0xff) << 16) + (self.data[self.position - 1] & 0xff) + ((self.data[self.position - 2] & 0xff) << 8) + ((self.data[self.position - 4] & 0xff) << 24)

    def read_unsigned_short(self):
        self.position += 2
        return ((self.data[self.position - 2] & 0xff) << 8) + (self.data[self.position - 1] & 0xff)

    def read_short(self):
        self.position += 2
        value = ((self.data[self.position - 2] & 0xff) << 8) + (self.data[self.position - 1] & 0xff)
        if value > 32767:
            value -= 65536
        return value

    def read_float(self):
        int_value = self.read_int()
        float_bytes = struct.pack('I', int_value)
        return struct.unpack('f', float_bytes)[0]


    def read_unsigned_byte(self):
        value = self.data[self.position] & 0xff
        self.position += 1
        return value

    def read_signed_byte(self):
        value = self.data[self.position]
        self.position += 1
        return value

    def read_signed_smart_minus_one(self):
        temp = self.data[self.position] & 0xff
        if temp < 128:
            value = self.read_unsigned_byte() - 1
        else:
            value = self.read_unsigned_short() - 32769
        return value


    def read_smart_2(self):
        temp = self.data[self.position] & 0xff
        if temp >= 0:
            value = self.read_unsigned_byte() - 0x40
        else:
            value = self.read_unsigned_short() - 0xc000
        return value

    def readUnsignedSmart(self):
        temp = self.data[self.position] & 0xff
        if temp < 128:
            value = self.read_unsigned_byte()
        else:
            value = self.read_unsigned_short() - 32768
        return value


    @property
    def readSignedSmart(self):
        temp = self.data[self.position] & 0xff
        if temp < 128:
            value = self.read_unsigned_byte() - 0x40
        else:
            value = self.read_unsigned_short() - 0xc000
        return value


    def put_byte(self, value):
        packed = value.to_bytes(1, 'big', signed=True)
        self.put_bytes(packed, 0, 1)


    def put_short(self, value):
        value &= 0xFFFF
        packed = value.to_bytes(2, 'big', signed=True)
        self.put_bytes(packed, 0, 2)


    def put_signed_smart(self, value):
        if -64 <= value < 64:
            self.put_byte(value + 64)
        elif -32768 <= value < 32768:
            self.put_short(value + 0xC000)
        else:
            raise ValueError("Value out of range for signed smart")

    def set_pos(self, pos):
        self.position = pos

    def getData(self):
        return self.data

    def put_bytes(self, src, offset, length):
        self.data[self.position:self.position + length] = src[offset:offset + length]
        self.position += length

    def getArray(self):
        return self.data

    def dec_position(self, amount):
        self.position -= amount

    def inc_position(self, amount):
        self.position += amount

    def get_pos(self):
        return self.position

