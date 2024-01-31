import pygame

from DataStructures.message import Message
from Components.UI.TextBox import TextBox

pygame.font.init()

class Chat:
    # (...) add maximum size to each message.

    def __init__(self, size: pygame.Vector2, position: pygame.Vector2, message_margin: int):
        self.size = size
        self.position = position
        self.message_margin = message_margin

        self.scroll_point = 20

        self.message_style = MessageStyle((61, 61, 66), "Poppins", 25, 20, 25, (255, 255, 255), (173, 173, 173), (255, 255, 255), border_radius=15)

        self.messages = []
        self.msg_input = TextBox(pygame.Vector2(self.size.x, 50), pygame.Vector2(self.position.x, self.position.y + self.size.y - 50 - 30), (39, 39, 43), "Enter your message here", "Poppins", 25, (166, 166, 166), padding_left=30, border_radius=30)

    def add_message(self, msg):
        self.messages.append(msg)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                self.scroll_point += event.y * 10

    def update(self, events: list):
        self.handle_events(events)
        return self.msg_input.update(events)

    def render(self, surface: pygame.Surface):
        margin_top = 0

        for i, msg in enumerate(self.messages):
            margin_top += self.message_style.implement(pygame.Vector2(self.position.x, self.position.y + self.scroll_point + i * self.message_margin + margin_top), msg, surface).y

        if margin_top + self.message_margin * (len(self.messages) - 1) + self.scroll_point >= self.msg_input.position.y - 20:
            self.scroll_point -= margin_top + self.message_margin * (len(self.messages) - 1) + self.scroll_point - (self.msg_input.position.y - 20)

        self.msg_input.render(surface)

class MessageStyle:
    def __init__(self, color: tuple, font: str, author_font_size: int, time_font_size: int, content_font_size: int, author_text_color: tuple, time_text_color: tuple, content_text_color: tuple, author_margin: tuple = (15, 10), padding: tuple = (25, 15, 70, 35), padding_left: int = 0, padding_top: int = 0, padding_right: int = 0, padding_bottom: int = 0, width: int = 0, border_radius: int = -1, border_top_left_radius: int = -1, border_top_right_radius: int = -1, border_bottom_left_radius: int = -1, border_bottom_right_radius: int = -1):
        self.color = color
        self.padding = [x for x in padding]

        if padding_left != 0:
            self.padding[0] = padding_left
        if padding_top != 0:
            self.padding[1] = padding_top
        if padding_right != 0:
            self.padding[2] = padding_right
        if padding_bottom != 0:
            self.padding[3] = padding_bottom

        self.font = font
        self.author_font_size = author_font_size
        self.time_font_size = time_font_size
        self.content_font_size = content_font_size
        self.author_text_color = author_text_color
        self.time_text_color = time_text_color
        self.content_text_color = content_text_color
        self.author_margin = author_margin

        self.author_font = pygame.font.SysFont(font, author_font_size)
        self.time_font = pygame.font.SysFont(font, time_font_size)
        self.content_font = pygame.font.SysFont(font, content_font_size)

        self.width, self.border_radius, self.border_top_left_radius, self.border_top_right_radius, self.border_bottom_left_radius, self.border_bottom_right_radius = width, border_radius, border_top_left_radius, border_top_right_radius, border_bottom_left_radius, border_bottom_right_radius

    def implement(self, position: pygame.Vector2, data: Message, surface: pygame.Surface) -> pygame.Vector2:
        author_text = self.author_font.render(data.author, True, self.author_text_color)
        time_text = self.time_font.render(data.time, True, self.time_text_color)
        content_text = self.content_font.render(data.content, True, self.content_text_color)

        size = pygame.Vector2(self.padding[0] + self.padding[2] + max(author_text.get_width() + self.author_margin[0] + time_text.get_width(), content_text.get_width()),
                              self.padding[1] + author_text.get_height() + self.author_margin[1] + content_text.get_height() + self.padding[3])

        # render all the objects
        pygame.draw.rect(surface, self.color, pygame.Rect(position, size), self.width, border_radius=self.border_radius, border_top_left_radius=self.border_top_left_radius, border_top_right_radius=self.border_top_right_radius, border_bottom_left_radius=self.border_bottom_left_radius, border_bottom_right_radius=self.border_bottom_right_radius)
        author_text_position = pygame.Vector2(position.x + author_text.get_width() / 2 + self.padding[0], position.y + author_text.get_height() / 2 + self.padding[1])
        surface.blit(author_text, author_text_position)
        surface.blit(time_text, pygame.Vector2(author_text_position.x + author_text.get_width() + self.author_margin[0], author_text_position.y + author_text.get_height() / 2 - time_text.get_height() / 2))
        surface.blit(content_text, pygame.Vector2(author_text_position.x, author_text_position.y + author_text.get_height() + self.author_margin[1]))

        return size
