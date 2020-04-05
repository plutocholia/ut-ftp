import socket
import json
import logging
import threading
from Utills import ResState, mapCommands, FTPSocks

class ClientThread(threading.Thread):
    def __init__(self, ftpsocks):
        # self.socket_client_cmd = _socket_cmd
        # self.address_client_cmd = _address_cmd
        # self.socket_client_data= _socket_data
        # self.address_client_data = _address_data
        self.ftpsocks = ftpsocks
        threading.Thread.__init__(self)

    def run(self):
        msg = ''
        while True:
            data = self.ftpsocks.socket_cmd.recv(2048)
            message = data.decode()

            state = mapCommands(self.ftpsocks, message)
            if state == ResState.quit:
                break

            self.ftpsocks.socket_cmd.sendall(f"got ur message in state {state.name}".encode())
        
        # logging
        print ("# Client ", self.ftpsocks.address_cmd, self.ftpsocks.address_data , " is gone")
        logging.info(f"{self.ftpsocks.address_data} {self.ftpsocks.address_cmd} is gone")

        self.ftpsocks.socket_cmd.close()
        self.ftpsocks.socket_data.close()

class Server:
    def __init__(self):
        with open('config.json') as f:
            data = json.load(f)
        self.PORT_COMMAND = data['commandChannelPort']
        self.PORT_DATA = data['dataChannelPort']
        self.HOST = "localhost"
        self.LOGGING = data['logging']['enable']
        self.PATH_LOGGING = data['logging']['path']

        # configuration of logging
        logging.basicConfig(
            filename=self.PATH_LOGGING,
            filemode='a',
            format='%(asctime)s  %(name)s  %(levelname)s  %(message)s',
            level=logging.DEBUG
        )


    def run(self):
        logging.info(
            f"server is now running on data port of {self.PORT_DATA} and command port of {self.PORT_COMMAND}"
        )

        sock_command = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_data = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_command.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock_command.bind((self.HOST, 8080))
        sock_data.bind((self.HOST, 8081))

        while True:
            sock_command.listen()
            sock_data.listen()
            socket_client_cmd, address_client_cmd = sock_command.accept()
            socket_client_data, address_client_data = sock_data.accept()
            ftpsocks = FTPSocks(
                socket_client_cmd, 
                address_client_cmd, 
                socket_client_data, 
                address_client_data
            )
            print(f"{address_client_cmd} and {address_client_data} is connected")
            logging.info(f"{address_client_cmd} and {address_client_data} is connected")
            thread_client = ClientThread(ftpsocks)
            thread_client.start()




if __name__ == '__main__':
    server = Server()
    server.run()