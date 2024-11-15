## Detector

1. Extract texture atlas from `*_tex.sc` and decompress highlevel structure from `*.sc`.

	```bash
	./dumpsc.py chr_giant_tex.sc # out: chr_giant_tex.png
	./dumpsc.py chr_giant.sc # out: chr_giant.bin
	```

2. Extract shape pngs from the atlas using coordinate information in `*.bin`
	
	```bash
	./sc_decode.py chr_giant.bin # out: chr_giant_out/
	```

