class SDXFBuilder:
    DATATYPE_MAP = {
        "STRUCTURED": 0x01,
        "NUMERIC": 0x02,
        "CHAR": 0x03
    }

    def __init__(self, buffersize=1000):
        self.buffer = bytearray(buffersize)
        self.offset = 0
        self.stack = []  # Tracks open structures: (header_pos, chunk_id, dtype_byte, payload_start)

    def create(self, chunk_id: int, datatype: str, value=None):
        header_pos = self.offset
        dtype_byte = self.DATATYPE_MAP.get(datatype, 0x00)
        
        self.offset += 6  # Reserve 6 bytes for header
        payload_start = self.offset

        if datatype == "STRUCTURED":
            self.stack.append((header_pos, chunk_id, dtype_byte, payload_start))
        else:
            if datatype == "NUMERIC":
                payload = int(value).to_bytes(4, byteorder='big', signed=True)
            elif datatype == "CHAR":
                payload = str(value).encode('utf-8')
            else:
                payload = b"\""
            
            self.buffer[self.offset:self.offset + len(payload)] = payload
            self.offset += len(payload)
            self._write_header(header_pos, chunk_id, dtype_byte, len(payload))

    def leave(self):
        if not self.stack:
            raise RuntimeError("Unmatched leave() call: No active structure to close.")
        
        header_pos, chunk_id, dtype_byte, payload_start = self.stack.pop()
        payload_len = self.offset - payload_start
        self._write_header(header_pos, chunk_id, dtype_byte, payload_len)

    def _write_header(self, pos, chunk_id, dtype_byte, length):
        self.buffer[pos:pos+2] = chunk_id.to_bytes(2, byteorder='big')
        self.buffer[pos+2] = dtype_byte
        self.buffer[pos+3:pos+6] = length.to_bytes(3, byteorder='big')

    def get_buffer(self) -> bytes:
        return bytes(self.buffer[:self.offset])


class SDXFParser:
    DATATYPE_MAP_REVERSE = {
        0x01: "STRUCTURED",
        0x02: "NUMERIC",
        0x03: "CHAR"
    }

    def __init__(self, binary_buffer: bytes):
        self.buffer = binary_buffer
        self.offset = 0
        self.stack = []
        self.rc = "SDX_RC_ok"
        self.chunk_id = None
        self.datatype = None
        self.length = 0
        self.value = None
        self.data_offset = 0

    def enter(self):
        if self.datatype != "STRUCTURED":
            raise RuntimeError("Current chunk is not a STRUCTURED type.")
        container_end = self.data_offset + self.length
        self.stack.append(container_end)
        self.offset = self.data_offset
        self.next()

    def next(self) -> bool:
        if self.stack:
            if self.offset >= self.stack[-1]:
                self.rc = "SDX_RC_eof"
                return False
        elif self.offset >= len(self.buffer):
            self.rc = "SDX_RC_eof"
            return False

        self.chunk_id = int.from_bytes(self.buffer[self.offset:self.offset+2], 'big')
        dtype_byte = self.buffer[self.offset+2]
        self.datatype = self.DATATYPE_MAP_REVERSE.get(dtype_byte, "UNKNOWN")
        self.length = int.from_bytes(self.buffer[self.offset+3:self.offset+6], 'big')
        
        self.data_offset = self.offset + 6
        self.offset = self.data_offset + self.length
        
        payload = self.buffer[self.data_offset:self.data_offset + self.length]
        if self.datatype == "NUMERIC":
            self.value = int.from_bytes(payload, 'big', signed=True)
        elif self.datatype == "CHAR":
            self.value = payload.decode('utf-8')
        else:
            self.value = None
            
        self.rc = "SDX_RC_ok"
        return True

    def leave(self):
        if not self.stack:
            raise RuntimeError("Unmatched leave() call.")
        container_end = self.stack.pop()
        self.offset = container_end
        self.rc = "SDX_RC_ok"


# --- ID Mapping Dictionary ---
ID_MAP = {
    10: "INVOICE",
    11: "INVOICE_NO",
    12: "DATE",
    13: "ADDRESS_SENDER",
    14: "NAME",
    15: "COUNTRY"
}

# 1. Initialize SDXF Structure (Buffersize = 1000)
sdx = SDXFBuilder(buffersize=1000)

# 2. Build the exact invoice structure from your script
sdx.create(10, "STRUCTURED")                           # INVOICE
sdx.create(11, "NUMERIC", 123456)                     # INVOICE_NO
sdx.create(12, "CHAR", "2005-06-17")                  # DATE
sdx.create(13, "STRUCTURED")                          # ADDRESS_SENDER
sdx.create(14, "CHAR", "Peter Somebody")              # NAME
sdx.create(15, "CHAR", "France")                      # COUNTRY
sdx.leave()                                           # leave ADDRESS_SENDER
sdx.leave()                                           # leave INVOICE

# 3. Save the binary output to a file (.sdxf / .bs)
filename = "invoice.sdxf"
binary_data = sdx.get_buffer()
with open(filename, "wb") as f:
    f.write(binary_data)
print(f"Successfully saved SDXF buffer ({len(binary_data)} bytes) to '{filename}'\n")

# 4. Read back and parse the binary file
with open(filename, "rb") as f:
    loaded_data = f.read()

parser = SDXFParser(loaded_data)

print("Parsing Binary Stream:")
parser.next()
print(f"[{ID_MAP.get(parser.chunk_id)}] (STRUCTURE)")
parser.enter()

while parser.rc == "SDX_RC_ok":
    name = ID_MAP.get(parser.chunk_id)
    if parser.datatype == "STRUCTURED":
        print(f"  └── {name} (START STRUCTURE)")
        parser.enter()
        continue
        
    print(f"      ├── {name}: {parser.value}")
    
    if not parser.next():
        parser.leave()
        print(f"  └── (END STRUCTURE)")
        parser.next()
