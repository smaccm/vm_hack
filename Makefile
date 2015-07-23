rw_mem: rw_mem.c
	g++ rw_mem.c -o rw_mem

.PHONY: read
read: rw_mem
	./rw_mem -a 0x1408000 -s 8192 -r

.PHONY: zero
zero: rw_mem
	./rw_mem -w -a 0x1408000 -s 24 -h 00

.PHONY: clean
clean:
	rm -f rw_mem
