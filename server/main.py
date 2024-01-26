import socket
import threading
import json

import utils
import Components.connections as connections
from Components.connections import connection

# list[connection]
live_connections = []

# connections with missed data like username
# for now it's only username
wait_list_connections = []

def main():
    try:
        # load the config from the config file
        config = utils.load_config("config/config.ini")

        # init the server
        server = socket.socket()
        server.bind((config["DEFAULT"]["SERVER_ADDRESS"], int(config["DEFAULT"]["SERVER_PORT"]) or int(config["DEFAULT"]["SERVER_RESERVE_PORT"])))
        server.settimeout(config["DEFAULT"]["CONNECTION_TIMEOUT"])
        server.listen(int(config["DEFAULT"]["MAX_USERS"]))

        # load users into the server
        while True:
            client_socket, client_address = server.accept()
            con = connection(client_address, client_socket)

            # check if there is a connection from the same computer
            # a multi connections from the same computer is not allow!
            if client_address not in [c.data.address for c in live_connections] + [c.data.address for c in wait_list_connections]:
                wait_list_connections.append(con)
                thread = threading.Thread(target=handle_client, args=con)
                thread.start()

    except Exception as e:
        utils.server_print(e)
    finally:
        print("Server is close!")

def handle_client(con: connection):
    try:
        # send the client that the connection has been successful
        # response (json) format: {event: '', data?: {}}
        con.connection.send(json.dumps({'event': 'connection_initialized'}).encode())

        # for now, we assume that the user is automatically in the wait list.
        while True:
            # read the client request to the server
            # request (json) format: {event: '', data: {}}
            request = json.loads(con.connection.recv(1024).decode())

            if not ('event' in request and 'data' in request):
                con.connection.send(json.dumps({'event': 'bad_formatting'}).encode())
                continue

            if con.status == connections.status.Wait:
                # 1. wait until the user give his username.
                # 2. add the username to the data section
                # 3. transfer the connection from the wait list to the live connections
                # 4. change status to live

                # username requirements:
                # 1. username length > 1
                # 2. username not taken already
                if request.event == "update_username" and 'username' in request.data and len(request.data.username) > 1:
                    if request.data.username in [c.data.username for c in live_connections]:
                        con.connection.send(json.dumps({'event': 'username_already_exists'}).encode())
                        continue

                    # add the username to the data section
                    con.data.username = request.data.username

                    # transfer the connection from the wait list to the live connections
                    live_connections.append(con)
                    wait_list_connections.remove(con)
                    utils.server_print("A connection redirected from the wait list to the live connections, " + con.data)

                    # update the status
                    con.status = connections.status.Live

                    # reply to the client
                    con.connection.send(json.dumps({'event': 'redirected_to_live'}).encode())

            elif con.status == connections.status.Live:
                # 1. wait utils the user send a message
                # 2. send the message to all users
                pass

    except Exception as e:
        utils.server_print(e)
    finally:
        con.connection.close()
        utils.server_print("A connection with a client closed, " + con.data)

if __name__ == '__main__':
    main()
