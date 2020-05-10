---
layout: post
title: "Shell Cheat Sheet"
categories: uncategorized
date: 2020-05-10 00:00:00
---

﻿# Tricks

## For loop

```bash
for ((i = 1; i < 100; i++)) do
	echo $i
done
```

## Cat a range of a file

```bash
awk 'NR >= 42 && NR <= 80' ${FILENAME}
```

## Iterate in 2 files
```bash
while read i <&3 && read j <&4; do
    # op $i $j
done 3<$IFILE 4<&JFILE
```

## Every 3 line
```bash
awk 'NR % 3 == 0' myfile
```

## Be careful with lasting backslash
```bash
caffe train solver.prototxt
    --weights=iter_1000.caffemodel
```
It will be executed! And finally you will find out caffe didn't load any thing!

## List full path
```bash
ls -d -1 ${PWD}/dir
```

## Find out intersectino
```bash
sort f1 f2 | uniq -d
```

## Wait for children
```bash
for job in `jobs -p`; do
    wait $job
done
```

## Conditional execution

```bash
if [[ ${#FILES} -le $THREDHOLD ]]; then
    # ...
else
    # ...
fi
```

Use `-e` to test if a file exists.

## Brackets
`$(cmd)` to execute `cmd`, `$((j + i))` to execute expression, `${var}` to expand variables.

## Glob strip

```bash
# Strip prefix (greedy)
filename=${VARIABLE_NAME##PREFIX}

# Strip postfix (non-greedy)
dirname=${VARIABLE_NAME%POSTFIX}
```

## Merge 2 files line by line
```bash
paste f1 f2
```

## Split by delimiter
```bash
for i in $(echo $IN | tr ";" "\n")
do
  # process
done
```

# quotes

Every thing is shell scripts is string, so **quoting is extremely and unfortunately important** in shell programming.

## Type of quoting

- `''`: Remove any special mean of character, except `'`.
- `""`: Allow `$` substitution.
- ` `` `: Legacy command substitution, use `$()` instead.

## Effects

- Preserve unescaped metacharacters.
- Prevent field  splitting and glob pattern characters.
- Expand argument lists.
`${array[@]}` expands to a list of words.


# Array in shell programming

Array:  An array is a numbered list of strings: it maps integers to strings.

## Creating arrays

With `=()` syntax.
```bash
names=("John" "$USER")
```

Glob can also be used.
```bash
files=(~/*'.jpg')
```
# To list files

Do not use
```bash
l=$(ls)
l=($(ls))
```

Use
```bash
l=(*)
```

# Get element number

```bash
echo ${#array[@]}
```

# Expanding elements

We can use a for loop to iterate over the elements
```bash
for i in "${l[@]}"; do
    echo "$i"
done
```
We use the quoted form again here: `"${l[@]}"`. Bash replaces this syntax with each element in the array properly quoted.

Use `"${!l[@]}"` to loop over the indices of arrays.
```bash
for i in "${!l[@]}"; do
    echo "${l[i]}"
done
```
Since it works with sparse array, it better than `${#l[@]}`.

# Rename with pattern

```bash
for f in *.jpg; do
	mv $f $(echo $f | sed /s/OLD/NEW/);
done
```
