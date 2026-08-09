class SDXFParser:
    DATATYPE_MAP_REVERSE = {
        0x01: "STRUCTURED",
        0x02: "NUMERIC",
        0x03: "CHAR"
    }

    def __init__(self, binary_buffer: bytes):
        self.buffer = binary_buffer
        self.offset = 0
        self.stack = []  # Tracks container end boundaries
        self.rc = "SDX_RC_ok"
        
        # Current chunk pointers
        self.chunk_id = None
        self.datatype = None
        self.length = 0
        self.value = None
        self.data_offset = 0

    def enter(self):
        """Steps into a structured container chunk."""
        if self.datatype != "STRUCTURED":
            raise RuntimeError("Current chunk is not a STRUCTURED type.")
        
        # Push the outer container's end boundary to stack
        container_end = self.data_offset + self.length
        self.stack.append(container_end)
        
        # Move parsing offset to the start of the inner payload
        self.offset = self.data_offset
        self.next()

    def next(self) -> bool:
        """Advances to the next chunk within the current scope."""
        # Check boundaries if inside a structured container
        if self.stack:
            if self.offset >= self.stack[-1]:
                self.rc = "SDX_RC_eof"
                return False
        elif self.offset >= len(self.buffer):
            self.rc = "SDX_RC_eof"
            return False

        # Parse 6-byte header: [ID: 2 bytes] [Type: 1 byte] [Length: 3 bytes]
        self.chunk_id = int.from_bytes(self.buffer[self.offset:self.offset+2], 'big')
        dtype_byte = self.buffer[self.offset+2]
        self.datatype = self.DATATYPE_MAP_REVERSE.get(dtype_byte, "UNKNOWN")
        self.length = int.from_bytes(self.buffer[self.offset+3:self.offset+6], 'big')
        
        self.data_offset = self.offset + 6
        self.offset = self.data_offset + self.length
        
        # Extract primitive values directly
        payload = self.buffer[self.data_offset:self.data_offset + self.length]
        if self.datatype == "NUMERIC":
            self.value = int.from_bytes(payload, 'big', signed=True)
        elif self.datatype == "CHAR":
            self.value = payload.decode('utf-8')
        else:
            self.value = None  # STRUCTURED container has no direct primitive value
            
        self.rc = "SDX_RC_ok"
        return True

    def leave(self):
        """Leaves the current structured container."""
        if not self.stack:
            raise RuntimeError("Unmatched leave() call: Not inside a structure.")
        
        container_end = self.stack.pop()
        self.offset = container_end
        self.rc = "SDX_RC_ok"
