## Detector

### Quick Start

1. set the `SC_DIR` in Makefile

2. 
	```
	make chr_skeleton  # base filename without extension
	```


### Step

1. Extract texture atlas from `*_tex.sc` and decompress highlevel structure from `*.sc`.

	```bash
	./dumpsc.py chr_skeleton_tex.sc # out: chr_skeleton_tex.png
	./dumpsc.py chr_skeleton.sc # out: chr_skeleton.bin
	```

2. Extract shape pngs from `*_tex.png` using coordinate information in `*.bin` (the two files must be in the same dir)
	
	```bash
	./sc_decode.py chr_skeleton.bin # out: chr_skeleton_out/
	```

