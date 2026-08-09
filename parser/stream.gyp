# Assuming 'binary_output' is the byte buffer generated from the builder
parser = SDXFParser(binary_output)

# Map IDs back to readable names for display
ID_NAMES = {
    100: "INVOICE",
    101: "INVOICE_NO",
    102: "DATE",
    103: "ADDRESS_SENDER",
    104: "NAME",
    105: "COUNTRY"
}

# Read root structure
parser.next() 
print(f"[{ID_NAMES.get(parser.chunk_id, parser.chunk_id)}] ({parser.datatype})")

# Step into INVOICE container
parser.enter()

while parser.rc == "SDX_RC_ok":
    name = ID_NAMES.get(parser.chunk_id, parser.chunk_id)
    
    if parser.datatype == "STRUCTURED":
        print(f"  └── {name} (START STRUCTURE)")
        parser.enter() # Dive into nested structure (e.g., ADDRESS_SENDER)
        continue
        
    print(f"      ├── {name}: {parser.value}")
    
    # Try moving to the next element; if scope ends, leave the structure
    if not parser.next():
        parser.leave()
        print(f"  └── (END STRUCTURE)")
        parser.next() # Resume outer scope
