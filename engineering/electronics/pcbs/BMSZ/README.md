# BMSZ

Open-source Battery Management System designed for high-voltage lithium battery packs with VESC integration.


## Longshot Repository Layout

This project was imported from `Julius-eng/Vector-BMS` and adapted into the Project Longshot engineering tree.

- `kicad/` — KiCad project, schematic sheets, PCB, and project-local library tables.
- `kicad/libs/BMSZ.pretty/` — project-local footprints imported from the source repository.
- `firmware/vesc_bms_hw/` — VESC BMS hardware configuration renamed to `hw_bmsz`.
- `docs/`, `images/`, and `manufacturing/` — placeholders for supporting design notes, renders, and fab outputs.

## Overview

BMSZ is a modular BMS supporting up to **24 series cells** (24S) with:
- Active cell monitoring and balancing
- High-current sensing (up to 120A)
- CAN bus communication (VESC-compatible)
- USB interface for configuration
- Isolated design for safety

**Firmware:** This project uses [VESC BMS firmware](https://github.com/vedderb/vesc_bms_fw) for full VESC Tool integration.

## Hardware Architecture

### Schematic Structure

```
BMSZ.kicad_sch (Main)
├── Power management
├── Cell monitoring (LTC6811 × 2)
├── Current sensing (INA226)
├── High-side switching
└── Connectors

MCU.kicad_sch
├── STM32L476 microcontroller
├── CAN interface (isolated via ISO1050)
├── isoSPI interface (LTC6820)
└── USB interface (CP2104)

cell.kicad_sch / cell2.kicad_sch
└── Per-cell balancing circuits (×12 each)
```

### Key Components

| Component | Part Number | Function |
|-----------|-------------|----------|
| MCU | STM32L476RGT6 | ARM Cortex-M4, 80MHz, low power |
| Cell Monitor | LTC6811-1 (×2) | 12-cell stack monitor, ±1.2mV accuracy |
| isoSPI | LTC6820 | Isolated SPI for LTC6811 daisy chain |
| Current Sensor | INA226 | 16-bit I2C power monitor |
| Shunt Resistor | WSLP5931L1000FEA | 0.1mΩ, 15W, ±1% |
| CAN Transceiver | ISO1050DUBR | Isolated CAN 2.0B |
| USB-UART | CP2104 | USB to UART bridge |
| DC-DC | LM5165 | Wide-input buck converter |
| Balance FET | DMG2305UX-7 | P-ch MOSFET, SOT-23 |
| Balance Resistor | CRCW25123R90JNEA | 3.9Ω, 1W, 2512 |
| High-side Switch | IRFL4105PBF | N-ch logic-level MOSFET |

### Cell Configuration

- **Maximum cells:** 24S (two LTC6811 in daisy chain)
- **Cell voltage range:** 0V to 5V per cell (compatible with most Li-ion/LiFePO4)
- **Balance current:** ~1A per cell @ 4.2V (passive balancing via 3.9Ω resistor)
- **Temperature monitoring:** 3× NTC thermistors

### Current Sensing

- **Shunt:** 0.1mΩ (WSLP5931, 15×7.6mm)
- **Max continuous:** 120A
- **Sensor:** INA226 (16-bit I2C power monitor)
- **Resolution:** ~1mA per LSB
- **Power dissipation:** 1.44W at 120A

## VESC BMS Firmware

BMSZ uses the [VESC BMS firmware](https://github.com/vedderb/vesc_bms_fw) which provides:

- ✅ Cell monitoring and balancing
- ✅ Charge control with CC/CV support
- ✅ Low-power sleep mode
- ✅ CAN-bus integration with VESC motor controllers
- ✅ USB configuration via VESC Tool
- ✅ Ah and Wh counting
- ✅ Distributed balancing across multiple BMSes
- ✅ Bootloader and firmware update support

### Building Firmware

#### Prerequisites

1. **ARM GCC Toolchain**
   ```bash
   # Ubuntu/Debian
   sudo apt install gcc-arm-none-eabi

   # macOS
   brew install arm-none-eabi-gcc

   # Windows: Download from ARM website
   ```

2. **ChibiOS** (included as submodule in VESC BMS)

3. **Make**

#### Clone and Build

```bash
# Clone VESC BMS firmware
git clone --recursive https://github.com/vedderb/vesc_bms_fw.git
cd vesc_bms_fw

# Copy BMSZ hardware config
cp /path/to/project-longshot/engineering/electronics/pcbs/BMSZ/firmware/vesc_bms_hw/hw_bmsz.h hwconf/
cp /path/to/project-longshot/engineering/electronics/pcbs/BMSZ/firmware/vesc_bms_hw/hw_bmsz.c hwconf/

# Build for BMSZ
make HWCONF=hw_bmsz

# Output: build/vesc_bms_fw.bin
```

#### Flashing

Using ST-Link:
```bash
# Flash via OpenOCD
openocd -f interface/stlink.cfg -f target/stm32l4x.cfg \
    -c "program build/vesc_bms_fw.bin 0x08000000 verify reset exit"

# Or via st-flash
st-flash write build/vesc_bms_fw.bin 0x08000000
```

Using VESC Tool (for updates):
1. Connect BMSZ via USB
2. Open VESC Tool
3. Go to **Firmware** → **Bootloader**
4. Select `vesc_bms_fw.bin` and upload

### Hardware Configuration

The BMSZ hardware config is in `firmware/vesc_bms_hw/`:

```
firmware/vesc_bms_hw/
├── hw_bmsz.h     # Pin definitions, parameters
└── hw_bmsz.c     # Initialization, INA226 driver
```

Key parameters in `hw_bmsz.h`:

```c
#define HW_CELLS_SERIES         24          // Cell count
#define HW_SHUNT_RES            (0.1e-3)    // Shunt resistance
#define HW_INA226_I2C_ADDR      0x40        // INA226 address
```

### VESC Tool Configuration

1. Connect BMSZ via USB
2. Open VESC Tool and connect
3. Go to **VESC BMS** tab
4. Configure:
   - Cell count: 24
   - Balance start voltage
   - Balance delta voltage
   - Current limits
   - Temperature limits
5. **Write Configuration**

## MCU Pin Mapping

| Function | STM32 Pin | Notes |
|----------|-----------|-------|
| SPI1_NSS (LTC6820) | PA4 | Directly driven CS |
| SPI1_SCK | PA5 | isoSPI clock |
| SPI1_MISO | PA6 | isoSPI data in |
| SPI1_MOSI | PA7 | isoSPI data out |
| I2C1_SDA (INA226) | PB7 | Current sensor |
| I2C1_SCL | PB6 | Current sensor |
| CAN1_RX | PB8 | Via ISO1050 |
| CAN1_TX | PB9 | Via ISO1050 |
| USART1_TX | PA9 | Via CP2104 to USB |
| USART1_RX | PA10 | Via CP2104 to USB |
| CHG_EN | PC6 | Charge enable |
| DSG_EN | PC7 | Discharge enable |
| PCHG_EN | PC8 | Precharge enable |
| LED_RED | PA0 | Status LED |
| LED_GREEN | PA1 | Power LED |
| BUZZER | PA8 | Audible alarm |

## Connectors

| Connector | Function |
|-----------|----------|
| J1 | Main battery input |
| J2 | Charger input |
| J3 | OLED display (I2C) |
| J12 | CAN bus |
| J14 | Serial/debug |
| J17 | Power button |
| J24 | USB (CP2104) |

## Hardware Design

### Prerequisites

- KiCad 9.0+ for schematic/PCB editing

### Opening the Project

1. Clone the repository
2. Open `kicad/BMSZ.kicad_pro` in KiCad
3. Review schematic and PCB layout
4. Generate BOM and fabrication files

## License

Hardware: Open Source (license TBD)
Firmware: [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html) (VESC BMS)

## Contributing

Contributions welcome! Please open an issue or pull request.

## Acknowledgments

- [Benjamin Vedder](https://github.com/vedderb) for VESC BMS firmware
- VESC Project for the open-source motor controller ecosystem
- Analog Devices for LTC6811 reference designs
- Arrow DAO community
