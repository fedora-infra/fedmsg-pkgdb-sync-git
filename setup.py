# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='fedmsg_pkgdb2branch',
    version='0.1',
    description='A fedmsg consumer that runs the pkgdb2branch based on fedmsg FAS messages',
    license="LGPLv2+",
    author='Janez Nemanič, Ralph Bean and Pierre-Yves Chibon',
    author_email='admin@fedoraproject.org',
    url='https://github.com/fedora-infra/fedmsg-pkgdb2branch',
    install_requires=["fedmsg", "fedmsg_meta_fedora_infrastructure"],
    packages=[],
    py_modules=['fedmsg_pkgdb2branch'],
    entry_points="""
    [moksha.consumer]
    fedmsg_pkgdb2branch = fedmsg_pkgdb2branch:FasClientConsumer
    """,
)
