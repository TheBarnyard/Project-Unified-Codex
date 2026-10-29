# Gotchas

Traps that cost someone time. Add one whenever you lose more than 15 minutes to something.

- **Serial junk at startup:** opening the receiver port after it has been closed for 5+ s gives one repeated 32-byte chunk of junk (about 60% of opens). The stream is clean after that. Likely a CP2102 / USB host artifact. (2026-10-07)
- **Pi Connect mangles long pastes:** give Pi steps as small heredoc blocks per file with a `sha256sum -c` check at the end.
- **Pi Python:** use `~/PythonLibraries/bin/python`. arduino-cli is `~/bin/arduino-cli`.
- **Pi auto-sync:** pause updates (desktop shortcut) before editing files inside a synced checkout.
- **ENGT480 logs branch is huge:** never fetch all branches. Use `git clone --depth 1 --filter=blob:none --no-checkout --single-branch --branch logs` and `git show HEAD:<path>`. CSVs over 20 MiB are `.csv.gz` or `.csv.gz.parts` (restore with `Code/Global/restore_csv_log.py`).
- **XIAO ESP32-C3 native USB:** `Serial.availableForWrite()` stays 0 forever if the monitor opens after boot, so gated writers print nothing. Write directly. The reset button drops USB and crashes miniterm.
- **Flash the right board:** check the MAC before flashing a XIAO. TX1 was flashed by mistake on 2026-10-27.
- **Powering a XIAO from 5 V:** 5 V goes to the XIAO 5V pin, never 3V3. Encoder and I2C pull-ups stay on the XIAO 3V3.
- **Mega 3.3 V pin is too weak** for an ESP32-C3 (TX bursts). Caused the 2026-10-27 dropouts.
- **A XIAO transmitter needs peak current, not just average:** a meter shows ~120-150 mA, but TX bursts reach ~335 mA. A bench supply limited to 150 mA reproduced the dropouts (2026-10-29). Give each XIAO a supply rated 500 mA+ and a bulk capacitor at the board.
- **TX2 on a USB cable** showed angle gaps up to 3.7 s; on battery it is clean.
- **Arm cable plugged in** changes the arm dynamics. Run `excite_20261027_154016` is bad for that reason; do not use it for fitting.
- **Stepper speed rounding:** at about 0.83 m/s one timer step is bigger than the allowed acceleration step, so the cart cannot speed up further. Keep planned speeds well below that.
