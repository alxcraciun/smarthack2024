# Aici faci tu Stefan structura de date
class Action:
    def __init__(self, pipe, cantitate):
        self.pipe = pipe
        self.cantitate = cantitate

    def Valid(self):
        return self.cantitate > 0


# Clasa de actiuni efectuate in fiecare zi
class Actions:
    def __init__(self):
        self.liste = [[] for _ in range(43)]

    def adauga(self, action,zi):
        self.liste[zi].append(action)

    def obtine_zi(self,zi):
        return self.liste[zi]


# Clasa singleton care contine toate trasele client<->rafinarie
class Rute(object):
    instance = None
    def __calculeaza(self):
        drumuri = dict()
        # code
        self.drumuri = drumuri

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Rute, cls).__new__(cls)
            cls.instance.__calculeaza()
        return cls.instance.drumuri


def day(nr, events):
    # ce se intampla intr-o zi
    pass