import unittest

import vivisect.symboliks.analysis as vsym_analysis

from vivisect.tests.helpers import MockVw


class MockVar(object):
    def __init__(self, va):
        self.va = va

    def solve(self, *args, **kwargs):
        return self.va


def nop(*args, **kwargs):
    pass


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.sfe = vsym_analysis.SymbolikFunctionEmulator(MockVw())
        self.sfe.setStackCounter = nop

    def test_getStackOffset_above(self, addr=0xbfbff000, size=16384):
        self.sfe.setStackBase(addr, size)
        offset = self.sfe.getStackOffset(MockVar(addr+1))

        self.assertIs(offset, None)

    def test_getStackOffset_inside(self, addr=0xbfbff000, size=16384):
        self.sfe.setStackBase(addr, size)
        offset = self.sfe.getStackOffset(MockVar(addr-1))

        self.assertIs(int(offset), -1)

    def test_getStackOffset_below(self, addr=0xbfbff000, size=16384):
        self.sfe.setStackBase(addr, size)
        offset = self.sfe.getStackOffset(MockVar(addr-size))

        self.assertIs(offset, None)


def cb_astNodeCount(path, obj, ctx):
    ctx['count'] += 1
    if len(path) > ctx['depth']:
        ctx['depth'] = len(path)
    # print("\n\t%r\n\t\t%s" % (obj, '\n\t\t'.join([repr(x) for x in path])))
