"""Main"""

import os
import unittest


def suite():
    """Discover test suite."""
    return unittest.defaultTestLoader.discover(
        os.path.dirname(os.path.realpath(__file__))
    )


def run():
    """Run the test suite."""
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(suite())
    if test_result.errors or test_result.failures:
        raise RuntimeError("There are test failures")

if __name__ == "__main__":
    run()