import pytest
import table_meta_info_report

@pytest.fixture(scope="session")
def webhook():
    with open("webhook.txt", "r") as f:
        webhook = f.readline()
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

# @pytest.mark.parametrize("command, expected",
#                          [
#                              ("ls table_meta_info_report.py", "table_meta_info_report.py"),
#                              ("uname", "Darwin"),
#                          ])
# def test_run_command_shell(command: str, expected: str):
#     result = table_meta_info_report.run_command_shell(command=command)
#     assert result == expected


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


def test_get_table_location():
    pass


def test_add_done_file_info():
    pass


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