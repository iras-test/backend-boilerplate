from setuptools import setup, find_packages

setup(
    name='backend-boilerplate',
    version='0.1.1',
    author='Sunday Deogratias',
    author_email='sundaydeogratias8@gmail.com',
    description='A wrapper package for django services',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/iras-test/backend-boilerplate',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=[
        'Django',
        'djangorestframework',
        'urllib3',
        'django-activity-stream',

    ],
)