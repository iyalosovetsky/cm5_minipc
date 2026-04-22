import smbus2

# Адреса INA3221 (за замовчуванням 0x40)
I2C_ADDR = 0x40
bus = smbus2.SMBus(1) # 1 вказує на /dev/i2c-1

def write_ina_reg(reg, value):
    # INA3221 очікує 16-бітні значення (Big Endian)
    high_byte = (value >> 8) & 0xFF
    low_byte = value & 0xFF
    bus.write_i2c_block_data(I2C_ADDR, reg, [high_byte, low_byte])

# 1. Налаштування Configuration Register (00h)
# Увімкнено тільки CH1 (біти 15-12: 1000), Averaging 16 (біти 11-9: 010)
# Bus/Shunt conversion time 1.1ms (біти 8-3: 100100), Continuous mode (111)
# Binary: 1000 0101 0010 0111 -> Hex: 0x8527
config_val = 0x8527
write_ina_reg(0x00, config_val)

# 2. Встановлення Power-Valid Upper Limit (10h)
# 3.5V / 0.008 = 437.5 (0x1B6). Зсув вліво на 4 біти -> 0x1B60
write_ina_reg(0x10, 0x1B60)

# 3. Встановлення Power-Valid Lower Limit (11h)
# 3.2V / 0.008 = 400 (0x190). Зсув вліво на 4 біти -> 0x1900
write_ina_reg(0x11, 0x1900)

print("Налаштування завершено. Моніторинг CH1 активовано.")

# Функція для читання напруги (для перевірки)
def get_bus_voltage_ch1():
    data = bus.read_i2c_block_data(I2C_ADDR, 0x02, 2)
    val = (data[0] << 8) | data[1]
    # Напруга в регістрах даних також зсунута на 3 біти вправо (залежить від ревізії)
    # Але для спрощення в INA3221: 1 LSB = 8mV
    return (val >> 3) * 0.008

print(f"Поточна напруга на батареї: {get_bus_voltage_ch1():.2f} V")
