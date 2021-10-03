from setuptools import setup


def read_requirements(fname):
    with open(fname) as file:
        lines = file.readlines()
        req = [line.strip() for line in lines]
    return req


requirements = read_requirements('requirements.txt')
setup(
    name='tetromiq',
    version='0.1',
    packages=['src'],
    url='',
    license='MIT',
    author='tetromiq',
    author_email='tetromiq@gmail.com',
    description='Quantum Games Hackaton 2011',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    include_package_data=True,
    install_requires=requirements,
)
