/*
    Copyright 2024 Benjamin Vedder  benjamin@vedder.se
    Copyright 2024 BMSZ Contributors

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

#include "hw_bmsz.h"
#include "hal.h"
#include "ina226.h"

/*===========================================================================*/
/* Hardware Initialization                                                   */
/*===========================================================================*/

void hw_bmsz_init(void) {
    /*
     * GPIO Configuration
     */

    // LEDs (output, push-pull)
    palSetLineMode(LINE_LED_RED, PAL_MODE_OUTPUT_PUSHPULL);
    palSetLineMode(LINE_LED_GREEN, PAL_MODE_OUTPUT_PUSHPULL);
    LED_RED_OFF();
    LED_GREEN_OFF();

    // Buzzer (output, push-pull)
    palSetLineMode(LINE_BUZZER, PAL_MODE_OUTPUT_PUSHPULL);
    palClearLine(LINE_BUZZER);

    // Charge/Discharge control (output, push-pull, start disabled)
    palSetLineMode(LINE_CHG_EN, PAL_MODE_OUTPUT_PUSHPULL);
    palSetLineMode(LINE_DSG_EN, PAL_MODE_OUTPUT_PUSHPULL);
    palSetLineMode(LINE_PCHG_EN, PAL_MODE_OUTPUT_PUSHPULL);
    palClearLine(LINE_CHG_EN);
    palClearLine(LINE_DSG_EN);
    palClearLine(LINE_PCHG_EN);

    // Inputs (input with pull-up)
    palSetLineMode(LINE_PWR_BTN, PAL_MODE_INPUT_PULLUP);
    palSetLineMode(LINE_CHG_DETECT, PAL_MODE_INPUT_PULLUP);
    palSetLineMode(LINE_SAFETY, PAL_MODE_INPUT_PULLUP);

    // OLED reset (output, active low, start in reset)
    palSetLineMode(LINE_OLED_RST, PAL_MODE_OUTPUT_PUSHPULL);
    palClearLine(LINE_OLED_RST);

    /*
     * SPI1 for LTC6820 isoSPI
     */
    palSetLineMode(LINE_LTC_CS, PAL_MODE_OUTPUT_PUSHPULL);
    palSetLine(LINE_LTC_CS);  // CS high (inactive)

    palSetLineMode(LINE_LTC_SCLK, PAL_MODE_ALTERNATE(HW_SPI_AF));
    palSetLineMode(LINE_LTC_MISO, PAL_MODE_ALTERNATE(HW_SPI_AF));
    palSetLineMode(LINE_LTC_MOSI, PAL_MODE_ALTERNATE(HW_SPI_AF));

    /*
     * I2C1 for INA226
     */
    palSetLineMode(LINE_I2C_SDA, PAL_MODE_ALTERNATE(HW_I2C_AF) | PAL_STM32_OTYPE_OPENDRAIN);
    palSetLineMode(LINE_I2C_SCL, PAL_MODE_ALTERNATE(HW_I2C_AF) | PAL_STM32_OTYPE_OPENDRAIN);

    /*
     * CAN1
     */
    palSetLineMode(LINE_CAN_RX, PAL_MODE_ALTERNATE(HW_CAN_AF));
    palSetLineMode(LINE_CAN_TX, PAL_MODE_ALTERNATE(HW_CAN_AF));

    /*
     * USART1 for USB (via CP2104)
     */
    palSetLineMode(LINE_USB_TX, PAL_MODE_ALTERNATE(HW_UART_AF));
    palSetLineMode(LINE_USB_RX, PAL_MODE_ALTERNATE(HW_UART_AF));

    /*
     * I2C2 for OLED (optional)
     */
    palSetLineMode(LINE_OLED_SDA, PAL_MODE_ALTERNATE(HW_I2C_AF) | PAL_STM32_OTYPE_OPENDRAIN);
    palSetLineMode(LINE_OLED_SCL, PAL_MODE_ALTERNATE(HW_I2C_AF) | PAL_STM32_OTYPE_OPENDRAIN);

    // Release OLED from reset after a short delay
    chThdSleepMilliseconds(10);
    palSetLine(LINE_OLED_RST);

    /*
     * Initialize INA226 current sensor
     */
    ina226_init(HW_INA226_I2C_ADDR, HW_INA226_CAL);

    // Signal successful init
    LED_GREEN_ON();
}

/*===========================================================================*/
/* INA226 Current Reading                                                    */
/*===========================================================================*/

#ifdef HW_HAS_INA226

float hw_read_current(void) {
    int16_t raw = ina226_read_current_raw();
    // With calibration set for 1mA/LSB
    return (float)raw * 0.001f;  // Return in Amps
}

float hw_read_shunt_voltage(void) {
    int16_t raw = ina226_read_shunt_raw();
    // INA226 LSB = 2.5µV
    return (float)raw * 2.5e-6f;  // Return in Volts
}

#endif

/*===========================================================================*/
/* Temperature Reading                                                       */
/*===========================================================================*/

float hw_temp_cell_max(void) {
    // Returns maximum temperature from LTC6811 GPIO readings
    // This will be called by the VESC BMS main loop
    // Temperature conversion is done in ltc.c using NTC_TEMP macro
    extern float ltc_get_temp(int sensor);

    float max_temp = -273.15f;
    for (int i = 0; i < HW_TEMP_SENSORS; i++) {
        float temp = ltc_get_temp(i);
        if (temp > max_temp) {
            max_temp = temp;
        }
    }
    return max_temp;
}
