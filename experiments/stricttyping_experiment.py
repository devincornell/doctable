

def meth(a: int, b: int = 1):
    if b is None:
        b = 10
    return a*b

print(meth(1, 3))

