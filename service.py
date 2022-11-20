"""This file contains service functions"""


def is_prime(n):
    for i in range(2, n):
        if (n % i) == 0:
            return False
    return True


def nsd(a, b):
    if a == 0:
        return b
    while b != 0:
        if a > b:
            a -= b
        else:
            b -= a
    return a


def euler_func(a):
    res = 0
    for i in range(1, a + 1):
        if nsd(a, i) == 1:
            res += 1
    return res


def find_reverse(a, b, m):
    res = []
    d = nsd(a, m)
    if b % d != 0:
        print("Нема рішень")
        return
    if d == 1:
        return (b * a**(euler_func(m) - 1)) % m
    else:
        m1 = int(m / d)
        x = (b * a**(euler_func(m1) - 1)) % m1
        res.append(x)
        d -= 1
        while d:
            res.append(x+m1)
            x += m1
            d -= 1
        return res

