import sys
import bincopy
import sqlite3
import Config

# if __name__ != r"__main__":
#     print(sys.version)
#     pass
    # url = uno.fileUrlToSystemPath( '{}/{}'.format(XSCRIPTCONTEXT.getDocument().URL,'Scripts/python/') )
    # if not url in sys.path: sys.path.insert(0, url )
class Bin2Db:
    def open_db(self, file_db, tables):
        con = sqlite3.connect(file_db)
        cur = con.cursor()
        for tb in tables:
            cur.execute("DELETE from \"" + tb + "\"")
        return con

    def __init__(self, file_db, file_hex):
        # -- Open SQLite db
        self.db = self.open_db(file_db, Config.NAMES_TBL)
        # -- Open hex fwm 0x08000000 B006      ADD      sp,sp,#0x18 <bytearray, len() = 1879179264>
        self.fwm_file = bincopy.BinFile(file_hex)
        self.fwm_name = '.'.join(file_hex.split('.')[:-1])
        pass
    def __del__(self):
        # -- Close DB
        self.db.commit()
        self.db.close()
        pass
    def _crc32_update(self, crc, v):
        CRC32_POLY = 0xEDB88320

        crc = crc ^ v;
        for i in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ CRC32_POLY;
            else:
                crc = (crc >> 1);

        return crc;
    def crc32_update(self, crc, v, size):
        for i in range(size):
            crc = self._crc32_update(crc, v[i]); 

        return crc;
    def insert_crc(self):
        # Calculated CRC
        self.crc = 0
        ADDR = Config.ADDR_FWM_BASE + Config.ADDR_FWM_CRC
        for address, data in self.fwm_file.segments:
            if address + len(data) > ADDR:
                INDX = ADDR - address
                for indx in range(len(data)):
                    if indx < INDX or (INDX + 4) <= indx:
                        self.crc = self._crc32_update(self.crc, data[indx])
            else:
                self.crc = self.crc32_update(self.crc, data, len(data))
        # Insert CRC
        for address, data in self.fwm_file.segments:
            if address + len(data) > ADDR:
                INDX = ADDR - address
                for indx in range(len(data)):
                    if INDX <= indx and indx < (INDX + 4):
                        data[indx : indx + 4] = self.crc.to_bytes(4, byteorder = 'big')
                        break
        pass

    def write_data_fwm(self, name_tbl):
        cur = self.db.cursor()
        self.num_items_data = 0

        for address, data in self.fwm_file.segments:
            addr = address
            size = 64
            Len = len(data)
            while Len > 0:
                size = min(Len, size)
                # cur.execute(''' INSERT INTO "FWM_DATA" VALUES (0, 16, '123456789ABCDEF') ''')
                req = "INSERT INTO \"" + name_tbl + "\" VALUES (" + str(addr) + ', ' + str(size) + ', \"'
                req += data[addr - address : addr - address + size].hex().upper() + '\")'

                cur.execute(req)
                # -- Next
                self.num_items_data += 1
                Len -= size
                addr += size
                pass
            pass
    
    def write_info_fwm(self, name_tbl):
        ADDR = Config.ADDR_FWM_BASE + Config.ADDR_FWM_VER
        for address, data in self.fwm_file.segments:
            if(address <= ADDR and ADDR <= (address + len(data))):
                addr_ver = ADDR - address
                data_ver = data[addr_ver : addr_ver + 4]
                ver = int.from_bytes(data_ver, byteorder='big', signed=False)
            pass

        # cur.execute(''' INSERT INTO "FWM_INFO" VALUES (ver, name, num_items_data) ''')
        req = "INSERT INTO \"" + name_tbl + "\" VALUES (" + str(ver) + ', \"' + self.fwm_name + '\", ' + str(self.num_items_data) + ")"
        self.db.cursor().execute(req)
        pass

    def Convert(self):
        # -- Fwm
        self.insert_crc()
        self.write_data_fwm(Config.FWM_DAT)
        self.write_info_fwm(Config.FWM_INFO)
        pass
        
        
    # Create table
    # cur.execute('''CREATE TABLE stocks
    #             (date text, trans text, symbol text, qty real, price real)''')
    # list_db = cur.fetchall()
    # cur.execute(''' INSERT INTO "FWM" VALUES (0, 16, '123456789ABCDEF') ''')
    # con.commit()

    # list_db = cur.execute('SELECT * FROM "FWM" ORDER BY "addr"')
    # list_db = cur.execute('SELECT * FROM "SystemSettings" ORDER BY "bSound"')
    # for row in list_db:
    #     print(row)
    pass

if __name__ == "__main__":
    # print(sys.path)
    # print(sys.version)
    cnv = Bin2Db(sys.argv[1], sys.argv[2])
    cnv.Convert()
    del cnv
    print("Convert complited!")

# bincopy info "./fwm.hex"