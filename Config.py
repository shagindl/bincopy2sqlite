FWM_DAT = "FWM_DATA"
FWM_INFO = "FWM_INFO"
NAMES_TBL = [FWM_DAT, FWM_INFO]
ADDR_FWM_BASE =  0x8000000
SIZE_FWM =       0x0080000
ADDR_RENEW =     0x800C000
SIZE_RENEW =     (ADDR_FWM_BASE + SIZE_FWM - ADDR_RENEW)
OFFSET_RENEW_VER = 0x000C40C
OFFSET_RENEW_SIZE = (OFFSET_RENEW_VER + 4)
OFFSET_FWM_CRC = 0x007FFF8
ADDR_INT_FLASH = 0x800C400
SIZE_INT_FLASH = 0x0000100
