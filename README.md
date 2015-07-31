Demo
====

In this demo the Odroid is loaded with deliberately misconfigured
software. This allows the VM to break off communication with the
legitimate ground control station (GCS) and turn over control to a
rogue GCS. This demonstrates how a very small flaw can lead to
complete loss of the system.

Setup
=====

1. Set up a legitimate GCS using the default software.

2. Configure a rogue GCS: set up a normal GCS, but modify
`smaccmpilot-stm32f4/src/smaccm-flight/keys.conf` to the following:

```
[symmetric_key.server_to_client]
keysalt = [ 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 0, 0, 0, 0, 0, 0, 0, 0 ]

[symmetric_key.client_to_server]
keysalt = [ 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 0, 0, 0, 0, 0, 0, 0, 0 ]
```

3. Fastboot the Odroid using the image `vm-hack-odroid-image`.

4. Have this repository checked out in the Odroid VM.

Running the demo
================

1. Run the Odroid and the legitimate GCS as normal. Demonstrate that
the legitimate GCS has control of the Odroid.

2. In the VM, go into the repository for this demo and execute
`./attack.sh`. If that doesn't work (due to caching issues) you can
just run `make clean hack` to do a quick version of the attack.

3. Demonstrate that the legitimate GCS has lost control of the Odroid.

4. Connect the rogue GCS (probably via reconnecting the USB-to-serial
cable).

5. Demonstrate that the rogue GCS has control of the Odroid.

