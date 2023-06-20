#!/bin/bash
set -x
set -e
cd /root/gitrs/IXPAGE
git fetch --all --force
git reset --hard origin/master
/root/arouteserver/scripts/gen_member_page.py
DATE=$(date +'%Y-%m-%d %H:%M:%S')
GIT_LAST_MSG=$(git log -1 --pretty=%B)
GIT_DIFF=$(git diff)

build_mkdocs=

while [ "$1" != "" ]; do
    case $1 in
        -b | --build )    build_mkdocs=1
                                ;;
    esac
    shift
done

if [ "$build_mkdocs" = "1" ]; then
  export SOURCE_DATE_EPOCH=$(date -d "$(git -C /root/gitrs/KSKB-IX log -1 --pretty="format:%ci" docs)"  +"%s")
  export PATH=`python3 -m site --user-base`/bin:$PATH
  mkdocs build
  gzip -f -n -k site/sitemap.xml
fi

git add -A
if  [[ $GIT_LAST_MSG == "sync members at"* ]] ;
then
    git diff-index --quiet HEAD || git commit -m "sync members at $DATE" --amend
    #git commit -m "sync members at $DATE"
else
    git diff-index --quiet HEAD || git commit -m "sync members at $DATE"
fi
git push -f
