# coding=utf-8
import setuptools

setuptools.setup(
    name='s3select',
    version='0.0.13',
    scripts=['s3select'],
    author="Marko Baštovanović",
    author_email="marko.bast@gmail.com",
    description="S3 select utility package",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/marko-bast/s3select",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests[security]>=2.18.3',
                      'pyasn1>=0.4.2',
                      'boto3>=1.7.79']
)
