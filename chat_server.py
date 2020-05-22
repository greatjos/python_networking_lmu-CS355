# A chat server


import socketserver
import threading

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

names = {}

class ChatServer(socketserver.StreamRequestHandler):
    def handle(self):
        self.name = ''
        nameAdded = False
        self.wfile.write('Please enter your name: \n'.encode('utf-8'))

        while not nameAdded:
            self.name = self.rfile.readline().decode('utf-8').rstrip()
            if self.name in names.keys():
                self.wfile.write(f'ERROR: {self.name} already in use\n'.encode('utf-8'))
            else:
                self.wfile.write('Name Accepted\n'.encode('utf-8'))
                nameAdded = True

        print(f'LOGIN request from {self.name}')
        for key,val in names.items():
            val.write(f'{self.name} has connected\n'.encode('utf-8'))
        
        names[self.name] = self.wfile

        try:
            self.chatOperations()
        except Exception as e:
            print(e)
        finally:
            if self.wfile is not None:
                names.pop(self.name)
            else:
                for key,val in names.items():
                    if key == self.name:
                        names.pop(key)
                        break
            print(f'{self.name} disconnected')
            for key,val in names.items():
                val.write(f'{self.name} has left the chat\n'.encode('utf-8'))

    def chatOperations(self):
        while True:
            data = self.rfile.readline().decode('utf-8').rstrip()
            if not data:
                break
            cmd = data.split()[0]

            if cmd == 'SEND' and len(data.split()) > 1:
                user = data.split()[1]
                dataSent = False
                for key,val in names.items():
                    if key == user:
                        msg = ' '.join(data.split()[2:])
                        if msg is None:
                            break
                        print(f'SEND request from {self.name} to {user}')
                        val.write(f'From {self.name}: {msg}\n'.encode('utf-8'))
                        dataSent = True
                        break
                if not dataSent:
                    self.wfile.write(f'Could not send msg to {user}\n'.encode('utf-8'))

            elif cmd == 'LIST':
                self.wfile.write('Users logged in:\n'.encode('utf-8'))
                print(f'LIST request from {self.name}')
                for key,val in names.items():
                    self.wfile.write(f'{key}\n'.encode('utf-8'))

            elif cmd == 'LOGOUT':
                print(f'LOGOUT request from {self.name}')
                self.wfile.write(f'Goodbye...\n'.encode('utf-8'))
                break

            else:
                for key,val in names.items():
                    val.write(f'{self.name}: {data}\n'.encode('utf-8'))


with ThreadedTCPServer(('', 53211), ChatServer) as server:
    print(f'The chat server is running...')
    server.serve_forever()