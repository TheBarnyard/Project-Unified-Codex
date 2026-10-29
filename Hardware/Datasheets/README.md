---
updated: 2026-10-29
updated_by: Barney (Claude, session [2026-10-29 hardware datasheets](../../sessions/2026/10/2026-10-29_1513_Barney_hardware-datasheets.md))
---
# Hardware datasheets

Datasheets, pinouts and manuals for every part on the rig, one folder per part. Files were uploaded by Barney on 2026-10-29 and renamed so the name says what the file is.

| Part (role on the rig) | File | What it is |
| --- | --- | --- |
| MT6701 magnetic encoder (arm joint angle) | [MT6701_Encoder_Datasheet.pdf](MT6701_Encoder/MT6701_Encoder_Datasheet.pdf) | MagnTek MT6701 14-bit Hall angle sensor datasheet (I2C, SSI, ABZ), 37 pages |
| Seeed XIAO ESP32-C3 (TX1, TX2 transmitters) | [XIAO_ESP32C3_Pinout.pdf](XIAO_ESP32C3_Transmitter/XIAO_ESP32C3_Pinout.pdf) | Board pinout diagram, 1 page |
| | [ESP32C3_Chip_Datasheet_v1.2.pdf](XIAO_ESP32C3_Transmitter/ESP32C3_Chip_Datasheet_v1.2.pdf) | Espressif ESP32-C3 series chip datasheet, v1.2 |
| ESP32-WROOM-32 (receiver master) | [ESP32_WROOM32_Module_Datasheet_v3.8.pdf](ESP32_WROOM32_Receiver/ESP32_WROOM32_Module_Datasheet_v3.8.pdf) | Espressif module datasheet, v3.8 (newest; use this one) |
| | [ESP32_WROOM32_Module_Datasheet_v2.4_old.pdf](ESP32_WROOM32_Receiver/ESP32_WROOM32_Module_Datasheet_v2.4_old.pdf) | Same module, older v2.4. Duplicate kept as uploaded |
| | [ESP32_Technical_Reference_Manual_v5.9.txt](ESP32_WROOM32_Receiver/ESP32_Technical_Reference_Manual_v5.9.txt) | ESP32 chip technical reference manual v5.9, text conversion of the PDF (tables and figures may be lost) |
| Arduino Mega 2560 Rev3 (cart stepper driver) | [Arduino_Mega2560_Rev3_Board_Datasheet.pdf](Arduino_Mega2560_Cart/Arduino_Mega2560_Rev3_Board_Datasheet.pdf) | Arduino board datasheet / user manual, SKU A000067 |
| | [ATmega2560_Chip_Datasheet.txt](Arduino_Mega2560_Cart/ATmega2560_Chip_Datasheet.txt) | Microchip (Atmel) ATmega640/1280/2560 MCU datasheet, text conversion of the PDF |
| Raspberry Pi 4 Model B 8 GB (controller) | [RaspberryPi4B_Datasheet.pdf](RaspberryPi4B_Controller/RaspberryPi4B_Datasheet.pdf) | Raspberry Pi datasheet RP-008341-DS, release 1.1 |
| | [RaspberryPi4B_Product_Brief.pdf](RaspberryPi4B_Controller/RaspberryPi4B_Product_Brief.pdf) | Product brief RP-008344-DS (21 MB) |
| UIM5756PM closed-loop stepper motor, UIM344 controller built in (cart motor) | [UIM5756PM_Motor_Dimensions.pdf](UIM5756PM_Motor/UIM5756PM_Motor_Dimensions.pdf) | Mechanical dimension drawing |
| | [UIM344_Controller_Manual_v5.11.pdf](UIM5756PM_Motor/UIM344_Controller_Manual_v5.11.pdf) | UIM344 pulse-direction controller user manual v5.11 |
| | [UIM344_Wiring_Diagram_UIM5756PM.pdf](UIM5756PM_Motor/UIM344_Wiring_Diagram_UIM5756PM.pdf) | One-page UIM344 wiring diagram for the UIM5756PM (1.8 deg step, 32 microsteps default). From project files `Manual_UIM5756PM.pdf` |
| | [UIM344_Config_Tool_Windows.zip](UIM5756PM_Motor/UIM344_Config_Tool_Windows.zip) | Vendor Windows config tool (`CfgTool_UIM344/CFG344.exe` + Qt DLLs), kept as uploaded. Not checked or run |

## Notes
- Duplicates: two ESP32-WROOM-32 datasheets (v3.8 and v2.4). Barney's Claude project files also hold copies of several of these (`A000067-datasheet.pdf` is a slightly different file from the one here, `MT6701.PDF`, `esp32-c3_datasheet.pdf`, the Pi datasheet, the XIAO pinout).
- The `.txt` files are text conversions; open the original PDF from Espressif or Microchip for figures and register tables.
