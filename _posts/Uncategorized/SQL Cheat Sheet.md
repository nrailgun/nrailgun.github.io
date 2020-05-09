## CRUD

### Select

```sql
SELECT column1, column2, ...
FROM table_name;
```

use `DISTINCT` to return only distinct values.

```sql
SELECT DISTINCT column1, column2, ...
FROM table_name;
```

A field with a NULL value is a field with no value. If a field in a table is optional, it is possible to insert a new record or update a record without adding a value to this field.

```sql
SELECT column_names
FROM table_name
WHERE column_name IS NOT NULL;
```

`SELECT TOP` is not supported in all database systems. MySQL supports `LIMIT` to select to limited number of records.

```mysql
SELECT column_name(s)
FROM table_name
WHERE condition
LIMIT number;
```

### Where

```sql
SELECT column1, column2, ...
FROM table_name
WHERE condition
ORDER BY column1, column2, ... ASC|DESC;
```

Where clause can be combined with `AND`, `OR`, and `NOT` operators.

### Insert

```sql
INSERT INTO table_name (column1, column2, column3, ...)
VALUES (value1, value2, value3, ...);
```

### Update

```sql
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

### Delete

```sql
DELETE FROM table_name WHERE condition;
```

### Min and Max

```sql
SELECT MIN(column_name)
FROM table_name
WHERE condition;
```

```sql
SELECT MAX(column_name)
FROM table_name
WHERE condition;
```

### Count, Avg, and Sum

```sql
SELECT COUNT(column_name)
FROM table_name
WHERE condition;
```

```sql
SELECT AVG(column_name)
FROM table_name
WHERE condition;
```

```sql
SELECT SUM(column_name)
FROM table_name
WHERE condition;
```

### Like

The `LIKE` operator is used in a `WHERE` clause to search for a specified pattern in a column. There are two wildcards often used in conjunction with the LIKE operator:

- `%`: The percent sign represents zero, one, or multiple characters
- `_`: The underscore represents a single character

```sql
SELECT column1, column2, ...
FROM table_name
WHERE columnN LIKE pattern; 
```

### In

```sql
SELECT column_name(s)
FROM table_name
WHERE column_name IN (value1, value2, ...); 
```

or even

```sql
SELECT column_name(s)
FROM table_name
WHERE column_name IN (SELECT STATEMENT); 
```

### Between

```sql
SELECT column_name(s)
FROM table_name
WHERE column_name BETWEEN value1 AND value2; 
```

### Aliases

Aliases are often used to make column names more readable.

```sql
SELECT column_name AS alias_name
FROM table_name;
```

```sql
SELECT column_name(s)
FROM table_name AS alias_name;
```

### Join

| Type               | Behaviour                                                    |
| ------------------ | ------------------------------------------------------------ |
| (Inner) Join       | Returns records that have matching values in both tables.    |
| Left (Outer) Join  | Returns all records from the left table, and the matches from the other. |
| Right (Outer) Join | Returns all records from the right table, and the matches from the other. |
| Full (Outer) Join  | Returns all records when there is a match in either table.   |

```sql
-- `JOIN` can be replaced with `LFET JOIN`, `RIGHT JOIN` or `FULL JOIN`.
SELECT column_name(s)
FROM table1
JOIN table2
ON table1.column_name = table2.column_name
WHERE condition;
```

A self JOIN is a regular join, but the table is joined with itself.

```sql
SELECT column_name(s)
FROM table1 T1, table1 T2
WHERE condition;
```

### Union

```sql
SELECT column_name(s) FROM table1
UNION
SELECT column_name(s) FROM table2; 
```

To allow  duplicate values, use `UNION ALL`.

### Group By

The `GROUP BY` statement groups rows that have the same values into summary  rows.

```sql
SELECT column_name(s)
FROM table_name
WHERE condition
GROUP BY column_name(s)
ORDER BY column_name(s);
```

### Having

The `HAVING` clause was added to SQL because the `WHERE` keyword could not be used with aggregate functions.

```sql
SELECT column_name(s)
FROM table_name
WHERE condition
GROUP BY column_name(s)
HAVING condition
ORDER BY column_name(s);
```

### Exists

The `EXISTS` operator is used to test for the existence of any record in a  subquery.

```sql
SELECT column_name(s)
FROM table_name
WHERE EXISTS
(SELECT column_name FROM table_name WHERE condition); 
```

### Any / All

The `ANY` and `ALL` operators are used with a WHERE or HAVING clause.

```sql
SELECT column_name(s)
FROM table_name
WHERE column_name operator ANY|ALL
(SELECT column_name FROM table_name WHERE condition); 
```

### Insert Into Select / Select Into

```sql
INSERT INTO table2
SELECT * FROM table1
WHERE condition;

-- U can also...
SELECT *
INTO newtable [IN externaldb]
FROM oldtable
WHERE condition; 
```

### Case

The `CASE` statement goes through conditions and returns a value when the first condition is  met (like an `IF-THEN-ELSE`statement). If there is no ELSE part and no conditions are true, it returns `NULL`.

```sql
SELECT
CASE
    WHEN condition1 THEN result1
    WHEN condition2 THEN result2
    WHEN conditionN THEN resultN
    ELSE result
END AS F
FROM T;
```

### IfNull

The MySQL `IFNULL()` function lets you  return an alternative value if an expression is NULL.

```mysql
SELECT ProductName, UnitPrice * (UnitsInStock + IFNULL(UnitsOnOrder, 0))
FROM Products;
```

## Database Managing

### Create / Drop Database

```sql
CREATE DATABASE databasename;
DROP DATABASE databasename;
```

### Create / Drop Table

```sql
CREATE TABLE table_name (
    column1 datatype,
    column2 datatype,
    column3 datatype,
    ....
);

DROP TABLE table_name;
```

### Alter Table

```mysql
ALTER TABLE table_name
ADD column_name datatype;

ALTER TABLE table_name
DROP COLUMN column_name;

ALTER TABLE table_name
MODIFY COLUMN column_name datatype;
```

## References

- [SQL Tutorial](https://www.w3schools.com/sql/default.asp)