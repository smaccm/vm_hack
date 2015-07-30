rw_mem: rw_mem.c
	g++ rw_mem.c -o rw_mem

.PHONY: read
read: rw_mem
	./rw_mem -a 0x80000000 -s 8192 -r

.PHONY: read-keys
read-keys: rw_mem
	./rw_mem -a 0x80000aa8 -s 16
	./rw_mem -a 0x80001aa8 -s 16

.PHONY: read-nonces
read-nonces: rw_mem
	./rw_mem -a 0x80000b79 -s 8
	./rw_mem -a 0x80001b78 -s 8

.PHONY: read-salts
read-salts: rw_mem
	./rw_mem -a 0x80000b6c -s 8
	./rw_mem -a 0x80001b6c -s 8

.PHONY: hack
hack: rw_mem
# Clear salts
	./rw_mem -a 0x80000b6c -s 8 -w -h 0x00
	./rw_mem -a 0x80001b6c -s 8 -w -h 0x00
# Reset nonces
	./rw_mem -a 0x80000b79 -s 8 -w -h 0x00
	./rw_mem -a 0x80001b78 -s 8 -w -h 0x00

.PHONY: clean
clean:
	rm -f rw_mem
