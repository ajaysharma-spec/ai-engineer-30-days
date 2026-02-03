class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello {self.name}"

u = User("AI Engineer")
print(u.greet())
