# CrystalMatch - Deployment

This application is intended for deployment on a beamline control machine.

It is now deployed as part of the local Python environment - dls-python.

It is installed as all other internal python packages in:

/dls_sw/prod/common/python/RHEL6-x86_64/CrystalMatch

In order to install a new version internally follow the steps in Release Procedure.

The module can also be released externally on pypi (see relevant steps in Release Procedure).
The external release procedure is not required and does not affect the internal release in any way.

## Release Procedure

1. Bump the version number
2. Update release notes and dev notes
3. Push the changes to gitlab (git push gitlab_new master) and github origins (origin)
4. Make sure that all unit tests pass on Travis and run system test locally and check that they pass
5. External release on pypi:
    1. activate your virtual environment (source venv/bin/activate):
    ```
    pip install --upgrade pip setuptools docutils wheel
    python setup.py sdist
    python setup.py bdist_wheel #this one worked for wheel==0.31.0 but not recent release
    ```
    2. exit your virtual environment (decativate) and do:
    ```
    module load python/ana
    python -m pip install --user --upgrade twine
    python -m twine upload dist/*
    ```
    3. To test the released script do:
    ```
    virtualenv -p /dls_sw/prod/tools/RHEL6-x86_64/Python/2-7-3/prefix/bin/dls-python venv_cmd --system-site-packages
    source venv_cmd/bin/activate
    pip install --upgrade pip setuptools
    pip install CrystalMatch
    CrystalMatch image.jpg focusing_dict 1800,1690 --scale 1.0:1.575
    ```
6. Create a new release on github and add the whl and tar.gz files - the release will be tagged
7. Do internal release for dls-python:
    1. Push the changes and add a tag:
    ```
    git push gitlab-python3 python3
    git tag -a 2.0.0 -m "Release 2.0.0"
    git push gitlab-python3 2.0.0
    ```
    2. Run release script, wait for the build to finish and configure the path:
    ```
    dls-release.py --python3 -r 7 -e R3.14.12.7 CrystalMatch 2.0.0
    dls-last-release.sh -w
    configure-ioc edit python3 CrystalMatch 2.0.0
    ```
    3. Test the released script:
    ```
    CrystalMatch image.jpg focusing_dict 1800,1690 --scale 1.0:1.575
    ```

## Old Deployment

The deployment was before done by putting a script build using pyinstaller on a server.
The old location of 'CrystalMatch' was /dls_sw/dasc/CrystalMatch.
Although the location is not used to keep the code anymore it contains config files used by GDA.
