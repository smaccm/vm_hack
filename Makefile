rw_mem: rw_mem.c
	g++ rw_mem.c -o rw_mem

.PHONY: read
read: rw_mem
	./rw_mem -a 0x80000000 -s 8192 -r

.PHONY: read-key
read-key: rw_mem
	./rw_mem -a 0x80001aa8 -s 16

.PHONY: read-nonce
read-nonce: rw_mem
	./rw_mem -a 0x80001b79 -s 8

.PHONY: read-salt
read-salt: rw_mem
	./rw_mem -a 0x80001b6c -s 8

.PHONY: hack
hack: rw_mem
	./rw_mem -a 0x80001b79 -s 8 -w -h 0x00
	./rw_mem -a 0x80001b6c -s 1 -w -h 0x09

.PHONY: zero-nonce
zero-nonce: rw_mem
	./rw_mem -a 0x80001b79 -s 8 -w -h 0x00

.PHONY: clean
clean:
	rm -f rw_mem
