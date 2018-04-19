import subprocess
import os

try:
    with open(os.devnull, 'w') as devnull:
        v = subprocess.check_output(['git', 'describe', '--dirty', '--abbrev'], stderr=devnull).decode().strip()
    if '-' in v:
        bv = v[:v.index('-')]
        bv = bv[:bv.rindex('.') + 1] + str(int(bv[bv.rindex('.') + 1:]) + 1)
        sempre = 'dirty' if v.endswith('-dirty') else 'commit'
        pippre = 'alpha' if v.endswith('-dirty') else 'pre'
        build = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        number_since = subprocess.check_output(['git', 'rev-list', v[:v.index('-')] + '..HEAD', '--count']).decode().strip()
        semver = bv + '-' + sempre + '+' + build
        pipver = bv + pippre + number_since
        winver = v[:v.index('-')] + '.' + number_since
    else:
        semver = v
        pipver = v
        winver = v + '.0'

    with open('version', 'w') as f:
        print('Semantic version is ' + semver)
        f.write(semver)
    with open('pip_version', 'w') as f:
        print('PIP version is ' + pipver)
        f.write(pipver)
    with open('win_version', 'w') as f:
        print('Windows version is ' + winver)
        f.write(winver)
except subprocess.CalledProcessError as e:
    print('Error calling git')

