#!/bin/bash

tag_version=$1

python setup.py sdist

git add .
git tag $tag_version
git push origin --tags

twine upload dist/*