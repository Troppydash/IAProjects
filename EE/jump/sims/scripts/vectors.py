# vector ops
def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def vec_add(a, b):
    return [a[0] + b[0], a[1] + b[1]]


def vec_scale(a, c):
    return [a[0] * c, a[1] * c]
