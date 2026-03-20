'''

this is the setup file for the project. 
It is used to install the required packages 
and dependencies for the project. 
It also contains the entry point for the project.



'''

from setuptools import setup, find_packages
from typing import List

HYPEN_E_DOT = '-e .'
def get_requirements(file_path:str)->List[str]:
    with open(file_path) as f:
        requirements = [
    line.strip()
    for line in f.read().splitlines()
    if line.strip() and not line.strip().startswith("#")
]
    if HYPEN_E_DOT in requirements:
        requirements.remove(HYPEN_E_DOT)
    return requirements

setup(
    name='Network_Security',
    version='0.0.1',
    author='Shammi',
    author_email='shammikumar3833@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements("requirements.txt")
    
    )