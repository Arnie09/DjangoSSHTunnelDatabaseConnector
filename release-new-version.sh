#!/bin/bash

tag_version=$1
echo "New Release version: $tag_version"

python setup.py sdist

git add .
git commit -m "New Release version: $tag_version"
git push
git tag $tag_version
git push origin --tags

twine upload dist/*