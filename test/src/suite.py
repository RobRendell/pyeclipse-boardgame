import os
import sys
import unittest

test_root = os.path.dirname(__file__)
src_root = '../../main/src'
src_root = os.path.abspath(os.path.join(test_root, src_root))
if src_root not in sys.path:
    sys.path.append(src_root)
os.chdir(src_root)

modules = unittest.defaultTestLoader.discover(test_root, "*_test.py")
test_runner = unittest.TextTestRunner()
test_runner.run(modules)
