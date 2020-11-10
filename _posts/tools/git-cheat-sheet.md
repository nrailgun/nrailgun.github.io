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

