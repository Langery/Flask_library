## MySQL

1. 删除一条数据
``` sql
  DELETE FROM tablename WHERE NAME = 'abc'
```
2. 查询
``` sql
  SELECT columnname FROM tablename
  -- 通过 username 找 id
  SELECT id FROM tablename WHERE username = 'xxx'
  -- 查询一段时间的内容
  SELECT * FROM tablename WHERE startNum < columnname < endNum
```
3. 添加
``` sql
  INSERT INTO tablename VALUES (value)
  INSERT INTO tablename (columnname...) VALUES (value...)
```
4. 修改
```sql
  UPDATE tablename SET columnname = 'newValue' WHERE columnvalue = 'xxx'
```
