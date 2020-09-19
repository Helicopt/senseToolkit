from senseTk.functions import LAP_Matching


def cost_func1(i, j):
    mat = [
        [2, 1, 1, 1],
        [1, 1, 2, 1],
        [2, 2, 1, 2],
        [1, 2, 1, 1],
    ]
    return mat[i][j]


def cost_func2(i, j):
    mat = [
        [0, 0, 0, 0.01],
        [0.01, 0.01, 0.02, 0.1],
        [0.02, 0.2, 0.01, 0.02],
        [0.01, 0.02, 0.1, 0.01],
    ]
    return mat[i][j]


def test_matching_0():
    L = [0, 1]
    R = [0, 1]
    try:
        ma, l, r = LAP_Matching(L, R, cost_func1, Lapsolver='nnnnn')
    except NotImplementedError:
        pass


def test_matching_1():
    L = []
    R = []
    ma, l, r = LAP_Matching(L, R, cost_func1)
    assert len(ma) == 0
    assert len(l) == 0
    assert len(r) == 0

    L = [i for i in range(4)]
    R = [i for i in range(4)]
    ma, l, r = LAP_Matching(L, R, cost_func1)
    mans = [(0, 0), (1, 2), (2, 3), (3, 1), ]
    assert len(ma) == len(mans)
    for i, j in zip(ma, mans):
        assert i == j
    assert len(l) == 0
    assert len(r) == 0


def test_matching_2():
    L = [i for i in range(4)]
    R = [i for i in range(4)]
    ma, l, r = LAP_Matching(L, R, cost_func2, CostFirst=True)
    mans = [(1, 3), (2, 1), (3, 2), ]
    lans = [0]
    rans = [0]
    assert len(ma) == len(mans)
    assert len(l) == 1
    assert len(r) == 1
    for i, j in zip(ma, mans):
        assert i == j
    for i, j in zip(l, lans):
        assert i == j
    for i, j in zip(r, rans):
        assert i == j

    ma, l, r = LAP_Matching(L, R, cost_func2)
    mans = [(0, 3), (1, 0), (2, 1), (3, 2), ]
    assert len(ma) == len(mans)
    assert len(l) == 0
    assert len(r) == 0
    for i, j in zip(ma, mans):
        assert i == j


def test_matching_3():
    L = [i for i in range(4)]
    R = [i for i in range(4)]
    ma, l, r = LAP_Matching(L, R, cost_func1, Lapsolver='scipy')
    mans = [(0, 0), (1, 2), (2, 3), (3, 1), ]
    assert len(ma) == len(mans)
    for i, j in zip(ma, mans):
        assert i == j
    assert len(l) == 0
    assert len(r) == 0

    L = [i for i in range(4)]
    R = [i for i in range(4)]
    ma, l, r = LAP_Matching(L, R, cost_func2, Lapsolver='scipy')
    mans = [(0, 0), (1, 3), (2, 1), (3, 2), ]
    assert len(ma) == len(mans)
    assert len(l) == 0
    assert len(r) == 0
    for i, j in zip(ma, mans):
        assert i == j
