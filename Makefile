# Default source directory
SC_DIR := ../2.0/assets/sc

# Get basename from the first argument
BASE := $(wordlist 1,1,$(MAKECMDGOALS))

# Verify BASE is provided
ifeq ($(BASE),)
$(error Usage: make basename (example: make chr_giant))
endif

# Construct full paths
SC_FILE := $(SC_DIR)/$(BASE).sc
TEX_FILE := $(SC_DIR)/$(BASE)_tex.sc
TEXTURE_PNG := $(BASE)_tex.png
BIN_FILE := $(BASE).bin
OUTPUT_DIR := $(BASE)_out

.PHONY: all clean $(BASE)

# The target matches the basename
$(BASE): $(OUTPUT_DIR)

# Extract texture atlas
$(TEXTURE_PNG): $(TEX_FILE)
	./dumpsc.py $(TEX_FILE)

# Decompress structure
$(BIN_FILE): $(SC_FILE)
	./dumpsc.py $(SC_FILE)

# Extract shape PNGs
$(OUTPUT_DIR): $(BIN_FILE) $(TEXTURE_PNG)
	./sc_decode.py $(BIN_FILE)

clean:
	rm -f $(TEXTURE_PNG)
	rm -f $(BIN_FILE)
	rm -rf $(OUTPUT_DIR)

# Catch any non-target arguments
%:
	@:

# Usage examples:
# make chr_giant            # Uses current directory
# make chr_giant SC_DIR=data  # Uses data directory
