## Syntax

Awk 脚本包含 3 部分：Begin（`BEGIN {}`），Body（`/pattern/ {}`） 和 End（`END {}`）。

可以直接启动 awk，

```bash
awk '{ print }' x.txt
```

也可以运行 awk 脚本。

```bash
awk -f y.awk x.txt
```

使用 `-v` 指定变量。

```bash
awk -v x=X 'BEGIN{printf "x=%s\n", x}'
```

## Examples

### print columns

```bash
awk '/a/ {print $3 "\t" $4}' marks.txt
```

### Counting

```bash
awk 'BEGIN { cnt = 0 } /a/ { ++cnt } END { print cnt }' marks.txt
```

### Printing Lines with More than 18 Characters

```bash
awk 'length($0) > 18' marks.txt
```

## Built-in Variables

```bash
awk 'BEGIN { 
   for (i = 0; i < ARGC - 1; ++i) { 
      printf "ARGV[%d] = %s\n", i, ARGV[i] 
   } 
}' one two three four
```

```bash
awk 'BEGIN { print ENVIRON["USER"] }'
```

```bash
awk 'END {print FILENAME}' marks.txt
```

`FS` represents the (input) field separator and its default value is space. You can also change this by using **-F** command line option.

```bash
awk 'BEGIN {print "FS = " FS}' | cat -vte
```

`NS` represents the number of fields in the current record.

`NR` represents the number of the current record. For instance.

```bash
awk 'BEGIN { print "B" } NR < 3 { print NF, "$" } END { print "E" }' marks.txt
```

`OFS` represents the output field separator and its default value is space.

## Operators

```bash
awk 'BEGIN { a = 50; b = 20; print "(a + b) = ", (a + b) }'
```

```bash
awk 'BEGIN {
   num = 5; if (num >= 0 && num <= 7) printf "%d is in octal format\n", num 
}'
```

Space is a string concatenation operator that merges two strings.

```bash
awk 'BEGIN { str1 = "H"; str2 = "W"; str3 = str1 str2; print str3 }'
```

## Control Flow

```bash
awk 'BEGIN {
   a = 30;
   if (a==10) {
       print "a = 10";
   } else if (a == 20)
       print "a = 20";
   else if (a == 30)
       print "a = 30";
}'
```

```bash
awk 'BEGIN { for (i = 1; i <= 5; ++i) print i }'
```

```bash
awk 'BEGIN {i = 1; while (i < 6) { print i; ++i } }'
```

## Regular Expression

`.` matches any single character except the end of line character. For instance, the following example matches **fin, fun, fan** etc.

```bash
echo -e "cat\nbat\nfun\nfin\nfan" | awk '/f.n/'
```

`^` matches the start of line.

`$` matches the end of line.

`[]` is used to match only one out of several characters. In exclusive set, the carat negates the set of characters in the square brackets.

```bash
echo -e "Call\nTall\nBall" | awk '/[CT]all/'
echo -e "Call\nTall\nBall" | awk '/[^CT]all/'
```

A `|` allows regular expressions to be logically ORed. For instance, the following example prints **Ball** and **Call**.

```bash
echo -e "Call\nTall\nBall\nSmall\nShall" | awk '/Call|Ball/'
```

`?` matches zero or one occurrence of the preceding character.

`*` matches zero or more occurrences of the preceding character.

`+` matches one or more occurrence of the preceding character.

### Grouping

**Parentheses ()** are used for grouping and the character | is used  for alternatives. For instance, the following regular expression matches the lines containing either **Apple Juice or Apple Cake**.

```bash
echo -e "Apple Juice\nApple Pie\nApple Tart\nApple Cake" | awk 
   '/Apple (Juice|Cake)/'
```

