from setuptools import setup, find_packages
import os

import shutil

for deleted_dir in ["./dist", "./build", "./.eggs", "./suvec.egg    -info"]:
    shutil.rmtree(deleted_dir, ignore_errors=True)


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(name="suvec",
      author='Arseny Protsenko',
      author_email="protsenkoar@gmail.com",
      url='https://github.com/ProtsenkoAI/skady-user-vectorizer',
      license="MIT",
      long_description=read("README.md"),
      packages=find_packages(),
      setup_requires=["wheel", "setuptools"],
      install_requires=["vk-api", "requests"],
      python_requires='>3.8.0',
      extras_require={
              'dev': [
                  "jupyterlab"
              ]
          }
      )
