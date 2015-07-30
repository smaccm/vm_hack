These notes describe how the attack is constructed

The goal is to overwrite the nonce and salt for the encryption and
decryption functions. The relevant data is in
  - `commsecDecodeState_inst_group_bin`
  - `commsecEncodeState_inst_group_bin`

Once Odroid image is compiled, these binaries can be found in
  - `build/arm/exynos5/smaccmpilot`


