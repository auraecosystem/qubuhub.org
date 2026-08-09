class SDXF:
    DATATYPE_MAP = {
        "STRUCTURED": 0x01,
        "NUMERIC": 0x02,
        "CHAR": 0x03
    }
    DATATYPE_REVERSE = {v: k for k, v in DATATYPE_MAP.items()}

    def __init__(self, buffersize=1000):
        self.buffer = bytearray(buffersize)
        self.offset = 0
        self.stack = []

    def create(self, chunk_id: int, datatype: str, value=None):
        """Creates a new SDXF chunk (elementary or structured container)."""
        header_pos = self.offset
        dtype_byte = self.DATATYPE_MAP.get(datatype, 0x00)
        
        self.offset += 6  # 2 bytes ID + 1 byte Type + 3 bytes Length
        payload_start = self.offset

        if datatype == "STRUCTURED":
            self.stack.append((header_pos, chunk_id, dtype_byte, payload_start))
        else:
            if datatype == "NUMERIC":
                payload = int(value).to_bytes(4, byteorder='big', signed=True)
            elif datatype == "CHAR":
                payload = str(value).encode('utf-8')
            else:
                payload = b""
            
            self.buffer[self.offset:self.offset + len(payload)] = payload
            self.offset += len(payload)
            self._write_header(header_pos, chunk_id, dtype_byte, len(payload))

    def leave(self):
        """Closes the current open structured container and backfills its length."""
        if not self.stack:
            raise RuntimeError("Unmatched leave() call: No active structure to close.")
        
        header_pos, chunk_id, dtype_byte, payload_start = self.stack.pop()
        payload_len = self.offset - payload_start
        self._write_header(header_pos, chunk_id, dtype_byte, payload_len)

    def _write_header(self, pos, chunk_id, dtype_byte, length):
        self.buffer[pos:pos+2] = chunk_id.to_bytes(2, 'big')
        self.buffer[pos+2] = dtype_byte
        self.buffer[pos+3:pos+6] = length.to_bytes(3, 'big')

    def save(self, filename: str):
        """Saves the compiled SDXF byte buffer directly to disk."""
        with open(filename, "wb") as f:
            f.write(bytes(self.buffer[:self.offset]))
        print(f"SDXF buffer successfully saved to '{filename}' ({self.offset} bytes).")
