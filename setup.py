from setuptools import setup

with open('README.md','r', encoding='utf-8') as f:
    long_description = f.read()

def GetVersion():
    import git

    repo_path = '.'
    repo = git.Repo(repo_path)
    count = repo.git.rev_list('--count', 'HEAD')
    #commit_hash = repo.commit('main').hexsha[:7]

    with open('version','r') as fp:
        lastverison = fp.read()
        version = lastverison.split('.')
    version = version[0]+'.'+version[1]+'.'+str(int(version[2].split('(')[0])+1)+'({})'.format(count)

    with open('version','w') as fp:
        fp.write(version)
        
    return version

setup(
    name='hust_login',
    version=GetVersion(),
    description='A python-lib for authenticating HustPass@2023',
    author='MarvinTerry',
    author_email='marvinterry2004@gmail.com',
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