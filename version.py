import os
import subprocess
from sys import stdout

try:
    with open(os.devnull, 'w') as devnull:
        V = subprocess.check_output(['git', 'describe', '--tags', '--dirty', '--abbrev'], stderr=stdout).decode().strip()
    if '-' in V:
        BV = V[:V.index('-')]
        BV = BV[:BV.rindex('.') + 1] + str(int(BV[BV.rindex('.') + 1:]) + 1)
        SEMPRE = 'dirty' if V.endswith('-dirty') else 'commit'
        PIPPRE = 'alpha' if V.endswith('-dirty') else 'pre'
        BUILD = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        NUMBER_SINCE = subprocess.check_output(
            ['git', 'rev-list', V[:V.index('-')] + '..HEAD', '--count']).decode().strip()
        SEMVER = BV + '-' + SEMPRE + '+' + BUILD
        PIPVER = BV + PIPPRE + NUMBER_SINCE
        WINVER = V[:V.index('-')] + '.' + NUMBER_SINCE
    else:
        SEMVER = V
        PIPVER = V
        WINVER = V + '.0'

    with open('version', 'w') as f:
        print('Semantic version is ' + SEMVER)
        f.write(SEMVER)
    with open('pip_version', 'w') as f:
        print('PIP version is ' + PIPVER)
        f.write(PIPVER)
    with open('win_version', 'w') as f:
        print('Windows version is ' + WINVER)
        f.write(WINVER)
except Exception as e:
    print('Error calling git')
    print(e)
