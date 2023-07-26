from setuptools import setup

with open('README.md','r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hust_login',
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    description='A python-lib for authenticating HustPass@2023',
    author='MarvinTerry',
    author_email='marvinterry2004@gmail.com',
    maintainer='Jackhr-arch',
    maintainer_email='63526062+Jackhr-arch@users.noreply.github.com',
    url='https://github.com/MarvinTerry/HustLogin',
    packages=['hust_login'],
    license='MIT',
    long_description=long_description,
    long_description_content_type = 'text/markdown',
    install_requires=[
        'Pillow>=10.0.0',
        'pycryptodome>=3.18.0',
        'pytesseract>=0.3.10',
        'Requests>=2.31.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
