with open('requirements.txt') as reqs:
    install_requires = [req.strip() for req in reqs.readlines()]
