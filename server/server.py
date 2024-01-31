import socket
import threading
import json
import datetime

import utils
import DataStructures.connections as connections
from DataStructures.connections import Connection

# list[connection]
live_connections = []

# connections with missed data like username
# for now it's only username
wait_list_connections = []

# server global vars
server = None

def main():
    global server
    try:
        # load the config from the config file
        config = utils.load_config("config/config.ini")

        # create the server socket
        server = socket.socket()

        IP = config["SOCKET"]["SERVER_ADDRESS"]
        PORT = int(config["SOCKET"]["SERVER_PORT"])

        server.bind((IP, PORT))
        server.listen(int(config["SOCKET"]["MAX_USERS"]))

        utils.server_print("The server is online on: " + IP + "/" + str(PORT))

        # load users into the server
        while True:
            client_socket, client_address = server.accept()
            con = Connection(client_address, client_socket)

            # check if there is a connection from the same computer
            # a multi connections from the same computer is not allow!
            if client_address in [c.data['address'] for c in live_connections] + [c.data['address'] for c in wait_list_connections]:
                client_socket.close()

            wait_list_connections.append(con)
            thread = threading.Thread(target=handle_client, args=[con])
            thread.start()

    except Exception as e:
        utils.server_print(str(e))
    finally:
        print("Server is close!")

def handle_client(con: Connection):
    # (...) add db for messages.
    # (...) create a format for the db, interface...
    # (...) load old messages!
    # (...) add cache to client, think of a way to know if the client have the old message or not, hashing.

    # replace the event long string (all the strings) to code (number)

    try:
        # send the client that the connection has been successful.
        # response (json) format: {event: '', data?: {}}
        con.connection.send(json.dumps({'event': 'connection_initialized'}).encode())
        utils.server_print("A new connection has been initialized, " + str(con.data))

        # for now, we assume that the user is automatically in the wait list.
        while True:
            # read the client request to the server.
            # request (json) format: {event: '', data: {}}
            request = json.loads(con.connection.recv(1024).decode())

            if not ('event' in request.keys() and 'data' in request.keys()):
                con.connection.send(json.dumps({'event': 'bad_formatting'}).encode())
                continue

            # take the current datetime immediately.
            time = datetime.datetime.now()

            if con.status == connections.Status.Wait:
                # 1. wait until the user give his username.
                # 2. add the username to the data section.
                # 3. transfer the connection from the wait list to the live connections.
                # 4. change status to live.
                # 5. update all the live users that a new user join the chat.

                # username requirements:
                # 1. username length > 1.
                # 2. username not taken already.
                if request['event'] == "update_username" and 'username' in request['data'].keys() and len(request['data']['username']) > 1:
                    if request['data']['username'] in [c.data['username'] for c in live_connections]:
                        con.connection.send(json.dumps({'event': 'username_already_exists'}).encode())
                        continue

                    # add the username to the data section.
                    con.data['username'] = request['data']['username']

                    # transfer the connection from the wait list to the live connections.
                    live_connections.append(con)
                    wait_list_connections.remove(con)
                    utils.server_print("A connection redirected from the wait list to the live connections, " + str(con.data))

                    # update the status.
                    con.status = connections.Status.Live

                    # reply to the client.
                    con.connection.send(json.dumps({'event': 'redirected_to_live'}).encode())

                    # update all the live users about the new connection
                    for client_connection in live_connections:
                        client_connection.connection.send(json.dumps({'event': 'new_connection', 'data': {'username': request['data']['username'], 'time': time.strftime("%m-%d-%Y %H:%M:%S")}}).encode())

            elif con.status == connections.Status.Live:
                # 1. wait utils the user send a message.
                # 2. send the message to all users.

                # new message requirements:
                # 1. content length > 0.
                # 2. (...) custom message types, discord embed style...

                if request['event'] == "new_message" and 'content' in request['data'].keys() and len(request['data']['content']) > 0:
                    request['data']['author'] = con.data['username']
                    request['data']['time'] = time.strftime("%m-%d-%Y %H:%M:%S")

                    utils.server_print("New message: " + str(request['data']))

                    # send the new message to all clients.
                    # (!) maybe send it in new thread.
                    for client_connection in live_connections:
                        client_connection.connection.send(json.dumps(request).encode())

    except Exception as e:
        utils.server_print(str(e))
    finally:
        # remove the connection from the connection list
        if con.status == connections.Status.Wait:
            wait_list_connections.remove(con)
        elif con.status == connections.Status.Live:
            live_connections.remove(con)

        con.connection.close()
        utils.server_print("A connection with a client closed, " + str(con.data))

if __name__ == '__main__':
    main()
