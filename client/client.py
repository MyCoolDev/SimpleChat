import socket
import json
import pygame
import threading

from Components.UI.Text import Text
from Components.chat import *
from Components.UI.TextBox import TextBox
from DataStructures.message import Message

import utils

class engine:
    def __init__(self):
        config = utils.load_config("config/config.ini")

        pygame.init()

        self.state = "connecting"

        self.screen = pygame.display.set_mode((int(config["WINDOW"]["WIDTH"]), int(config["WINDOW"]["HEIGHT"])))
        pygame.display.set_caption("SimpleChat")
        self.events = None
        self.running = True
        self.clock = pygame.time.Clock()
        self.dt = 0

        self.render_system = []

        self.client = socket.socket()
        self.client.settimeout(int(config["SOCKET"]["CONNECTION_TIMEOUT"]))

        self.username = ""
        self.username_input_size = pygame.Vector2(0.4 * self.screen.get_width(), 50)
        self.username_input = TextBox(self.username_input_size, pygame.Vector2(self.screen.get_width() / 2 - self.username_input_size.x / 2, self.screen.get_height() / 2), (39, 39, 43), "Enter a username...", "Poppins", 25, (166, 166, 166), padding_left=30, border_radius=30)

        self.chat_size = pygame.Vector2(0.5 * self.screen.get_width(), self.screen.get_height())
        self.chat = Chat(self.chat_size, pygame.Vector2(self.screen.get_width() / 2 - self.chat_size.x / 2, self.screen.get_height() - self.chat_size.y), 15)

        self.client_thread = threading.Thread(target=listen_response, args=[self.client, config, self])
        self.client_thread.start()

    def start(self):
        while self.running:
            # limit the fps to 60
            self.dt = self.clock.tick(60) / 1000

            self.screen.fill((0, 0, 0))

            self.events = pygame.event.get()
            self.handle_events()

            self.update()
            self.render()

            pygame.display.flip()

    def handle_events(self):
        for event in self.events:
            if event.type == pygame.QUIT:
                self.running = False
                self.client.send("close".encode('utf-8'))
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if self.state == "sign":
                    if self.username_input.text.color != (255, 255, 255):
                        self.username_input.text.update_color((255, 255, 255))

                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]

                    elif event.key == pygame.K_RETURN:
                        # the username requirement is that the username length is more than 1
                        # if the username is ok than send the username to the server
                        if len(self.username) > 1:
                            self.client.send(json.dumps({'event': 'update_username', 'data': {'username': self.username}}).encode())

                    elif event.unicode != "":
                        self.username += event.unicode

    def switch_state(self, new_state: str):
        self.render_system.clear()
        self.state = new_state

        if new_state == "sign":
            self.render_system.append(self.username_input)

        elif new_state == "chat":
            self.render_system.append(self.chat)

    def update(self):
        if self.state == "sign":
            self.username_input.update_text(self.username)
        elif self.state == "chat":
            if self.chat.update(self.events):
                self.client.send(json.dumps({'event': 'new_message', 'data': {'content': self.chat.msg_input.content}}).encode())
                self.chat.msg_input.update_text("")

    def render(self):
        for _obj in self.render_system:
            _obj.render(self.screen)

def listen_response(client: socket.socket, config: dict, eng: engine):
    try:
        client.connect((config["SOCKET"]["SERVER_ADDRESS"], int(config["SOCKET"]["SERVER_PORT"])))
        client.settimeout(None)

        while True:
            # read the server response to the client.
            # response (json) format: {event: '', data?: {}}
            response = json.loads(client.recv(1024).decode())

            if 'event' not in response.keys():
                continue

            if eng.state == "connecting":
                # connection_initialized
                if response['event'] == "connection_initialized":
                    eng.switch_state("sign")
            elif eng.state == "sign":
                # username_already_exists
                if response['event'] == "redirected_to_live":
                    eng.switch_state("chat")
                    print("Redirected to live")
                elif response['event'] == "username_already_exists":
                    eng.username_input.update_color((255, 0, 0))
            elif eng.state == "chat":

                if not ('data' in response.keys() and type(response['data']) == dict):
                    continue

                if response['event'] == "new_connection" and 'username' in response['data'].keys() and 'time' in response['data'].keys():
                    eng.chat.add_user_message({'username': response['data']['username'], 'time': response['data']['time']})

                # new_message
                if response['event'] == "new_message" and 'content' in response['data'].keys() and 'time' in response['data'].keys() and 'author' in response['data'].keys():
                    eng.chat.add_message(Message(response['data']))

    except Exception as e:
        print(e)
    finally:
        print("The client socket closed.")

def main():
    engine().start()


if __name__ == '__main__':
    main()
