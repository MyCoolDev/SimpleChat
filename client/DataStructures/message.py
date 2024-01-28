class Message:
    def __init__(self, data: dict):
        self.author = data['author']
        self.content = data['content']
        self.time = data['time']

    def __str__(self):
        return f"({self.author}, {self.content}, {self.time})"
