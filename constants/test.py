# Constants for IDs
INVOICE = 10
INVOICE_NO = 11
DATE = 12
ADDRESS_SENDER = 13
NAME = 14
COUNTRY = 15

# Initialize engine
sdx = SDXF(buffersize=1000)

# Build structure
sdx.create(INVOICE, "STRUCTURED")
sdx.create(INVOICE_NO, "NUMERIC", 123456)
sdx.create(DATE, "CHAR", "2005-06-17")

sdx.create(ADDRESS_SENDER, "STRUCTURED")
sdx.create(NAME, "CHAR", "Peter Somebody")
sdx.create(COUNTRY, "CHAR", "France")
sdx.leave()  # Leave ADDRESS_SENDER

sdx.leave()  # Leave INVOICE

# Save to file
sdx.save("invoice.sdxf")
