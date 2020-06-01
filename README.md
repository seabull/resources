# Some useful URLs



### Big Data

- [Reading List](https://www.mapflat.com/lands/resources/reading-list/)

### CI/CD

- [git-hooks-continuous-integration](https://www.atlassian.com/continuous-delivery/git-hooks-continuous-integration)
- [Code is Law in Chinese](https://mp.weixin.qq.com/s/a-tUQSy5zT3qhd8mBy2HfA)
- [CI friendly git repos](https://www.atlassian.com/continuous-delivery/ci-friendly-git-repos)

### Git/Github

- [pre-commit](https://pre-commit.com)

  - installation

    ```
    pip install pre-commit
    brew install pre-commit
    ```

  - Add pre-commit plugins to project

    - add .pre-commit-config.yaml to root directory of the project
    - Example:

    ``` repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v1.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-symlinks
      - id: mixed-line-ending
      - id: trailing-whitespace
    - repo: git@github.com:Yelp/detect-secrets
    rev: 0.9.1
    hooks:
      - id: detect-secrets
    args: ['--baseline', '.secrets.baseline']
    exclude: ./temp/.
    
    ```

  - Updating hooks automatically

    - Run ```pre-commit autoupdate```
    - 

- [git tips](https://github.com/git-tips/tips)

  - Remove sensitive data from history after a push

    ```git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch <path-to-your-file>' --prune-empty --tag-name-filter cat -- --all && git push origin --force --all```

- [git beyond the basics](https://www.perforce.com/blog/git-beyond-basics-using-shallow-clones)

- [git flow cheatsheet](https://danielkummer.github.io/git-flow-cheatsheet/)

### Docker

- [Find child docker images](https://stackoverflow.com/questions/36584122/how-to-get-the-list-of-dependent-child-images-in-docker)

### GoLang

- [Concurrency Best Practices](https://github.com/codeship/go-best-practices/tree/master/concurrency)
  - Ensure consumers can only consume. `recvOnly <-chan Thing` are your friends.
  - Track completion of goroutines. `sync.WaitGroup` is your friend.
  - Close only when producing routines can be verified as no longer able to send on the channel being closed.
- [GO in production](https://peter.bourgon.org/go-in-production/)
- [7 common mistakes in Go](https://www.youtube.com/watch?v=29LLRKIL_TI)
- [5 useful ways to use Closure](https://www.calhoun.io/5-useful-ways-to-use-closures-in-go/)
- [Retry example](http://github.com/matryer/try)
  - [Idiomatic Go Tricks](https://www.youtube.com/watch?v=yeetIgNeIkc)
- [Code Review Comment](https://github.com/golang/go/wiki/CodeReviewComments)
- [Awesome Go](https://awesome-go.com)
- [Dependecny Management](https://blog.spiralscout.com/golang-vgo-dependency-management-explained-419d143204e4)
- [Error Handling](<https://banzaicloud.com/blog/error-handling-go/>)
- [go mod just tell me how to use](https://www.kablamo.com.au/blog-1/2018/12/10/just-tell-me-how-to-use-go-modules)
- [gRPC and REST tutorial](https://medium.com/@amsokol.com/tutorial-how-to-develop-go-grpc-microservice-with-http-rest-endpoint-middleware-kubernetes-af1fff81aeb2)
- [gRPC eco-system](https://github.com/grpc-ecosystem)
- [Go High Performance](https://dave.cheney.net/high-performance-go-workshop/dotgo-paris.html)
- [Sourced](https://github.com/src-d)
  - [src-d engine](https://github.com/src-d/engine)
  - [lookout](https://github.com/src-d/lookout)
  - [BubbleFish](dashboard.bblf.sh)
- Useful packages
  - [envconfig](https://github.com/kelseyhightower/envconfig)

### Kotlin

- [Kotlin Idioms](https://kotlinlang.org/docs/reference/idioms.html)
- [Spark+Kotlin](https://thegmariottiblog.blogspot.com/2017/05/lets-make-apache-spark-more-kotlinesque.html)

### Python

- [Tiny Python Notebook](https://github.com/mattharrison/Tiny-Python-3.6-Notebook)

- [pytest folder structure](https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure)

- [Python Tutor visualize](http://pythontutor.com/visualize.html#mode=edit)

- [pytest monkeypatching](https://www.patricksoftwareblog.com/monkeypatching-with-pytest/)

- [Python run-time method patching](https://tryolabs.com/blog/2013/07/05/run-time-method-patching-python/)

- [Python and postgres](https://hakibenita.com/fast-load-data-python-postgresql)

- [Python String Formatting best practices](https://realpython.com/python-string-formatting)

- [Some Useful Packages]

  - [Retry package](https://github.com/jd/tenacity)
  - [Data Validation library](https://github.com/alecthomas/voluptuous)
  - [Pattern Matching](https://github.com/santinic/pampy)

- [virtualenv and git best practices](http://libzx.so/main/learning/2016/03/13/best-practice-for-virtualenv-and-git-repos.html)

  - python virtualenv do NOT need to be in the same directory as the python sources, i.e. we could put all venvs in ~/.envs (e.g. ~/.envs/myenv1  ~/.envs/my-test-env1), then run "source ~/.envs/myenv1/bin/activate" 

- [python property decorator](https://stackoverflow.com/a/17330273/8593536)

- [python anti-patterns](https://docs.quantifiedcode.com/python-anti-patterns/correctness/implementing_java-style_getters_and_setters.html?highlight=getter)

- pip SSL config

  - ``` bash
    #!/usr/bin/env bash
    
    MY_ID=$(whoami)
    HOME_DIR=$(cd ~ && pwd)
    
    TIMEOUT=60
    ```

  - [Packaging](http://alexanderwaldin.github.io/packaging-python-project.html)

  - [PEP440 versions](https://medium.com/@vladyslav.krylasov/implement-versioning-of-python-projects-according-to-pep-440-af952199eb30)
  
  - [python load into posgresql](https://hakibenita.com/fast-load-data-python-postgresql)

### Functional Programming

- [Functional Thinking by Neal Ford](http://nealford.com/functionalthinking.html)

### Tmux

- [tmux and screen cheatsheet](http://www.dayid.org/comp/tm.html)
- [tmux configuration](https://www.hamvocke.com/blog/a-guide-to-customizing-your-tmux-conf/)
- [cheat sheet](https://gist.github.com/henrik/1967800)

### Spark

- [spark internal docs](https://github.com/JerryLead/SparkInternals/tree/master/markdown)

- [data frame partitioning](https://stackoverflow.com/questions/30995699/how-to-define-partitioning-of-dataframe)

- [pyspark production best practices](https://developerzen.com/best-practices-writing-production-grade-pyspark-jobs-cb688ac4d20f)

- [advanced spark training by sameer](https://youtu.be/7ooZ4S7Ay6Y)

- [spark tuning tips](https://spark.apache.org/docs/latest/tuning.html)

  - [custom listener](https://db-blog.web.cern.ch/blog/luca-canali/2017-03-measuring-apache-spark-workload-metrics-performance-troubleshooting)

  - [Spark Perf Tuning Checklist](https://zerogravitylabs.ca/spark-performance-tuning-checklist/)
  
  - [Spark Linstener](https://dzone.com/articles/using-spark-listeners)
  
    - [Some examples](https://gist.github.com/hadoopsters)
  
  - [configuration properties](https://spark.apache.org/docs/latest/configuration.html)
  
  - ``` bash
    spark-submit --master yarn --deploy-mode cluster 
    --executor-cores 3 
    --executor-memory 1g 
    --conf "spark.executor.extraJavaOptions=-Dhttps.proxyHost=${PROXY_HOST} 
    -Dhttps.proxyPort=${PROXY_PORT}" 
    --conf spark.dynamicAllocation.enabled=false 
    --num-executors 36 
    --conf spark.driver.cores=1
    --conf spark.streaming.receiver.maxRate=150 
    --conf spark.rpc.netty.dispatcher.numThreads=2 
    --conf spark.ui.retainedJobs=100 
    --conf spark.ui.retainedStages=100 
    --conf spark.ui.retainedTasks=100 
    --conf spark.worker.ui.retainedExecutors=100 
    --conf spark.worker.ui.retainedDrivers=100 
    --conf spark.sql.ui.retainedExecutions=100 
    --conf spark.streaming.ui.retainedBatches=10000 
    --conf spark.ui.retainedDeadExecutors=100 
    --conf spark.rpc.netty.dispatcher.numThreads=2 
    --conf spark.eventLog.enabled=false 
  --conf spark.history.retainedApplications=2 
    --conf spark.history.fs.cleaner.enabled=true 
    --conf spark.history.fs.cleaner.maxAge=2d 
    --class "$APPCLASS" "$APPFILE" >> "/var/log/${APPCLASS}.log" 2>&1
  --conf  spark.extraListeners=org.apache.spark.scheduler.StatsReportListener
    ```
  
  - some config
  
  - ``` python
    spark=SparkSession.builder.master('yarn').appName('tga-dfa-adhoc')\
        .enableHiveSupport()\
        .config("hive.exec.dynamic.partition","true")\
        .config("hive.exec.dynamic.partition.mode", "nonstrict")\
        .config("spark.sql.cbo.enabled", "true")\
        .config("spark.rpc.netty.dispatcher.numThreads", "2")\
        .config("spark.serializer","org.apache.spark.serializer.KryoSerializer")\
        .config("spark.default.parallelism","10000")\
        .config("spark.driver.maxResultSize","10G")\
        .config("spark.rdd.compress", "true")\
        .config("spark.sql.inMemoryColumnarStorage.compressed", "true")\
        .config("spark.io.compression.codec", "snappy")\
        .config("spark.executor.memory", '20g')\
        .config("spark.executor.memoryOverhead", "10g")\
        .config("spark.sql.hive.thriftServer.singleSession", "true")\
      .getOrCreate()
    ```
  
  - ``` python
    # useful to debug and find the source file name
    df = df.withColumn("fname", input_file_name())
    ```


  ```bash
  The following configuration settings are set by default in the bigRED environment and *should not* be modified:
  
  spark.authenticate = true (turns on authentication between Spark components)
  spark.master = yarn (Configures spark to use YARN as the execution engine)
  spark.executorEnv.LD_LIBARARY_PATH (varies depending on version / environment)
  spark.yarn.appMasterEnv.SPARK_HOME (varies depending on version / environment) [Spark 2.0 only]
  spark.yarn.archive (varies depending on version / environment)
  spark.driver.extraJavaOptions (varies depending on version)
  spark.yarn.am.extraJavaOptions (varies depending on version)
  spark.eventLog.enabled = true (turns on Spark event logging)
  spark.eventLog.dir (varies depending on version / environment)
  spark.yarn.historyServer.address (varies depending on version / environment)
  spark.shuffle.service.enabled = true (enables Spark external shuffle service)
  
  The following configuration settings are set by default in the bigRED environment. They should work for many (if not most) tasks, especially shell jobs, but may be customized as necessary:
  
  spark.yarn.am.waitTime = 180000000 (sets the time to wait for an ApplicationMaster to be allocated before giving up -- 3 minutes)
  spark.network.timeout = 300s (sets the time before network transfers should be considered failed -- 5 minutes)
  spark.speculation = true (enables speculative execution of Spark tasks)
  spark.dynamicAllocation.enabled = true (enables dynamic allocation of Spark executors)
  spark.dynamicAllocation.minExecutors = 1 (sets the minimum number of executors to allocate -- please do NOT change for shell jobs)
  spark.dynamicAllocation.maxExecutors = 100 (sets the maximum number of executors to allocate)
  spark.dynamicAllocation.executorIdleTimeout = 300s (sets the amount of time before idle executors are terminated -- please do NOT change for shell jobs)
  spark.executor.instances = 1 (sets the default # of Spark executors -- for dynamic allocation, use spark.dynamicAllocation.minExecutors, spark.dynamicAllocation.initialExecutors and spark.dynamicAllocation.maxExecutors instead)
  spark.driver.memory = 1g (sets the amount of RAM to allocate for Driver instances)
  spark.executor.memory = 4g (sets the amount of RAM to allocate for Executor instances)
  spark.r.command = /usr/local/R-xyz-201701/bin/Rscript (sets the R command used to execute SparkR scripts)
  spark.r.shell.command = /usr/local/R-xyz-201701/bin/R (sets the R command used to execute SparkR shells) [Spark >= 2.1 only]
  spark.pyspark.python = /usr/local/python-xyz-201701/bin/python2.7 (sets the python executable to use by default for pyspark) [Spark >= 2.1 only]
  spark.yarn.appMasterEnv.PYSPARK_PYTHON = /usr/local/python-xyz-201701/bin/python2.7 (sets the python executable to use by default for pyspark on YARN AM) [Spark <= 2.0 only]
  spark.port.maxRetries = 64
  ```

  

  - [Spark Streaming log configuration](http://shzhangji.com/blog/2015/05/31/spark-streaming-logging-configuration/)

  - [Mastering Spark Book](https://jaceklaskowski.gitbooks.io/mastering-apache-spark/content/)

  - Some Tips

      - Spark Native ORC: Create table MyTable ... ***USING ORC*** 

      - **Nested Schema Pruning: spark.conf.set("spark.sql.optimizer.nestedSchemaPruning.enabled", true)** Prunes the nested columns (e.g. struct) if not all fields are selected. Without this config, it read **ALL** fields

      - collapse projects: use .asNondeterministic in the udf

      - Spark 3.0: Join Hints: 

          - BROADCAST (prior versions)
      - MERGE: Shuffle sort merge join
          - SHUFFLE_HASH: Shuffle hash join
      - SHUFFLE_REPLICATED_NL: Shuffle and Replicate Nested Loop join
        
    - **spark.sql.codegen**

      The default value of *spark.sql.codegen* is **false**. When the value of this is true, Spark SQL will compile each query to Java bytecode very quickly. Thus, improves the performance for large queries. But the issue with codegen is that it slows down with very short queries. This happens because it has to run a compiler for each query.

    - **spark.sql.inMemorycolumnarStorage.compressed**

      The default value of *spark.sql.inMemorycolumnarStorage.compressed* is **true**. When the value is true we can compress the in-memory columnar storage automatically based on statistics of the data.

    - **spark.sql.inMemoryColumnarStorage.batchSize**

      The default value of *spark.sql.inMemoryColumnarStorage.batchSize* is **10000**. It is the batch size for columnar caching. The larger values can boost up memory utilization but causes an out-of-memory problem.

    - **spark.sql.parquet.compression.codec**

      The *spark.sql.parquet.compression.codec* uses default snappy compression. Snappy is a library which for compression/decompression. It mainly aims at very high speed and reasonable compression. In most compression, the resultant file is 20 to 100% bigger than other inputs although it is the order of magnitude faster. Other possible option includes uncompressed, gzip and lzo.

  - [productionize spark ETL video](https://databricks.com/session/keeping-spark-on-track-productionizing-spark-for-etl)

  - [Spark Metrics](http://www.hammerlab.org/2015/02/27/monitoring-spark-with-graphite-and-grafana/)

  - [Spark Shuffling](https://medium.com/swlh/revealing-apache-spark-shuffling-magic-b2c304306142)

## Security

- Kerberos

  - keytab file

  - ```
    Typing passwords is annoying, especially when you are forced to change
    them arbitrarily. Here's what I did on bigred:
    
    Set up passwordless ssh:
    
    	cat ~/.ssh/id_rsa.pub | ssh <user>@domain.XYZ.com "cat >>
    ~/.ssh/authorized_keys"
    
    On host, create a local keytab file for your principal:
    
    	$ ktutil
    	ktutil: addent -password -p <USER>@DOMAIN.XYZ.COM -k 1 -e
    aes256-cts-hmac-sha1-96
    	ktutil: wkt .keytab
    	ktutil: q
    
    In ~/.profile:
    
    	if [ -f $HOME/.keytab ]; then
    		kinit -kt $HOME/.keytab <USER>@XYZ.COM
    	fi
    
    Now forget your password and go on with your life.
    
    $ generate-keytab .keytab <USER>@XYZ.COM
    Kerberos password for <USER>@XYZ.COM: ********
    ```

  - ssh keys

    ``` bash
    ssh-keygen -t rsa -C "your_email@example.com"
    ```

  - ssh config

    ``` bash
    cat ~/.ssh/config                                                                                                       HashKnownHosts yes
    ServerAliveInterval 120
    TCPKeepAlive yes
    
    Host gitlab.com
      Hostname altssh.gitlab.com
      User git
      Port 443
      PreferredAuthentications publickey
      IdentityFile ~/.ssh/gitlab
    
    Host *
      UseKeychain yes
    ```

    

### Java

- [String and StringBuffer concat out of memory](https://www.captaincasademo.com/forum/posts/list/1503.page)
- [Java Memory Model and Garbage Collection](https://dzone.com/articles/understanding-the-java-memory-model-and-the-garbag)

### Scala

- [Scala Implicit design pattern](http://www.lihaoyi.com/post/ImplicitDesignPatternsinScala.html)
- 

### Architecture

- [Architectyure ketas](http://nealford.com/katas/list.html)
- [Document Architectual Decisions](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions)
- [Lightweight Arch Decision Records](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
- [Thinking Architecturally](https://content.pivotal.io/ebooks/thinking-architecturally)
- [Should that be a microservice](https://content.pivotal.io/blog/should-that-be-a-microservice-keep-these-six-factors-in-mind)

### Misc Tools

- [Cookiecutter template](https://github.com/audreyr/cookiecutter)

- [Terminal Setup](https://medium.freecodecamp.org/how-you-can-style-your-terminal-like-medium-freecodecamp-or-any-way-you-want-f499234d48bc)
  - [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts#font-installation)
  - [Powerlevel9k font](https://github.com/bhilburn/powerlevel9k/wiki/Install-Instructions#step-1-install-powerlevel9k)

- VS Code Extensions
  - [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
  - Golang
  - Dash
  - Docker

- [Architecture Resources](https://developertoarchitect.com)

- [Code City](https://wettel.github.io/codecity-download.html)

- [cgroup video](https://youtu.be/sK5i-N34im8)

- productivity tools

  - asciinema
  - exa (dir/ls tool)

- Notes and tips

  - Hive CLI in Oozie actions

  - ```bash
    SET mapreduce.job.credentials.binary=${HADOOP_TOKEN_FILE_LOCATION}
    --hiveconf hive.execution.engine=mr
    ```

- [Shellcheck](https://github.com/koalaman/shellcheck)

- Terminal tools

  - [bench](https://darrenburns.net/posts/tools/)
  - [Tools collection](https://onethingwell.org)
  - [The Art of command Line](https://github.com/jlevy/the-art-of-command-line)

- Apache Beam

  - [Data processing job using BEAM](https://www.talend.com/blog/2018/04/23/how-to-develop-a-data-processing-job-using-apache-beam-2/)  [Part2](https://www.talend.com/blog/2018/08/07/developing-data-processing-job-using-apache-beam-streaming-pipeline/)

  - 

    
