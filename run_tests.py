import unittest


def run_tests(start_dir):
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    run_tests("./tests/")
