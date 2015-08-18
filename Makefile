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

.PHONY: unhack
unhack:
# Reset salts
	./rw_mem -a 0x80000b6c -s 1 -w -h 0x08
	./rw_mem -a 0x80000b6d -s 1 -w -h 0x07
	./rw_mem -a 0x80000b6e -s 1 -w -h 0x06
	./rw_mem -a 0x80000b6f -s 1 -w -h 0x05
	./rw_mem -a 0x80000b70 -s 1 -w -h 0x04
	./rw_mem -a 0x80000b71 -s 1 -w -h 0x03
	./rw_mem -a 0x80000b72 -s 1 -w -h 0x02
	./rw_mem -a 0x80000b73 -s 1 -w -h 0x01

	./rw_mem -a 0x80001b6c -s 8 -w -h 0x11
	./rw_mem -a 0x80001b6d -s 8 -w -h 0x12
	./rw_mem -a 0x80001b6e -s 8 -w -h 0x13
	./rw_mem -a 0x80001b6f -s 8 -w -h 0x14
	./rw_mem -a 0x80001b70 -s 8 -w -h 0x15
	./rw_mem -a 0x80001b71 -s 8 -w -h 0x16
	./rw_mem -a 0x80001b72 -s 8 -w -h 0x17
	./rw_mem -a 0x80001b73 -s 8 -w -h 0x18

# Reset nonces
	./rw_mem -a 0x80000b79 -s 8 -w -h 0x00
	./rw_mem -a 0x80001b78 -s 8 -w -h 0x00

.PHONY: clean
clean:
	rm -f rw_mem
