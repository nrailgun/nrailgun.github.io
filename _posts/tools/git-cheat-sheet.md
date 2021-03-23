# Git Cheat Sheet

查看所有更改的文件

```bash
git diff --name-only HEAD~2 HEAD
```

去掉 `--name-only` 可以看内容。

---

暂存本分支 diff：

```bash
git stash
```

然后切换回来之后：

```bash
git stash pop
```

---

squeeze 掉垃圾 commit

```bash
git rebase -i HEAD~N
```

N 是要合并掉的 commit 数量。

---

重命名分支

```bash
git branch -m <name>
```

---

大文件管理

```bash
# https://git-lfs.github.com/

git lfs install
git lfs track "*.psd"
git add .gitattributes
```

---

找到具有某个 md5sum 的文件

```bash
#!/usr/bin/env bash
# -*- encoding: utf-8 -*-

FILE=$1
CHECKSUM=$2

REVS=`git log --pretty=%H -- $FILE`
echo 'revs modified file: ' $REVS

for rev in $REVS; do
  echo 'rev' $rev
  echo 'file md5' `git show $rev:$FILE | md5sum`
done
```

---

create and apply patch

```bash
git format-patch -1 HEAD
git apply x.patch
```

