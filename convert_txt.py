import json
import os
from binascii import unhexlify

fmt24 = '%06x'
fmt32 = '%08x'

if __name__ == '__main__':
    json_string = "["
    f = open("data.txt", "r")
    json_string += f.read()
    f.close()
    json_string += "]"
    data = json.loads(json_string)
    for data_obj in data:
        binary_data = unhexlify(fmt32 % int(data_obj[0]/1000))
        binary_data += unhexlify(fmt32 % int(data_obj[1]))
        binary_data += unhexlify(fmt24 % int(data_obj[2]))
        if not os.path.exists("data.bin"):
            out_file = open("data.bin", "w+b")
            out_file.write(binary_data)
            out_file.close()
        else:
            if os.path.getsize("data.bin") < 22:
                out_file = open("data.bin", "a+b")
                out_file.write(binary_data)
                out_file.close()
            else:
                out_file = open("data.bin", "r+b")
                out_file.seek(-22, 2)
                file_data = out_file.read()
                if file_data[4:8] == file_data[15:19] and file_data[8:11] == file_data[19:22] and \
                                binary_data[4:8] == file_data[15:19] and binary_data[8:11] == file_data[19:22]:
                    out_file.seek(-11, 2)
                    out_file.write(binary_data)
                    out_file.truncate()
                else:
                    out_file.write(binary_data)
                    out_file.close()


