import socket
import enum
from pathlib import Path
import os
import json

class Client:
    def __init__(self):
        self.HOST = "localhost"
        with open('config.json') as f:
            data = json.load(f)
        self.PORT_COMMAND = data['commandChannelPort']
        self.PORT_DATA = data['dataChannelPort']

    def run(self):
        socket_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_command.connect((self.HOST, self.PORT_COMMAND))
        socket_data.connect((self.HOST, self.PORT_DATA))

        while True:
            
            _input = input("ftp> ")
            socket_command.sendall(_input.encode())
            if _input == '':
                continue
            
            data = socket_command.recv(2048)
            print(data.decode())

            if data.decode() == "226 List transfer done.": # LIST response
                data_len = 0
                count = 0
                whole_data = ""
                data_len = int(socket_data.recv(13).decode())
                while count < data_len:
                    datadata = socket_data.recv(10)
                    count += len(datadata)
                    whole_data += datadata.decode()
                spdata = whole_data.split('$$')
                if spdata[0] == "":
                    pass
                else:
                    for item in spdata:
                        print(item)

            if data.decode() == "226 Successful Download.": # DL response
                data_len  = 0
                count = 0
                with open(os.path.join(Path.home(), f"Downloads/{_input.split(' ')[1].split('/')[-1]}"), 'wb') as file_to_write:
                    data_len = int(socket_data.recv(13).decode())
                    while count < data_len:
                        datadata = socket_data.recv(10)
                        count += len(datadata)
                        file_to_write.write(datadata)
                    file_to_write.close()
            
        socket_command.close()
        socket_data.close()

if __name__ == '__main__':
    client = Client()
    client.run()