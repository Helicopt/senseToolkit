from pytest import approx
from senseTk.common import *
from senseTk.magic.hp_optimizer import HyperParamOptimizer, HyperParamHolder as HP, HyperParamGroup as HG


def test_hpo_0():
    HO = HyperParamOptimizer('test1', sample_num=9)

    inputs = [
        Det(10, 10, 5, 5, confidence=0.1),
        Det(20, 10, 5, 5, confidence=0.2),
        Det(30, 10, 5, 5, confidence=0.3),
        Det(40, 10, 5, 5, confidence=0.4),
        Det(50, 10, 5, 5, confidence=0.5),
        Det(60, 10, 5, 5, confidence=0.6),
        Det(70, 10, 5, 5, confidence=0.7),
        Det(80, 10, 5, 5, confidence=0.8),
        Det(90, 10, 5, 5, confidence=0.9),
        Det(100, 10, 5, 5, confidence=0.4),
        Det(110, 10, 5, 5, confidence=0.2),
        Det(120, 10, 5, 5, confidence=0.3),
    ]
    groundtruth = [
        Det(60, 10, 5, 5, confidence=0.6),
        Det(70, 10, 5, 5, confidence=0.7),
        Det(80, 10, 5, 5, confidence=0.8),
        Det(90, 10, 5, 5, confidence=0.9),
        Det(100, 10, 5, 5, confidence=0.4),
    ]

    @HO.optimize(hyper_params=HG(
        HP('score_thr', 'range', (0.1, 0.9, 0.1)),
    ))
    def filter_det(dets, score_thr=0.5):
        ret = []
        for det in dets:
            if det.conf < score_thr:
                continue
            else:
                ret.append(det)
        return ret

    @HO.evaluate(map_to=filter_det)
    def eval_filter_det(out):
        fp = 0
        fn = 0
        for d in out:
            found = False
            for g in groundtruth:
                if d.iou(g) > 0.5:
                    found = True
                    break
            if not found:
                fp += 1
        for g in groundtruth:
            found = False
            for d in out:
                if d.iou(g) > 0.5:
                    found = True
                    break
            if not found:
                fn += 1
        return len(inputs) + len(groundtruth) - fp - fn

    filter_det(inputs, score_thr=HP)
    print(HO._data)
    HO.remove()
    hp = HO.get_hyper_params()
    print(hp)
    assert approx(hp['score_thr']) == 0.6


def test_hpo_1():
    HO = HyperParamOptimizer('test2', sample_num=9)

    inputs = [
        Det(10, 10, 5, 5, confidence=0.1),
        Det(20, 10, 5, 5, confidence=0.2),
        Det(30, 10, 5, 5, confidence=0.3),
        Det(40, 10, 5, 5, confidence=0.4),
        Det(50, 10, 5, 5, confidence=0.5),
        Det(60, 10, 5, 5, confidence=0.6),
        Det(70, 10, 5, 5, confidence=0.7),
        Det(80, 10, 5, 5, confidence=0.8),
        Det(90, 10, 5, 5, confidence=0.9),
        Det(100, 10, 5, 5, confidence=0.4),
        Det(110, 10, 5, 5, confidence=0.2),
        Det(120, 10, 5, 5, confidence=0.3),
    ]
    groundtruth = [
        Det(60, 10, 5, 5, confidence=0.6),
        Det(70, 10, 5, 5, confidence=0.7),
        Det(80, 10, 5, 5, confidence=0.8),
        Det(90, 10, 5, 5, confidence=0.9),
        Det(100, 10, 5, 5, confidence=0.4),
    ]

    @HO.optimize(hyper_params=HG(
        HP('score_thr1', 'range', (0.1, 0.9, 0.1)),
        HP('score_thr2', 'range', (0.1, 0.9, 0.1)),
        sample_num=81))
    def filter_det(dets, score_thr1=0.5, score_thr2=0.5):
        ret = []
        for det in dets:
            if det.conf < score_thr1 + score_thr2:
                continue
            else:
                ret.append(det)
        return ret

    @HO.evaluate(map_to=filter_det)
    def eval_filter_det(out):
        fp = 0
        fn = 0
        for d in out:
            found = False
            for g in groundtruth:
                if d.iou(g) > 0.5:
                    found = True
                    break
            if not found:
                fp += 1
        for g in groundtruth:
            found = False
            for d in out:
                if d.iou(g) > 0.5:
                    found = True
                    break
            if not found:
                fn += 1
        return len(inputs) + len(groundtruth) - fp - fn

    filter_det(inputs, score_thr1=HP, score_thr2=HP)
    print(HO._data)
    HO.remove()
    hp = HO.get_hyper_params()
    print(hp)
    assert approx(hp['score_thr1']+hp['score_thr2']) == 0.6
