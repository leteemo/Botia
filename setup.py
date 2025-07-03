from setuptools import setup, find_packages

setup(
    name='Botia',
    version='0.1.0',
    author='Khoussein Maalov',
    description='Create your own script to automate actions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/leteemo/Botia',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[ 
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    install_requires=[
        'PySide2',
        'numpy',
        'requests',
        'pytest',
        'NodeGraphQt',
        'pyautogui',
        'opencv-python',
        'bs4',
        'matplotlib',
        'mss'
    ],
)