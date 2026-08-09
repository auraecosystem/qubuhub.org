from sdxf import SDXF

# Initialize structure for your project data workflow
sdx = SDXF(buffersize=1000)
sdx.create(10, "STRUCTURED")           # Root Container
sdx.create(11, "NUMERIC", 123456)     # Data ID
sdx.create(12, "CHAR", "2026-03-30")  # Timestamp/Date
sdx.leave()

# Save the binary package directly to your project's data directory
sdx.save("data/output.sdxf")
