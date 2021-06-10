import setuptools
import os

import shutil

# delete existing build paths
for deleted_dir in ["./dist", "./build", "./.eggs", "./suvec.egg"]:
    shutil.rmtree(deleted_dir, ignore_errors=True)


def _read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setuptools.setup(name="suvec",
                 author='Arseny Protsenko',
                 author_email="protsenkoar@gmail.com",
                 url='https://github.com/ProtsenkoAI/skady-user-vectorizer',
                 license="MIT",
                 long_description=_read("README.md"),
                 packages=setuptools.find_packages(),
                 setup_requires=["wheel", "setuptools"],
                 install_requires=["vk-api", "requests"],
                 python_requires='>3.8.0',
                 extras_require={
                     'dev': [
                         "jupyterlab"
                     ]
                 }
                 )
