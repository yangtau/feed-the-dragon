class A:
    def __init__(self):
        print('__init__: A')
        self.a = 20

    def show(self):
        print(self.a)

class B(A):
    def __init__(self):
        super().__init__()
        self.a = 10

b = B()
b.show()

