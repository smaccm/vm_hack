rw_mem: rw_mem.c
	g++ rw_mem.c -o rw_mem

.PHONY: read
read: rw_mem
	./rw_mem -a 0xd0000000 -s 8192 -r

.PHONY: read-keys
read-keys: rw_mem
	./rw_mem -a 0xd00004c8 -s 16
	./rw_mem -a 0xd0001598 -s 16

.PHONY: read-nonces
read-nonces: rw_mem
	./rw_mem -a 0xd0000599 -s 8
	./rw_mem -a 0xd0001668 -s 8

.PHONY: read-salts
read-salts: rw_mem
	./rw_mem -a 0xd000058c -s 8
	./rw_mem -a 0xd000165c -s 8

.PHONY: hack
hack: rw_mem
# Clear salts
	./rw_mem -a 0xd000058c -s 8 -w -h 0x00
	./rw_mem -a 0xd000165c -s 8 -w -h 0x00
# Reset nonces
	./rw_mem -a 0xd0000599 -s 8 -w -h 0x00
	./rw_mem -a 0xd0001668 -s 8 -w -h 0x00

.PHONY: unhack
unhack:
# Reset salts
	./rw_mem -a 0xd000058c -s 1 -w -h 0x08
	./rw_mem -a 0xd000058d -s 1 -w -h 0x07
	./rw_mem -a 0xd000058e -s 1 -w -h 0x06
	./rw_mem -a 0xd000058f -s 1 -w -h 0x05
	./rw_mem -a 0xd0000590 -s 1 -w -h 0x04
	./rw_mem -a 0xd0000591 -s 1 -w -h 0x03
	./rw_mem -a 0xd0000592 -s 1 -w -h 0x02
	./rw_mem -a 0xd0000593 -s 1 -w -h 0x01

	./rw_mem -a 0xd000165c -s 8 -w -h 0x11
	./rw_mem -a 0xd000165d -s 8 -w -h 0x12
	./rw_mem -a 0xd000165e -s 8 -w -h 0x13
	./rw_mem -a 0xd000165f -s 8 -w -h 0x14
	./rw_mem -a 0xd0001660 -s 8 -w -h 0x15
	./rw_mem -a 0xd0001661 -s 8 -w -h 0x16
	./rw_mem -a 0xd0001662 -s 8 -w -h 0x17
	./rw_mem -a 0xd0001663 -s 8 -w -h 0x18

# Reset nonces
	./rw_mem -a 0xd0000599 -s 8 -w -h 0x00
	./rw_mem -a 0xd0001668 -s 8 -w -h 0x00

.PHONY: clean
clean:
	rm -f rw_mem
