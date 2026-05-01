/*
    Copyright 2024 Benjamin Vedder  benjamin@vedder.se
    Copyright 2024 BMSJ Contributors

    This file is part of the VESC BMS firmware.

    The VESC BMS firmware is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    The VESC BMS firmware is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef HWCONF_HW_BMSJ_H_
#define HWCONF_HW_BMSJ_H_

#define HW_NAME                 "BMSJ"

/*===========================================================================*/
/* Cell Configuration                                                        */
/*===========================================================================*/

#define HW_CELLS_SERIES         24          // 2x LTC6811 in daisy chain
#define HW_LTC_COUNT            2           // Number of LTC6811 ICs

/*===========================================================================*/
/* Current Sensing - INA226                                                  */
/*===========================================================================*/

// Using INA226 via I2C instead of analog shunt amplifier
#define HW_HAS_INA226
#define HW_INA226_I2C_ADDR      0x40

#define HW_SHUNT_RES            (0.1e-3)    // 0.1 mOhm (WSLP5931L1000FEA)
#define HW_INA226_CAL           51200       // Calibration for 1mA/LSB

// No analog current measurement
#undef HW_HAS_ANALOG_CURRENT

/*===========================================================================*/
/* LTC6811 via LTC6820 isoSPI                                               */
/*===========================================================================*/

// SPI1 for LTC6820
#define LINE_LTC_CS             PAL_LINE(GPIOA, 4)      // SPI1_NSS
#define LINE_LTC_SCLK           PAL_LINE(GPIOA, 5)      // SPI1_SCK
#define LINE_LTC_MISO           PAL_LINE(GPIOA, 6)      // SPI1_MISO
#define LINE_LTC_MOSI           PAL_LINE(GPIOA, 7)      // SPI1_MOSI

#define HW_SPI_DEV              SPID1
#define HW_SPI_AF               5

// LTC6811 (not LTC6813)
#define HW_LTC_TYPE             6811

/*===========================================================================*/
/* I2C for INA226                                                            */
/*===========================================================================*/

#define LINE_I2C_SDA            PAL_LINE(GPIOB, 7)      // I2C1_SDA
#define LINE_I2C_SCL            PAL_LINE(GPIOB, 6)      // I2C1_SCL

#define HW_I2C_DEV              I2CD1
#define HW_I2C_AF               4

/*===========================================================================*/
/* CAN Bus (via ISO1050 isolated transceiver)                                */
/*===========================================================================*/

#define LINE_CAN_RX             PAL_LINE(GPIOB, 8)      // CAN1_RX
#define LINE_CAN_TX             PAL_LINE(GPIOB, 9)      // CAN1_TX

#define HW_CAN_DEV              CAND1
#define HW_CAN_AF               9

/*===========================================================================*/
/* USB (via CP2104 USB-UART bridge)                                          */
/*===========================================================================*/

// CP2104 connects to USART - not native USB
#define LINE_USB_TX             PAL_LINE(GPIOA, 9)      // USART1_TX
#define LINE_USB_RX             PAL_LINE(GPIOA, 10)     // USART1_RX

#define HW_UART_DEV             UARTD1
#define HW_UART_AF              7
#define HW_UART_BAUDRATE        115200

/*===========================================================================*/
/* OLED Display (optional, I2C)                                              */
/*===========================================================================*/

#define HW_HAS_OLED
#define LINE_OLED_SDA           PAL_LINE(GPIOB, 11)     // I2C2_SDA
#define LINE_OLED_SCL           PAL_LINE(GPIOB, 10)     // I2C2_SCL
#define LINE_OLED_RST           PAL_LINE(GPIOC, 13)     // OLED reset

/*===========================================================================*/
/* Charge/Discharge Control                                                  */
/*===========================================================================*/

// High-side switch controls (active high via IRFL4105PBF)
#define LINE_CHG_EN             PAL_LINE(GPIOC, 6)      // Charge enable
#define LINE_DSG_EN             PAL_LINE(GPIOC, 7)      // Discharge enable
#define LINE_PCHG_EN            PAL_LINE(GPIOC, 8)      // Precharge enable

#define CHARGE_ENABLE()         palSetLine(LINE_CHG_EN); palSetLine(LINE_DSG_EN)
#define CHARGE_DISABLE()        palClearLine(LINE_CHG_EN); palClearLine(LINE_DSG_EN)
#define PRECHARGE_ENABLE()      palSetLine(LINE_PCHG_EN)
#define PRECHARGE_DISABLE()     palClearLine(LINE_PCHG_EN)

/*===========================================================================*/
/* Status LEDs                                                               */
/*===========================================================================*/

#define LINE_LED_RED            PAL_LINE(GPIOA, 0)      // Status LED (red)
#define LINE_LED_GREEN          PAL_LINE(GPIOA, 1)      // Power LED (green)

#define LED_RED_ON()            palSetLine(LINE_LED_RED)
#define LED_RED_OFF()           palClearLine(LINE_LED_RED)
#define LED_GREEN_ON()          palSetLine(LINE_LED_GREEN)
#define LED_GREEN_OFF()         palClearLine(LINE_LED_GREEN)

/*===========================================================================*/
/* Buzzer                                                                    */
/*===========================================================================*/

#define HW_HAS_BUZZER
#define LINE_BUZZER             PAL_LINE(GPIOA, 8)      // Buzzer output

/*===========================================================================*/
/* Inputs                                                                    */
/*===========================================================================*/

#define LINE_PWR_BTN            PAL_LINE(GPIOC, 9)      // Power button
#define LINE_CHG_DETECT         PAL_LINE(GPIOC, 10)     // Charger detect
#define LINE_SAFETY             PAL_LINE(GPIOC, 11)     // Safety interlock

/*===========================================================================*/
/* Temperature Sensing (NTC via LTC6811 GPIO)                                */
/*===========================================================================*/

// Thermistors connected to LTC6811 GPIO pins
#define HW_TEMP_SENSORS         3
#define LTC_GPIO_TEMP_0         1   // GPIO1 - Thermistor 1
#define LTC_GPIO_TEMP_1         2   // GPIO2 - Thermistor 2
#define LTC_GPIO_TEMP_2         3   // GPIO3 - Thermistor 3

// NTC parameters (100k @ 25°C, B=4250)
#define NTC_RES_25C             100000.0
#define NTC_BETA                4250.0
#define NTC_PULLUP              10000.0

#define NTC_RES(adc)            (NTC_PULLUP * (float)adc / (30000.0 - (float)adc))
#define NTC_TEMP(adc)           (1.0 / ((logf(NTC_RES(adc) / NTC_RES_25C) / NTC_BETA) + (1.0 / 298.15)) - 273.15)

/*===========================================================================*/
/* Pack Voltage Sensing                                                      */
/*===========================================================================*/

// Voltage divider for pack voltage (sum of cells from LTC6811)
// Using LTC6811 internal sum-of-cells register
#define HW_USE_LTC_SOC          1   // Use LTC6811 sum-of-cells

/*===========================================================================*/
/* Initialization                                                            */
/*===========================================================================*/

#define HW_INIT_HOOK()          hw_bmsj_init()

void hw_bmsj_init(void);

#endif /* HWCONF_HW_BMSJ_H_ */
