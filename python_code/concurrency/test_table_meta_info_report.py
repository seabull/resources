import pytest
import table_meta_info_report
import re
import types

@pytest.fixture(scope="session")
def webhook():
    with open("webhook.txt", "r") as f:
        webhook = f.readline().strip()
    return webhook


# def test_get_table_location():
#     table_meta_info_report.get_table_location(("prd_roundel_fnd.guest_behavior"))
#     assert False


@pytest.mark.parametrize("lst, chunk_size, expected", [
    ([1,2,3,4,5,6,7,8], 5, [[1,2,3,4,5], [6,7,8]]),
    (('a','b','c','d'), 2, [('a','b'), ('c','d')]),
])
def test_make_chunks(lst, chunk_size, expected):
    result = list(table_meta_info_report.make_chunks(lst, chunk_size))
    assert result is not None
    assert result == expected


@pytest.mark.parametrize("command, expected",
                         [
                             ("ls table_meta_info_report.py", table_meta_info_report.CommandResult(cmd="ls table_meta_info_report.py",
                                                                                                   returncode=0,
                                                                                                   output="table_meta_info_report.py")),
                             ("uname", table_meta_info_report.CommandResult(cmd="uname",
                                                                            returncode=0,
                                                                            output="Darwin")),
                         ])
@pytest.mark.asyncio
async def test_run_command_shell(command: str, expected: str):
    result = await table_meta_info_report.run_command_shell(command=command)
    assert result == expected


@pytest.mark.parametrize("commands, max_concurrency, expected", [
    (["ls table_meta_info_report.py"], 5,
     [table_meta_info_report.CommandResult("ls table_meta_info_report.py", 0, "table_meta_info_report.py")]),
    (["uname", "ls table_meta_info_report.py"], 3,
     [table_meta_info_report.CommandResult("uname", 0, "Darwin"),
      table_meta_info_report.CommandResult("ls table_meta_info_report.py", 0, "table_meta_info_report.py")]),
    ([], 2, []),
])
def test_run_asyncio_commands(commands, max_concurrency, expected):
    result = table_meta_info_report.run_asyncio_commands(commands=commands, max_concurrent_tasks=max_concurrency)
    assert result == expected


@pytest.mark.format
def test_format_table_info(webhook):
    d = table_meta_info_report.format_table_info({"table_info": [{"table_name": "Guest_spend",
                                                      "max_partition": "2019-12-02",
                                                      "done_flag": "Not Exist",
                                                      "update_date": "2019-12-01",
                                                      "update_time": "10:00"
                                                                  }]})
    assert d == """\
\n        ```\n\
|                              Table Name|        Date|        Time|  Max Partition|Partition Status|\n\
|----------------------------------------|------------|------------|---------------|----------------|\n\
|                             Guest_spend|  2019-12-01|       10:00|     2019-12-02|  In Progress/NA|\
```"""


# {"table_name": "",
#  "update_date": "",
#  "update_time": "",
#  "max_partition": "",
#  }


@pytest.mark.parametrize("cmd_results, expected", [
    ([table_meta_info_report.CommandResult(cmd="uname", returncode=0, output="Darwin")], {"table_info": [
                ]}
     ),
])
def test_extract_info_from_results(cmd_results, expected):
    result = table_meta_info_report.extract_info_from_results(cmd_results=cmd_results)
    assert result == expected


def test_get_all_tables():
    pass


@pytest.mark.parametrize("table_list, expected_cmds", [
    (["prd_roundel_fnd.guest_spend"], ["""hive -e "show create table prd_roundel_fnd.guest_spend;" """]),
    (["prd_roundel_fnd.guest_spend", "prd_roundel_fnd.guest_behavior"],
     ["""hive -e "show create table prd_roundel_fnd.guest_spend;" """,
      """hive -e "show create table prd_roundel_fnd.guest_behavior;" """,
      ]),
])
def test_get_ddl_commands(table_list, expected_cmds):
    result = table_meta_info_report.get_ddl_commands(table_list)
    assert isinstance(result, types.GeneratorType)
    assert list(result) == expected_cmds


def test_get_meta_from_ddl_results():
    pass


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


@pytest.mark.parametrize("ddl, pattern, expected", [
    ("""CREATE TABLE prd_roundel_fnd.guest_spend ( ) LOCATION
    'hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend'
    """,
     table_meta_info_report.DDL_META_PATTERN,
     table_meta_info_report.TableMeta(name="prd_roundel_fnd.guest_spend",
                                      location="hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend",
                                      load_frequency="Daily")
     )
])
def test_get_meta_from_ddl(ddl, pattern, expected):
    result = table_meta_info_report.get_meta_from_ddl(ddl=ddl, pattern=pattern)
    assert result == expected


@pytest.mark.parametrize("tables, done_file_mapping, expected_commands", [
    ([{"table_name": "tableA", "max_partition": '2019-12-02'}], None,
     ["hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/12/02/tableA*"]),

    ([{"table_name": "tableA", "max_partition": '2019-12-02'}, {"table_name": "tableB", "max_partition": '2020-01-02'}],
     None,
     ["hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/12/02/tableA*",
      "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2020/01/02/tableB*"]),

    ([{"table_name": "table1", "max_partition": '2019-12-02'}, {"table_name": "table2", "max_partition": '2020-01-02'}],
     {"table1": "table2"},
     ["hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2019/12/02/table2*",
      "hdfs dfs -ls /common/MMA/data/ready/prd_roundel_fnd/2020/01/02/table2*"]),

    ([], None,
     []),
])
def test_done_commands_from_table(tables, done_file_mapping, expected_commands):
    commands = table_meta_info_report.done_commands_from_table(table_list=tables, done_file_mapping=done_file_mapping)
    assert commands == expected_commands


@pytest.mark.parametrize("cmd_results, expected_flags", [
    ([table_meta_info_report.CommandResult(cmd="", returncode=0, output="")],
    []
    )
])
def test_extract_done_flag(cmd_results, expected_flags):
    flags = table_meta_info_report.extract_done_flag(cmd_results)


pytest.mark.slack
def test_send_slack(webhook):
    txt = table_meta_info_report.format_table_info({'table_info':
                          [
                              {'table_name': 'lift_metrics', 'update_date': '2019-12-08', 'update_time': '14:18', 'max_partition': '2019-11-24', 'done_flag': "Not Exist"},
                              {'table_name': 'lift_metrics', 'update_date': '2019-12-01', 'update_time': '14:19', 'max_partition': '2019-11-17', 'done_flag': "XYZ"},
                          ]
    })
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
    status = table_meta_info_report.send_slack({
        "text": f"*UNIT TEST* _PLEASE IGNORE_ -- Latest table information for *Roundel* {txt}"
    }, webhook=webhook)

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