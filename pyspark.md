### Data frame

- Dataframe Methods

```python
class pyspark.sql.DataFrame(jdf, sql_ctx)
agg(*exprs)
alias(alias)
approxQuantile(col, probabilities, relativeError)
cache()
checkpoint(eager=True)
coalesce(numPartitions)
colRegex(colName)
collect()
corr(col1, col2, method=None)
count()
cov(col1, col2)
createGlobalTempView(name)
createOrReplaceGlobalTempView(name)
createOrReplaceTempView(name)
createTempView(name)
crossJoin(other)
crosstab(col1, col2)
cube(*cols)
describe(*cols)
distinct()
drop(*cols)
dropDuplicates(subset=None)
dropna(how='any', thresh=None, subset=None)
explain(extended=False)
fillna(value, subset=None)
filter(condition)
first()
foreach(f)
foreachPartition(f)
freqItems(cols, support=None)
groupBy(*cols)
head(n=None)
hint(name, *parameters)
intersect(other)
isLocal()
join(other, on=None, how=None)
limit(num)
localCheckpoint(eager=True)
persist(storageLevel=StorageLevel(True, True, False, False, 1))
printSchema()
randomSplit(weights, seed=None)
registerTempTable(name)
repartition(numPartitions, *cols)
replace(to_replace, value=<no value>, subset=None)
rollup(*cols)
sample(withReplacement=None, fraction=None, seed=None)
sampleBy(col, fractions, seed=None)
select(*cols)
selectExpr(*expr)
show(n=20, truncate=True, vertical=False)
sort(*cols, **kwargs)
sortWithinPartitions(*cols, **kwargs)
subtract(other)
summary(*statistics)
take(num)
toDF(*cols)
toJSON(use_unicode=True)
toLocalIterator()
toPandas()
union(other)
unionAll(other)
unionByName(other)
unpersist(blocking=False)
withColumn(colName, col)
withColumnRenamed(existing, new)
withWatermark(eventTime, delayThreshold)

```

- functions

  ``` python
  # pyspark.sql.functions module
  pyspark.sql.functions.abs(col)
  pyspark.sql.functions.acos(col)
  pyspark.sql.functions.add_months(start, months)
  pyspark.sql.functions.approxCountDistinct(col, rsd=None)
  pyspark.sql.functions.approx_count_distinct(col, rsd=None)
  pyspark.sql.functions.array(*cols)
  pyspark.sql.functions.array_contains(col, value)
  pyspark.sql.functions.asc(col)
  pyspark.sql.functions.ascii(col)
  pyspark.sql.functions.asin(col)
  pyspark.sql.functions.atan(col)
  pyspark.sql.functions.atan2(col1, col2)
  pyspark.sql.functions.avg(col)
  pyspark.sql.functions.base64(col)
  pyspark.sql.functions.bin(col)
  pyspark.sql.functions.bitwiseNOT(col)
  pyspark.sql.functions.broadcast(df)
  pyspark.sql.functions.bround(col, scale=0)
  pyspark.sql.functions.cbrt(col)
  pyspark.sql.functions.ceil(col)
  pyspark.sql.functions.coalesce(*cols)
  pyspark.sql.functions.col(col)
  pyspark.sql.functions.collect_list(col)
  pyspark.sql.functions.collect_set(col)
  pyspark.sql.functions.column(col)
  pyspark.sql.functions.concat(*cols)
  pyspark.sql.functions.concat_ws(sep, *cols)
  pyspark.sql.functions.conv(col, fromBase, toBase)
  pyspark.sql.functions.corr(col1, col2)
  pyspark.sql.functions.cos(col)
  pyspark.sql.functions.cosh(col)
  pyspark.sql.functions.count(col)
  pyspark.sql.functions.countDistinct(col, *cols)
  pyspark.sql.functions.covar_pop(col1, col2)
  pyspark.sql.functions.covar_samp(col1, col2)
  pyspark.sql.functions.crc32(col)
  pyspark.sql.functions.create_map(*cols)
  pyspark.sql.functions.cume_dist()
  pyspark.sql.functions.current_date()
  pyspark.sql.functions.current_timestamp()
  pyspark.sql.functions.date_add(start, days)
  pyspark.sql.functions.date_format(date, format)
  pyspark.sql.functions.date_sub(start, days)
  pyspark.sql.functions.date_trunc(format, timestamp)
  pyspark.sql.functions.datediff(end, start)
  pyspark.sql.functions.dayofmonth(col)
  pyspark.sql.functions.dayofweek(col)
  pyspark.sql.functions.dayofyear(col)
  pyspark.sql.functions.decode(col, charset)
  pyspark.sql.functions.degrees(col)
  pyspark.sql.functions.dense_rank()
  pyspark.sql.functions.desc(col)
  pyspark.sql.functions.encode(col, charset)
  pyspark.sql.functions.exp(col)
  pyspark.sql.functions.explode(col)
  pyspark.sql.functions.explode_outer(col)
  pyspark.sql.functions.expm1(col)
  pyspark.sql.functions.expr(str)
  pyspark.sql.functions.factorial(col)
  pyspark.sql.functions.first(col, ignorenulls=False)
  pyspark.sql.functions.floor(col)
  pyspark.sql.functions.format_number(col, d)
  pyspark.sql.functions.format_string(format, *cols)
  pyspark.sql.functions.from_json(col, schema, options={})
  pyspark.sql.functions.from_unixtime(timestamp, format='yyyy-MM-dd HH:mm:ss')
  pyspark.sql.functions.from_utc_timestamp(timestamp, tz)
  pyspark.sql.functions.get_json_object(col, path)
  pyspark.sql.functions.greatest(*cols)
  pyspark.sql.functions.grouping(col)
  pyspark.sql.functions.grouping_id(*cols)
  pyspark.sql.functions.hash(*cols)
  pyspark.sql.functions.hex(col)
  pyspark.sql.functions.hour(col)
  pyspark.sql.functions.hypot(col1, col2)
  pyspark.sql.functions.initcap(col)
  pyspark.sql.functions.input_file_name()
  pyspark.sql.functions.instr(str, substr)
  pyspark.sql.functions.isnan(col)
  pyspark.sql.functions.isnull(col)
  pyspark.sql.functions.json_tuple(col, *fields)
  pyspark.sql.functions.kurtosis(col)
  pyspark.sql.functions.lag(col, count=1, default=None)
  pyspark.sql.functions.last(col, ignorenulls=False)
  pyspark.sql.functions.last_day(date)
  pyspark.sql.functions.lead(col, count=1, default=None)
  pyspark.sql.functions.least(*cols)
  pyspark.sql.functions.length(col)
  pyspark.sql.functions.levenshtein(left, right)
  pyspark.sql.functions.lit(col)
  pyspark.sql.functions.locate(substr, str, pos=1)
  pyspark.sql.functions.log(arg1, arg2=None)
  pyspark.sql.functions.log10(col)
  pyspark.sql.functions.log1p(col)
  pyspark.sql.functions.log2(col)
  pyspark.sql.functions.lower(col)
  pyspark.sql.functions.lpad(col, len, pad)
  pyspark.sql.functions.ltrim(col)
  pyspark.sql.functions.map_keys(col)
  pyspark.sql.functions.map_values(col)
  pyspark.sql.functions.max(col)
  pyspark.sql.functions.md5(col)
  pyspark.sql.functions.mean(col)
  pyspark.sql.functions.min(col)
  pyspark.sql.functions.minute(col)
  pyspark.sql.functions.monotonically_increasing_id()
  pyspark.sql.functions.month(col)
  pyspark.sql.functions.months_between(date1, date2)
  pyspark.sql.functions.nanvl(col1, col2)
  pyspark.sql.functions.next_day(date, dayOfWeek)
  pyspark.sql.functions.ntile(n)
  pyspark.sql.functions.pandas_udf(f=None, returnType=None, functionType=None)
  pyspark.sql.functions.percent_rank()
  pyspark.sql.functions.posexplode(col)
  pyspark.sql.functions.posexplode_outer(col)
  pyspark.sql.functions.pow(col1, col2)
  pyspark.sql.functions.quarter(col)
  pyspark.sql.functions.radians(col)
  pyspark.sql.functions.rand(seed=None)
  pyspark.sql.functions.randn(seed=None)
  pyspark.sql.functions.rank()
  pyspark.sql.functions.regexp_extract(str, pattern, idx)
  pyspark.sql.functions.regexp_replace(str, pattern, replacement)
  pyspark.sql.functions.repeat(col, n)
  pyspark.sql.functions.reverse(col)
  pyspark.sql.functions.rint(col)
  pyspark.sql.functions.round(col, scale=0)
  pyspark.sql.functions.row_number()
  pyspark.sql.functions.rpad(col, len, pad)
  pyspark.sql.functions.rtrim(col)
  pyspark.sql.functions.second(col)
  pyspark.sql.functions.sha1(col)
  pyspark.sql.functions.sha2(col, numBits)
  pyspark.sql.functions.shiftLeft(col, numBits)
  pyspark.sql.functions.shiftRight(col, numBits)
  pyspark.sql.functions.shiftRightUnsigned(col, numBits)
  pyspark.sql.functions.signum(col)
  pyspark.sql.functions.sin(col)
  pyspark.sql.functions.sinh(col)
  pyspark.sql.functions.size(col)
  pyspark.sql.functions.skewness(col)
  pyspark.sql.functions.sort_array(col, asc=True)
  pyspark.sql.functions.soundex(col)
  pyspark.sql.functions.spark_partition_id()
  pyspark.sql.functions.split(str, pattern)
  pyspark.sql.functions.sqrt(col)
  pyspark.sql.functions.stddev(col)
  pyspark.sql.functions.stddev_pop(col)
  pyspark.sql.functions.stddev_samp(col)
  pyspark.sql.functions.struct(*cols)
  pyspark.sql.functions.substring(str, pos, len)
  pyspark.sql.functions.substring_index(str, delim, count)
  pyspark.sql.functions.sum(col)
  pyspark.sql.functions.sumDistinct(col)
  pyspark.sql.functions.tan(col)
  pyspark.sql.functions.tanh(col)
  pyspark.sql.functions.toDegrees(col)
  pyspark.sql.functions.toRadians(col)
  pyspark.sql.functions.to_date(col, format=None)
  pyspark.sql.functions.to_json(col, options={})
  pyspark.sql.functions.to_timestamp(col, format=None)
  pyspark.sql.functions.to_utc_timestamp(timestamp, tz)
  pyspark.sql.functions.translate(srcCol, matching, replace)
  pyspark.sql.functions.trim(col)
  pyspark.sql.functions.trunc(date, format)
  pyspark.sql.functions.udf(f=None, returnType=StringType)
  pyspark.sql.functions.unbase64(col)
  pyspark.sql.functions.unhex(col)
  pyspark.sql.functions.unix_timestamp(timestamp=None, format='yyyy-MM-dd HH:mm:ss')
  pyspark.sql.functions.upper(col)
  pyspark.sql.functions.var_pop(col)
  pyspark.sql.functions.var_samp(col)
  pyspark.sql.functions.variance(col)
  pyspark.sql.functions.weekofyear(col)
  pyspark.sql.functions.when(condition, value)
  pyspark.sql.functions.window(timeColumn, windowDuration, slideDuration=None, startTime=None)
  pyspark.sql.functions.year(col)
  ```

- Column methods

  ``` python
  class pyspark.sql.Column(jc)
  # 1. Select out of a data frame
  df.colName
  df["colName"]
  
  # 2. Create from an expression
  df.colName + 1
  1 / df.colName
  
  alias(*alias, **kwargs)
  asc()
  astype(dataType)
  between(lowerBound, upperBound)
  bitwiseAND(other)
  bitwiseOR(other)
  bitwiseXOR(other)
  cast(dataType)
  contains(other)
  desc()
  endswith(other)
  eqNullSafe(other)
  getField(name)
  getItem(key)
  isNotNull()
  isNull()
  isin(*cols)
  like(other)
  name(*alias, **kwargs)
  otherwise(value)
  over(window)
  rlike(other)
  startswith(other)
  substr(startPos, length)
  when(condition, value)
  ```



  - Row

    ``` python
    class pyspark.sql.Row
    # A row in DataFrame. The fields in it can be accessed:
    #  - like attributes (row.key)
    #  - like dictionary values (row[key])
    # key in row will search through row keys.
    
    # Row can be used to create a row object by using named arguments, the fields will be sorted by names. It is not allowed to omit a named argument to represent the value is None or missing. This should be explicitly set to None in this case.
    asDict(recursive=False)
    # Row(name="Alice", age=11).asDict() == {'name': 'Alice', 'age': 11}
    
    ```


  - DataFrameNaFunctions

    ``` python
    class pyspark.sql.DataFrameNaFunctions(df)
    # Functionality for working with missing data in DataFrame
    drop(how='any', thresh=None, subset=None)
    # Replace null values, alias for na.fill(). DataFrame.fillna() and DataFrameNaFunctions.fill() are aliases of each other
    fill(value, subset=None)
    # Returns a new DataFrame replacing a value with another value. DataFrame.replace() and DataFrameNaFunctions.replace() are aliases of each other.
    replace(to_replace, value=<no value>, subset=None)
    ```

  - DataFrameStatFunctions

    ``` python
    class pyspark.sql.DataFrameStatFunctions(df) 
    ```

  - Window

    ``` python
    # Utility functions for defining window in DataFrames
    class pyspark.sql.Window[source]
    window = Window.orderBy("date").rowsBetween(Window.unboundedPreceding, Window.currentRow)
    static orderBy(*cols)
    static partitionBy(*cols)
    static rangeBetween(start, end)
    static rowsBetween(start, end)
    
    ```

  - WindowSpec

    ``` python
    # A window specification that defines the partitioning, ordering, and frame boundaries. Use the static methods in Window to create a WindowSpec.
    class pyspark.sql.WindowSpec(jspec)
    orderBy(*cols)
    partitionBy(*cols)
    rangeBetween(start, end)
    rowsBetween(start, end)
    ```

  - Catalog

    ``` python
    class pyspark.sql.Catalog(sparkSession)
    # User-facing catalog API, accessible through SparkSession.catalog.
    # This is a thin wrapper around its Scala implementation org.apache.spark.sql.catalog.Catalog
    cacheTable(tableName)
    clearCache()
    createExternalTable(tableName, path=None, source=None, schema=None, **options)
    createTable(tableName, path=None, source=None, schema=None, **options)
    currentDatabase()
    dropGlobalTempView(viewName)
    dropTempView(viewName)
    isCached(tableName)
    listColumns(tableName, dbName=None)
    listDatabases()
    listFunctions(dbName=None)
    listTables(dbName=None)
    recoverPartitions(tableName)
    refreshByPath(path)
    refreshTable(tableName)
    registerFunction(name, f, returnType=None)
    setCurrentDatabase(dbName)
    uncacheTable(tableName)
    
    ```




