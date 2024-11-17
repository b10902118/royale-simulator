## Detector

### Quick Start

1. set the `SC_DIR` in Makefile

2. Arg is base filename without extension, ex:

	```
	make chr_skeleton  
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

### Note
New sc can only be downloaded from server [SC-Assets-Downloader-GUI](https://github.com/Galaxy1036/SC-Assets-Downloader-GUI). The new sc file is compressed by ZSTD, which cr-sc-dump can recognize but still needs to dump the decompressed data to sc_decode. For some character like skeleton, the decompressed swf has extra header and cannot be decoded currently, not sure whether it is for China version.

### Reference
https://github.com/123456abcdef/cr-sc-dump

https://github.com/Galaxy1036/sc_decode/

https://github.com/sc-workshop/SupercellFlash

https://github.com/Galaxy1036/SC-Assets-Downloader-GUI
