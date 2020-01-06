import pytest
from pyspark.sql import SparkSession
# from pyspark import SparkConf, SparkContext


@pytest.fixture(scope="session",
                params=[pytest.mark.spark_local('local'),
                        pytest.mark.spark_yarn('yarn')])
def spark_session(request):
    """
    Session Fixture to create spark context
    :param request:
    :return:
    """
    if request.param == 'local':
        spark = (SparkSession()
                .setMaster("local[2]")
                .setAppName("pytest-pyspark-local-testing")
                .enableHiveSupport()
                )
    elif request.param == 'yarn':
        spark = (SparkSession()
                .setMaster("yarn-client")
                .setAppName("pytest-pyspark-yarn-testing")
                .set("spark.executor.memory", "1g")
                .set("spark.executor.instances", 2)
                .enableHiveSupport()
                )
    request.addfinalizer(lambda: spark.stop())

    # spark = SparkSession(conf=conf)
    return spark


def my_test_that_requires_sc(spark_session):
    assert spark_session.textFile('/path/to/a/file').count() == 10
