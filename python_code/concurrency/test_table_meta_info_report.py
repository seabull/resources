import pytest
import table_meta_info_report
from asyncio_command.command import run_asyncio_commands, run_command_shell, make_chunks
# import re
import types
import re


@pytest.fixture(scope="session")
def webhook():
    """
    Read webhook text from file webhook.txt
    """
    with open("webhook.txt", "r") as f:
        webhook = f.readline().strip()
    return webhook


# def test_get_table_location():
#     table_meta_info_report.get_table_location(("prd_roundel_fnd.guest_behavior"))
#     assert False


@pytest.mark.parametrize("lst, chunk_size, expected", [
    ([1, 2, 3, 4, 5, 6, 7, 8], 5, [[1, 2, 3, 4, 5], [6, 7, 8]]),
    (('a', 'b', 'c', 'd'), 2, [('a', 'b'), ('c', 'd')]),
])
def test_make_chunks(lst, chunk_size, expected):
    result = list(make_chunks(lst, chunk_size))
    assert result is not None
    assert result == expected


@pytest.mark.parametrize("command, expected", [
    ("ls table_meta_info_report.py",
     table_meta_info_report.CommandResult(cmd="ls table_meta_info_report.py",
                                          returncode=0,
                                          output="table_meta_info_report.py")),
    ("uname",
     table_meta_info_report.CommandResult(
         cmd="uname", returncode=0, output="Darwin")),
])
@pytest.mark.asyncio
async def test_run_command_shell(command: str, expected: str):
    result = await run_command_shell(command=command)
    assert result == expected


@pytest.mark.parametrize("commands, max_concurrency, expected", [
    (["ls table_meta_info_report.py"], 5, [
        table_meta_info_report.CommandResult("ls table_meta_info_report.py", 0,
                                             "table_meta_info_report.py")
    ]),
    (["uname", "ls table_meta_info_report.py"], 3, [
        table_meta_info_report.CommandResult("uname", 0, "Darwin"),
        table_meta_info_report.CommandResult("ls table_meta_info_report.py", 0,
                                             "table_meta_info_report.py")
    ]),
    ([], 2, []),
])
def test_run_asyncio_commands(commands, max_concurrency, expected):
    result = run_asyncio_commands(
        commands=commands, max_concurrent_tasks=max_concurrency)
    assert result == expected


@pytest.mark.format
def test_format_table_info(webhook):
    d = table_meta_info_report.format_table_info(
        { 'Guest_spend':
            {
            "table_name": "Guest_spend",
            "max_partition": "2019-12-02",
            "done_flag": "Not Exist",
            "update_date": "2019-12-01",
            "update_time": "10:00",
                "load_frequency": "Daily"
            }
        }
    )
    assert d == """\
\n        ```\n\
|                              Table Name|        Date|  Time|Max Partition|  Frequency|    Status|\n\
|----------------------------------------|------------|------|-------------|-----------|----------|\n\
|                             Guest_spend|  2019-12-01| 10:00|   2019-12-02|      Daily|In Progress/NA|\
```"""


# {"table_name": "",
#  "update_date": "",
#  "update_time": "",
#  "max_partition": "",
#  }


# @pytest.mark.parametrize("cmd_results, expected", [
#     ([
#         table_meta_info_report.CommandResult(
#             cmd="uname", returncode=0, output="Darwin")
#     ], []),
# ])
# def test_extract_info_from_results(cmd_results, expected):
#     result = table_meta_info_report.extract_info_from_results(
#         cmd_results=cmd_results)
#     assert result == expected
#     # assert 0, "Fail it intentionally"


@pytest.mark.skip
def test_get_all_tables():
    pass


@pytest.mark.parametrize("table_list, expected_cmds", [
    (["prd_roundel_fnd.guest_spend"
      ], ["""hive -e "show create table prd_roundel_fnd.guest_spend;" """]),
    (["prd_roundel_fnd.guest_spend", "prd_roundel_fnd.guest_behavior"], [
        """hive -e "show create table prd_roundel_fnd.guest_spend;" """,
        """hive -e "show create table prd_roundel_fnd.guest_behavior;" """,
    ]),
])
def test_get_ddl_commands(table_list, expected_cmds):
    result = table_meta_info_report.get_ddl_commands(table_list)
    assert isinstance(result, types.GeneratorType)
    assert list(result) == expected_cmds


# @pytest.mark.parametrize("cmd_results, expected_meta",
#                          [
#                              ([table_meta_info_report.CommandResult(cmd="", returncode==0, output="""
#                              """)])
#                          ])

@pytest.mark.skip
def test_get_meta_from_ddl_results():
    pass


@pytest.mark.skip
def test_get_table_location():
    pass


# @pytest.mark.parametrize("cmd_results, expected", [
#     ([table_meta_info_report.CommandResult(cmd="", returncode=0, output="""CREATE TABLE prd_roundel_fnd.guest_spend ( ) LOCATION
#     'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend'
#     """)],
#      ("prd_roundel_fnd.guest_spend", "hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend")
#     )
# ])
# def test_get_ddl_strings():
#     pass


# @pytest.mark.parametrize(
#     "ddl, pattern, expected",
#     [("""CREATE TABLE prd_roundel_fnd.guest_spend ( ) LOCATION
#     'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend'
#     TBLPROPERTIES (
#     'LOAD_FREQUENCY'='Weekly',
#     )
#     """, table_meta_info_report.DDL_META_PATTERN,
#       table_meta_info_report.TableMeta(
#           name="prd_roundel_fnd.guest_spend",
#           location=
#           "hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend",
#           load_frequency="Weekly"))])
# def test_get_meta_from_ddl(ddl, pattern, expected):
#     result = table_meta_info_report.parse_ddl(ddl=ddl, pattern=pattern)
#     print(result)
#     assert result == expected
#     # assert 0


# @pytest.mark.parametrize("tables, done_file_mapping, expected_commands", [
#     ([{
#         "table_name": "tableA",
#         "max_partition": '2019-12-02'
#     }], None, [
#         "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/12/02/tableA*"
#     ]),
#     ([{
#         "table_name": "tableA",
#         "max_partition": '2019-12-02'
#     }, {
#         "table_name": "tableB",
#         "max_partition": '2020-01-02'
#     }], None, [
#         "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/12/02/tableA*",
#         "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2020/01/02/tableB*"
#     ]),
#     ([{
#         "table_name": "table1",
#         "max_partition": '2019-12-02'
#     }, {
#         "table_name": "table2",
#         "max_partition": '2020-01-02'
#     }], {
#         "table1": "table2"
#     }, [
#         "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/12/02/table2*",
#         "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2020/01/02/table2*"
#     ]),
#     ([], None, []),
#     (
#         [table_meta_info_report.TableMeta(name="tbl1", max_partition="2019-01-10"),
#          table_meta_info_report.TableMeta(name="tbl2", max_partition="2019-01-11"),
#          table_meta_info_report.TableMeta(name="tbl3", max_partition="2019-01-12")
#          ],
#         None,
#         [
#             "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/01/10/tbl1*",
#             "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/01/11/tbl2*",
#             "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/01/12/tbl3*",
#         ]
#     )
# ])
# def test_done_commands_from_table(tables, done_file_mapping,
#                                   expected_commands):
#     commands = table_meta_info_report.done_commands_from_table(
#         table_list=tables, done_file_mapping=done_file_mapping)
#     assert commands == expected_commands


# @pytest.mark.parametrize(
#     "cmd_results, expected_flags",
#     [([table_meta_info_report.CommandResult(cmd="", returncode=0, output="")
#        ], []),
#      pytest.param(table_meta_info_report.CommandResult(
#          cmd="", returncode=0, output=""), [],
#                   marks=pytest.mark.xfail)])
# def test_extract_done_flag(cmd_results, expected_flags):
#     flags = table_meta_info_report.extract_done_flag(cmd_results)


@pytest.mark.slack
@pytest.mark.parametrize("data",
                         [
            #                  (
            # {
            # "text":
            # f"*UNIT TEST* _PLEASE IGNORE_ -- Latest table information for *Roundel*  ```formatted``` ",
            # "blocks": [
            #     {
            #         "type": "section",
            #         "text": {
            #             "type" : "mrkdwn",
            #             "text": f"Another formatted ```another```"
            #         }
            #     },
            #     {
            #         "type": "section",
            #         "text": {
            #             "type": "mrkdwn",
            #             "text": f"3rd formatted ```3rd```"
            #         }
            #     }
            #
            # ]
            # }
            #                  ),
#                              (
#                                      {
#                                          "text": f"""*UNIT TEST* ```formatted 123456789012345678901234567890123456789012345678901234567890
#
# ***Some more text
# formatted 123456789012345678901234567890123456789012345678901234567890
# ```"""
#                                      }
#                              ),
#                              (
#                                      {
#                                          "text": f"""
# ```
# Latest table information in prd_roundel_fnd
# Partition Status: Completed=Max Partition Loaded,
# In Progress/NA=Either Max Partition is being loaded or No Information Available
#
# |                              Table Name|        Date|  Time|Max Partition|  Frequency|        Status|
# |----------------------------------------|------------|------|-------------|-----------|--------------|
# |                   active_guest_exposure|  2020-02-03| 10:10|   2020-02-01|      Daily|In Progress/NA|
# |                    active_user_exposure|  2020-02-03| 10:28|   2020-02-01|      Daily|In Progress/NA|
# |         campaign_guest_line_performance|  2020-02-20| 10:27|   2020-02-18|      Daily|In Progress/NA|
# |               campaign_line_performance|  2020-02-10| 16:45|   2020-02-27|      Daily|In Progress/NA|
# |             campaign_report_performance|  2020-02-10| 17:27|   2020-02-27|      Daily|In Progress/NA|
# |      campaign_guest_line_performance_ss|  2020-02-20| 01:43|   2020-02-19|      Daily|     Completed|
# |            campaign_line_performance_ss|  2020-02-20| 02:19|   2020-02-19|      Daily|     Completed|
# |          campaign_report_performance_ss|  2020-02-20| 02:55|   2020-02-19|      Daily|     Completed|
# |                          guest_behavior|  2020-02-20| 04:59|   2020-02-19|      Daily|     Completed|
# |                   guest_features_global|  2020-02-19| 20:12|   2020-02-17|      Daily|     Completed|
# |               guest_features_item_final|  2020-02-17| 14:24|   2020-02-16|     Weekly|     Completed|
# |                             guest_spend|  2020-02-20| 10:04|   2020-02-18|      Daily|     Completed|
# |                            lift_metrics|  2020-02-16| 14:22|   2020-02-02|     Weekly|     Completed|
# |                         lift_metrics_ss|  2020-02-20| 03:17|   2020-02-19|      Daily|In Progress/NA|
# |                   sf_reporting_insights|  2020-02-20| 01:08|   2020-02-19|      Daily|     Completed|
# |          whitewalker_test_control_final|  2020-02-17| 15:19|   2020-02-16|      Daily|     Completed|
# |       whitewalker_test_control_final_ss|  2020-02-20| 03:08|   2020-02-19|      Daily|In Progress/NA|
# ---------------------------------------------------------
# ***Latest Oozie Coordinator Job information***
# |                        Job Name|     status|          Start Time|  Duration|      Scheduled Time|  Missing Dependency|
# |--------------------------------|-----------|--------------------|----------|--------------------|--------------------|
# |             BASKET_ANALYSIS_ETL|  SUCCEEDED|2020-02-20 11:10 GMT|   2:05:00|2020-02-20 11:10 GMT|                    |
# |              Saleforce Pipeline|  SUCCEEDED|2020-02-20 07:00 GMT|   0:11:00|2020-02-20 07:00 GMT|                    |
# |            Campaign Performance|  SUCCEEDED|2020-02-20 16:07 GMT|   0:55:00|2020-02-20 16:00 GMT|                    |
# |         Global Feature Pipeline|  SUCCEEDED|2020-02-20 02:09 GMT|   0:04:00|2020-02-19 18:01 GMT|                    |
# |                  Guest Behavior|  SUCCEEDED|2020-02-20 10:45 GMT|   0:16:00|2020-02-20 10:45 GMT|                    |
# |              guest_exposure_etl|    WAITING|                    |          |2020-02-20 06:10 GMT|/common/dse_data_ingest/ready/2020/02/20/dfaNetworkImpressionsLoader_v3.ready|
# |  Guest Features and WhiteWalker|  SUCCEEDED|2020-02-17 18:05 GMT|   3:16:00|2020-02-17 08:10 GMT|                    |
# |                     Guest Sales|  SUCCEEDED|2020-02-20 14:52 GMT|   1:15:00|2020-02-20 11:00 GMT|                    |
# |                            Lift|  SUCCEEDED|2020-02-16 20:10 GMT|   0:13:00|2020-02-16 20:10 GMT|                    |
# |            non-attributed-sales|  SUCCEEDED|2020-02-16 13:30 GMT|  14:15:00|2020-02-16 13:30 GMT|                    |
# |                Lift SelfService|  SUCCEEDED|2020-02-20 07:11 GMT|   2:07:00|2020-02-20 07:00 GMT|                    |
# |Campaign Performance SelfService|  SUCCEEDED|2020-02-20 07:12 GMT|   1:44:00|2020-02-20 05:30 GMT|                    |```
#
#
# """
#                                      }
#                              ),
                             (
                                     {
                                         "text": f"""
```
Start
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
----------
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
----------
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
----------
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
----------
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
```
"""
                                     }
                             )

                         ])
def test_send_slack(data, webhook):
    # txt = "foo"
    # txt = table_meta_info_report.format_table_info(
    #     [
    #         {
    #             'table_name': 'lift_metrics',
    #             'update_date': '2019-12-08',
    #             'update_time': '14:18',
    #             'max_partition': '2019-11-24',
    #             'done_flag': "Not Exist"
    #         },
    #         {
    #             'table_name': 'lift_metrics',
    #             'update_date': '2019-12-01',
    #             'update_time': '14:19',
    #             'max_partition': '2019-11-17',
    #             'done_flag': "XYZ"
    #         },
    #     ]
    # )

    # status = table_meta_info_report.send_slack({
    #     "blocks": [
    #         {
    #             "type": "section",
    #             "text": {
    #                 "type": "mrkdwn",
    #                 "text": "Daily Update on *Roundel Data Load*:"
    #             }
    #         },
    #         {
    #             "type": "section",
    #             "text": {
    #                 "type": "mrkdwn",
    #                 "text": txt
    #             }
    #         }
    #     ]
    # }, webhook="https://api.target.com/slack_events/v1/webhooks/XYZ")
    # import json
    status = table_meta_info_report.send_slack(data,
        webhook=webhook)

    # print(status)
    assert status is not None
    assert status == 200


# def test_command_results_to_json():
#     content = table_meta_info_report.extract_info_from_results([
#         table_meta_info_report.CommandResult(cmd="hdfs dfs -ls hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/lift_metrics/partition_date=2019-11-24",
#                                  returncode=0,
#                                  output="""\
# drwxrwxr-x   - SVMMAHLSTC mmaholac          0 2019-12-08 14:18 hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/lift_metrics/partition_date=2019-11-24
# """),
#         table_meta_info_report.CommandResult(
#             cmd="hdfs dfs -ls hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/lift_metrics/partition_date=2019-11-23",
#             returncode=0,
#             output="""\
# drwxrwxr-x   - SVMMAHLSTC mmaholac          0 2019-12-01 14:19 hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/lift_metrics/partition_date=2019-11-17
# """)
#
#     ])
#     print(content)
#     assert content is not None
#     assert content == {'table_info':
#                           [
#                               {'table_name': 'lift_metrics', 'update_date': '2019-12-08', 'update_time': '14:18', 'max_partition': '2019-11-24'},
#                               {'table_name': 'lift_metrics', 'update_date': '2019-12-01', 'update_time': '14:19', 'max_partition': '2019-11-17'}
#                           ]
#                         }
#
#
# def test_format_dict():
#     txt = table_meta_info_report.format_table_info({'table_info':
#                           [
#                               {'table_name': 'lift_metrics', 'update_date': '2019-12-08', 'update_time': '14:18', 'max_partition': '2019-11-24'},
#                               {'table_name': 'lift_metrics', 'update_date': '2019-12-01', 'update_time': '14:19', 'max_partition': '2019-11-17'}
#                           ]
#     })
#     print(txt)
#     assert txt is not None

@pytest.mark.parametrize("dict1, dict2, expected",
                         [
        ({'a': {"aa": 1, "bb": 2}, 'b': {"dd": 4}},
         {'a': {"cc": 3}},

        {'a': {'aa': 1, "bb": 2, 'cc': 3}, 'b': {"dd": 4}}
         ),
        ##
        ({'a': {"aa": 1, "bb": 2}},
         {'a': {"cc": 3}},

         {'a': {'aa': 1, "bb": 2, 'cc': 3}}
         ),
        ##
        ({'a': ["aa", "bb"]},
         {'a': {"cc": 3}},
         {'a': [['aa', "bb"], {'cc': 3}]}
         ),
        ##
        ({'a': ["aa", "bb"]},
         {'a': ["cc", "aa"]},
         {'a': ['aa', "bb", 'cc', 'aa']}
         ),
        ##
        ])
def test_merge_dict(dict1, dict2, expected):
    merged = table_meta_info_report.merge_dict(dict1, dict2)
    assert merged == expected


@pytest.mark.parametrize("part_meta, done_file_info, done_file_mapping, expected_rtn",
                         [
                             ({}, {}, {}, {}),
                             ({'tableA': {}}, {}, {}, {"tableA": {"done_flag": "Unknown"}}),
                             ({'tableA': {'hdfs_location': '/common/MMA/xxx'}},
                              {'tableA': {'done_flag':'/common/MMA/2020/01/10/tableA_donefile'}},
                              {},
                              {'tableA': {'hdfs_location': '/common/MMA/xxx',
                                          'done_flag': '/common/MMA/2020/01/10/tableA_donefile'}}),

                         ])
def test_add_done_info(part_meta, done_file_info, done_file_mapping, expected_rtn):
    rtn = table_meta_info_report.add_done_info(part_meta=part_meta, done_file_info=done_file_info, done_file_mapping=done_file_mapping)
    assert rtn == expected_rtn


@pytest.mark.parametrize("cmd_result, expected_rtn",
                         [
                             (table_meta_info_report.CommandResult(cmd='', returncode=0,
                                                                   output='drwxrwxr-x   - SVMMAHLSTC mmaholac          0 2020-01-10 06:26 hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/tableA/sls_d=2020-01-08'),
                              {
                                  'tableA': {
                                      "table_name" : 'tableA',
                                      "update_date":  '2020-01-10',
                                      "update_time": '06:26',
                                      "max_partition": '2020-01-08'
                                  }
                              })
                         ])
def test_parse_partition_result(cmd_result, expected_rtn):
    rtn = table_meta_info_report.parse_partition_result(cmd_result=cmd_result)
    assert rtn == expected_rtn


@pytest.mark.parametrize("ddl, pattern_re, load_freq_pattern, expected",
                         [
                             ("""CREATE TABLE prd_roundel_fnd.tableA (
                             column1 int 'comment 1',
                             )
                             COMMENT 'this is a comment'
                             PARTITIONED BY (`part_col` string COMMENT 'partition comment')
                             LOCATION 'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/tableA'
                             TBLPROPERTIES (
                             'Prop1'='value1',
                             'Prop2'='value2',
)
                             """,
                              re.compile(r"CREATE\s*(?:EXTERNAL\s)*TABLE\s+[`]?(\w+)\.(\w+)[`]?.+LOCATION\s*[\n]?\s*[']([\w/:.]+)['].+",
                                         re.DOTALL | re.MULTILINE), table_meta_info_report.DDL_META_FREQ_PATTERN,
                              { 'tableA':
                                    {'hdfs_location': 'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/tableA',
                                     'load_frequency': 'Daily',
                                     'db_name': 'prd_roundel_fnd',
                                     }
                                }),
                             ("""CREATE TABLE prd_roundel_fnd.tableA (
                                                      column1 int 'comment 1',
                                                      )
                                                      COMMENT 'this is a comment'
                                                      PARTITIONED BY (`part_col` string COMMENT 'partition comment')
                                                      LOCATION 'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/tableA'
                                                      TBLPROPERTIES (
                                                      'Prop1'='value1',
                                                      'Prop2'='value2',
                                                      'LOAD_FREQUENCY'='Weekly'
                         )
                                                      """,
                              re.compile(
                                  r"CREATE\s*(?:EXTERNAL\s)*TABLE\s+[`]?(\w+)\.(\w+)[`]?.+LOCATION\s*[\n]?\s*[']([\w/:.]+)['].+",
                                  re.DOTALL | re.MULTILINE), table_meta_info_report.DDL_META_FREQ_PATTERN,
                              {'tableA':
                                   {'hdfs_location': 'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/tableA',
                                    'load_frequency': 'Weekly',
                                    'db_name': 'prd_roundel_fnd',
                                    }
                               }),
                         ])
def test_parse_ddl_dict(ddl, pattern_re, load_freq_pattern, expected):
    rtn = table_meta_info_report.parse_ddl_dict(ddl=ddl, pattern=pattern_re, load_pattern=load_freq_pattern)
    assert rtn == expected


@pytest.mark.parametrize("cmd_result, expected", [
    (table_meta_info_report.CommandResult(cmd='hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2020/01/20/tableA*', returncode=0,
                                          output='-rw-r--r--   3 SVTMNHOLP  mmaholac          0 2020-01-20 19:12 /common/MMA/data/ready/prd_roundel_fnd/2020/01/20/tableA_daily.ready'),
     {'tableA': {"done_flag": 'tableA_daily.ready'}})
])
def test_parse_done_result(cmd_result, expected):
    rtn = table_meta_info_report.parse_done_result(cmd_result=cmd_result)
    assert rtn == expected


@pytest.mark.parametrize("table_name, max_partition, done_file_mapping, db_name, expected",
                         [
                             ("tableA", "2020-01-20", {}, "prd_roundel_fnd",
                              "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2020/01/20/tableA*")
                         ]
                         )
def test_done_command_str(table_name, max_partition, done_file_mapping, db_name, expected):
    rtn = table_meta_info_report.done_command_str(table_name=table_name, max_partition=max_partition,
                                                  done_file_mapping=done_file_mapping, db_name=db_name)
    assert rtn == expected
