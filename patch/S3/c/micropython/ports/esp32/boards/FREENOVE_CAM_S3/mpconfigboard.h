#undef MICROPY_HW_BOARD_NAME
#define MICROPY_HW_BOARD_NAME               "FREENOVE CAM S3"
#define MICROPY_HW_MCU_NAME                 "ESP32S3"

#define MICROPY_PY_MACHINE_DAC              (0)

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)

#define MICROPY_HW_I2C0_SCL                 (9)
#define MICROPY_HW_I2C0_SDA                 (8)
#define CONFIG_FREENOVE_CAM_S3 1
#define CONFIG_CAMERA 1
