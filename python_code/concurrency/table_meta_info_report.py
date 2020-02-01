import sys
import time
# import platform
# import asyncio
# from collections import namedtuple, defaultdict
import subprocess
import requests
import json
import argparse
import re

import logging
import os
from typing import List, Dict, DefaultDict, Pattern, Generator, Tuple
# from pprint import pprint

from asyncio_command.command import run_asyncio_commands, CommandResult
from oozie_cli import get_coord_jobs, format_coord_details

for f in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if os.path.isfile(f) and (f.endswith(".egg") or f.endswith(".zip")):
        logging.debug(f"Adding {f} to PYTHONPATH")
        sys.path.insert(0, f)


# _table_meta_fields = ("name", "location", "load_frequency", "update_date", "update_time", "max_partition", "load_done_flag")
# TableMeta = namedtuple("TableMeta", _table_meta_fields,
#                     defaults=(None,)*(len(_table_meta_fields)-1))

# class TableMeta:
#     def __init__(self, name: str, location: str = None, load_frequency: str = None, update_date: str = None,
#                  update_time: str = None, max_partition: str = None, load_done_flag: str = None):
#         self.name = name
#         self.location = location
#         self.load_frequency = load_frequency
#         self.update_time = update_time
#         self.update_date = update_date
#         self.max_partition = max_partition
#         self.load_done_flag = load_done_flag


# DDL_META_RE = r"CREATE\s+(?:EXTERNAL\s)*TABLE\s+[`]?(\w+.\w+)[`]?.+LOCATION\s*[\n]\s*[']([\w/:.]+)[']"
# DDL_META_RE = r"CREATE\s+(?:EXTERNAL\s)*TABLE\s+[`]?(\w+)\.(\w+)[`]?.+LOCATION\s*[\n]\s*[']([\w/:.]+)['].+"
DDL_META_RE = r"CREATE\s*(?:EXTERNAL\s)*TABLE\s+[`]?(\w+)\.(\w+)[`]?.+LOCATION\s*[\n]\s*[']([\w/:.]+)['].+"
DDL_META_PATTERN = re.compile(DDL_META_RE, re.DOTALL | re.MULTILINE)
DDL_META_FREQ_PATTERN = re.compile(r".+'LOAD_FREQUENCY'='(\w+)'", re.DOTALL | re.MULTILINE)

DB_NAME = "prd_roundel_fnd"
MAX_CONCURRENCY = 10

# f"prd_roundel_fnd.salesforce_reports",
# f"{DB_NAME}.active_reports",
# f"{DB_NAME}.behavior_report_data",
# f"{DB_NAME}.camp_perf_reach_counts",
# f"{DB_NAME}.cumltv_camp_gst_line_metrics",
# f"{DB_NAME}.glob_item_feature_set",
# f"{DB_NAME}.line_impression_counts",
# f"{DB_NAME}.ss_report_logic",
# f"{DB_NAME}.frctnl_allctn",
TABLE_LIST = (f"{DB_NAME}.active_guest_exposure",
              f"{DB_NAME}.active_user_exposure",
              f"{DB_NAME}.campaign_guest_line_performance",
              f"{DB_NAME}.campaign_line_performance",
              f"{DB_NAME}.campaign_report_performance",
              f"{DB_NAME}.campaign_guest_line_performance_ss",
              f"{DB_NAME}.campaign_line_performance_ss",
              f"{DB_NAME}.campaign_report_performance_ss",
              # f"{DB_NAME}.exception_table",
              f"{DB_NAME}.guest_behavior",
              f"{DB_NAME}.guest_features_global",
              # f"{DB_NAME}.guest_features_item",
              f"{DB_NAME}.guest_features_item_final",
              f"{DB_NAME}.guest_spend",
              f"{DB_NAME}.lift_metrics", f"{DB_NAME}.lift_metrics_ss",
              f"{DB_NAME}.sf_reporting_insights",
              f"{DB_NAME}.whitewalker_test_control_final",
              f"{DB_NAME}.whitewalker_test_control_final_ss")


def format_table_info(data: Dict) -> str:
    # pprint(data)
    slack_text = f"""
        ```
|{"Table Name":>40}|{"Date":>12}|{"Time":>6}|{"Max Partition":>13}|{"Frequency":>11}|{"Status":>10}|
|{"":->40}|{"":->12}|{"":->6}|{"":->13}|{"":->11}|{"":->10}|"""
    for name, tbl in data.items():
        if tbl["done_flag"] == "Not Exist":
            done_status = "In Progress/NA"
        else:
            done_status = "Completed"

        slack_text += f"""{os.linesep}|{name:>40}|{tbl.get("update_date", ""):>12}|{tbl["update_time"]:>6}|{tbl["max_partition"]:>13}|{tbl["load_frequency"]:>11}|{done_status:>10}|"""
    slack_text += "```"
    return slack_text


# def parse_partition_result_old(cmd_result: CommandResult) -> TableMeta:
#     rtn = None
#     if cmd_result is not None:
#         if cmd_result.output is not None and str(cmd_result.output).strip() != '':
#             logging.debug(f"cmd_result={cmd_result}")
#             if '=' in cmd_result.output:
#                 # Example output:
#                 # drwxrwxr-x   - SVMMAHLSTC mmaholac          0
#                 # 2019-12-10 06:26 hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend/sls_d=2019-12-08
#                 content, max_partition = str(cmd_result.output).strip().split('=')[:2]
#                 update_date, update_time, hdfs_path = content.split(' ')[-3:]
#                 tbl = hdfs_path.split('/')[-2]
#                 rtn = TableMeta(name=tbl, update_date=update_date, update_time=update_time, max_partition=max_partition)
#                 # rtn = (tbl, update_date, update_time, max_partition)
#                 #     {
#                 #     "table_name": tbl,
#                 #     "update_date": update_date,
#                 #     "update_time": update_time,
#                 #     "max_partition": max_partition
#                 # }
#             else:
#                 logging.warning(f"No partition found in {cmd_result.output}")
#         else:
#             logging.warning(f"output is empty for {cmd_result.cmd}")
#
#     return rtn
#

def parse_partition_result(cmd_result: CommandResult) -> Dict:
    rtn = None
    if cmd_result is not None:
        if cmd_result.output is not None and str(cmd_result.output).strip() != '':
            logging.debug(f"cmd_result={cmd_result}")
            if '=' in cmd_result.output:
                # Example output:
                # drwxrwxr-x   - SVMMAHLSTC mmaholac          0
                # 2019-12-10 06:26 hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend/sls_d=2019-12-08
                content, max_partition = str(cmd_result.output).strip().split('=')[:2]
                update_date, update_time, hdfs_path = content.split(' ')[-3:]
                tbl = hdfs_path.split('/')[-2]
                # rtn = {tbl: [max_partition, update_date, update_time]}
                rtn = {
                    tbl:
                        {
                            "table_name" : tbl,
                            "update_date": update_date,
                            "update_time": update_time,
                            "max_partition": max_partition
                        }
                }
            else:
                logging.warning(f"No partition found in {cmd_result.output}")
        else:
            logging.warning(f"output is empty for {cmd_result.cmd}")

    return rtn


def get_all_tables(dbname: str):
    completed_process = subprocess.run(f"""
        hive -e "use {dbname}; show tables;"
        """,
                                       capture_output=True,
                                       shell=True)
    if completed_process.returncode == 0:
        result = completed_process.stdout.decode().strip().split(os.linesep)
    else:
        logging.error(f"ERROR getting tables {completed_process}")
        result = []

    return [f"{dbname}.{tbl}" for tbl in result]


def get_ddl_commands(tables: List[str]) -> Generator:
    return (get_ddl_command(table_name=tbl) for tbl in tables)


def get_ddl_command(table_name: str) -> str:
    return f"""hive -e "show create table {table_name};" """


# def get_meta_from_ddl_results(cmd_results: List[CommandResult]) -> Generator:
#     for cmd, rc, ddl in cmd_results:
#         # meta = get_meta_from_ddl(ddl=ddl, pattern=DDL_META_PATTERN)
#         # yield meta.name, meta.location, meta.load_frequency
#         yield parse_ddl(ddl=ddl, pattern=DDL_META_PATTERN)
#
#
# def parse_ddl(ddl: str,
#               pattern: Pattern = DDL_META_PATTERN,
#               load_pattern: Pattern = DDL_META_FREQ_PATTERN) -> TableMeta:
#     # ddl_location_freq = re.compile(ddl_location_re, re.DOTALL | re.MULTILINE)
#     matched = pattern.match(ddl)
#
#     table_name, hdfs_location, load_frequency = None, None, "Daily"
#     if matched:
#         # pprint(matched.groups())
#         # table_name, hdfs_location, load_freq = matched.groups()
#         table_name, hdfs_location = matched.groups()
#     else:
#         print(f"Not matched! {ddl}")
#         logging.warning(f"Not matched! {ddl}")
#
#     matched = load_pattern.match(ddl)
#     if matched:
#         load_frequency = matched.group(1)
#     else:
#         print(f"Load Frequency not matched! {ddl}")
#         logging.warning(f"Load Frequency Not matched! {ddl}")
#
#     tbl_meta = {table_name: [hdfs_location, load_frequency]}
#     return TableMeta(name=table_name,
#                      location=hdfs_location,
#                      load_frequency=load_frequency)
#

def parse_ddl_dict(ddl: str,
                   pattern: Pattern = DDL_META_PATTERN,
                   load_pattern: Pattern = DDL_META_FREQ_PATTERN) -> Dict:
    matched = None
    try:
        # ddl_location_freq = re.compile(ddl_location_re, re.DOTALL | re.MULTILINE)
        matched = pattern.match(ddl)
    except TypeError as e:
        print(f"Type Error {e} trying to match DDL in string {ddl}")
        logging.error(f"Type Error {e} trying to match DDL in string {ddl}")

    db_name, table_name, hdfs_location, load_frequency = None, None, None, "Daily"
    if matched:
        # pprint(matched.groups())
        # table_name, hdfs_location, load_freq = matched.groups()
        db_name, table_name, hdfs_location = matched.groups()
    else:
        print(f"Not matched! {ddl}")
        logging.warning(f"Not matched! {ddl}")

    matched = load_pattern.match(ddl)
    if matched:
        load_frequency = matched.group(1)
    else:
        print(f"Load Frequency not matched! {ddl}")
        logging.warning(f"Load Frequency Not matched! {ddl}")

    return {table_name: {"hdfs_location": hdfs_location, "load_frequency": load_frequency, "db_name": db_name}}


def send_slack(json_data: Dict, webhook: str) -> int:
    # print(json.dumps(json_data))
    rtn = 200
    resp = requests.post(url=webhook,
                         data=json.dumps(json_data),
                         headers={'Content-Type': "application/json"})
    if resp.status_code != 200:
        logging.error(f"Error sending message to slack: {json_data}")
        logging.error(f"{resp}")
        rtn = resp.status_code
    return rtn


# def done_commands_from_table(table_list: List[Dict],
#                              done_file_mapping: Dict = None) -> List[str]:
#     commands = []
#     for tbl in table_list:
#         table_name = tbl.get("table_name", None)
#         if tbl is not None and table_name is not None and tbl.get(
#                 "max_partition", None) is not None:
#             # find done files
#             # done_file[tbl["table_name"]] = None
#             part = tbl["max_partition"]
#             if '-' in part:
#                 part = part.replace('-', '/')
#                 # print(f"{part}")
#             else:
#                 matched = re.match(part,
#                                    '([1-9][0-9]{3})([01][0-9])([0-3][0-9])')
#                 if matched:
#                     logging.warning(f"Partition value format change: {part}")
#                     part = '/'.join(matched.groups())
#                 else:
#                     logging.warning(
#                         f"Unknown partition value format {part}, SKIP")
#             if done_file_mapping is not None and done_file_mapping.get(
#                     table_name, None) is not None:
#                 logging.debug(
#                     f"mapping found {table_name} : {done_file_mapping[table_name]}"
#                 )
#                 table_name = done_file_mapping[table_name]
#             else:
#                 logging.debug(f"No mappings!!! {done_file_mapping}")
#             commands.append(
#                 f"""hdfs dfs -ls /common/MMA/data/ready/{DB_NAME}/{part}/{table_name}*"""
#             )
#         else:
#             logging.warning(f"Table name or max partition is None!")
#     return commands


def done_command_str(table_name: str, max_partition: str, done_file_mapping: Dict = None,
                     db_name: str = DB_NAME) -> str:
    command = None
    if table_name is not None and max_partition is not None:
        # find done files
        # done_file[tbl["table_name"]] = None
        part = max_partition
        # table_name = table_meta.name
        if '-' in part:
            part = part.replace('-', '/')
            # print(f"{part}")
        else:
            matched = re.match(part,
                               '([1-9][0-9]{3})([01][0-9])([0-3][0-9])')
            if matched:
                logging.warning(f"Partition value format change: {part}")
                part = '/'.join(matched.groups())
            else:
                logging.warning(
                    f"Unknown partition value format {part}, SKIP")
        if done_file_mapping is not None and done_file_mapping.get(table_name, None) is not None:
            logging.debug(
                f"mapping found {table_name} : {done_file_mapping[table_name]}"
            )
            table_name = done_file_mapping[table_name]
        else:
            logging.debug(f"No mappings!!! {done_file_mapping}")
        command = f"""hdfs dfs -ls /common/MMA/data/ready/{db_name}/{part}/{table_name}*"""
    else:
        logging.warning(f"Table name or max partition is None!")
    return command


# def extract_done_flag(done_file_cmd_results: List[CommandResult]
#                       ) -> DefaultDict:
#     # Use defaultdict to avoid missing key exception
#     done_file = defaultdict(lambda: "Not Exist")
#
#     for cmd, rc, output in done_file_cmd_results:
#         logging.debug(f"Done file checking output: {output}")
#
#         if cmd is not None and cmd.strip(
#         ) != "" and output is not None and output.strip() != "":
#             tbl_name = cmd.split('/')[-1][:-1]
#             if "No such file" in output:
#                 logging.warning(f"Done file not found: {output}")
#                 done_file[tbl_name] = "Not Exist"
#             elif f"{tbl_name}" in output:
#                 done_file[tbl_name] = output.strip().split('/')[-1]
#             else:
#                 logging.warning(
#                     f"Unknown done file command output string {output}")
#                 done_file[tbl_name] = output.strip()
#         else:
#             logging.warning(f"No output from {cmd}")
#     return done_file


# def parse_done_result_old(cmd_result: CommandResult) -> Tuple:
#     # Use defaultdict to avoid missing key exception
#     # done_file = defaultdict(lambda: "Not Exist")
#     tbl_name, done_file_name = "Unknown", None
#     if cmd_result is not None and cmd_result.cmd is not None \
#             and cmd_result.cmd.strip() != "" \
#             and cmd_result.output is not None \
#             and cmd_result.output.strip() != "":
#         tbl_name = cmd_result.cmd.split('/')[-1][:-1]
#         if "No such file" in cmd_result.output:
#             logging.warning(f"Done file not found: {cmd_result.output}")
#             # done_file[tbl_name] = "Not Exist"
#         elif f"{tbl_name}" in cmd_result.output:
#             done_file_name = cmd_result.output.strip().split('/')[-1]
#         else:
#             logging.warning(
#                 f"Unknown done file command output string {cmd_result.output}")
#             done_file_name = cmd_result.output.strip()
#     else:
#         logging.warning(f"No output from {cmd_result.cmd}")
#     return TableMeta(name=tbl_name, load_done_flag=done_file_name)


def parse_done_result(cmd_result: CommandResult) -> Dict:
    # Use defaultdict to avoid missing key exception
    # done_file = defaultdict(lambda: "Not Exist")
    tbl_name, done_file_name = "Unknown", None
    if cmd_result is not None and cmd_result.cmd is not None \
            and cmd_result.cmd.strip() != "" \
            and cmd_result.output is not None \
            and cmd_result.output.strip() != "":
        tbl_name = cmd_result.cmd.split('/')[-1][:-1]
        if "No such file" in cmd_result.output:
            logging.warning(f"Done file not found: {cmd_result.output}")
            # done_file[tbl_name] = "Not Exist"
        elif f"{tbl_name}" in cmd_result.output:
            done_file_name = cmd_result.output.strip().split('/')[-1]
        else:
            logging.warning(
                f"Unknown done file command output string {cmd_result.output}")
            done_file_name = cmd_result.output.strip()
    else:
        logging.warning(f"No output from {cmd_result.cmd}")
    return {tbl_name: {"done_flag": done_file_name}}


# def merge_meta_list(meta1: List[TableMeta], meta2: List[TableMeta]) -> List[TableMeta]:
#     # do we care about doing deep or shallow copy here?
#     merged = list(meta1)
#     for m1 in merged:
#         m = next(m2 for m2 in meta2 if m1.name == m2.name)
#         for k, v in m1.items()
#         m1.max_partition = m.max_partition if m.max_partition is not None
#         m1.load_done_flag = m.load_done_flag if m.load_done_flag is not None


# def merge_meta(meta1: TableMeta, meta2: TableMeta) -> TableMeta:
#     meta = None
#     if meta1.name == meta2.name:
#         for k in _table_meta_fields:
#              = meta2.max_partition or meta1.max_partition


def merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """
    Merge two dictionaries
    :param dict1:
    :param dict2:
    :return: merged dict
    """
    dict3 = {**dict2, **dict1}
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            if isinstance(value, dict) and isinstance(dict2[key], dict):
                dict3[key] = {**value, **dict2[key]}
            elif isinstance(value, list) and isinstance(dict2[key], list):
                dict3[key] = value + dict2[key]
            else:
                # raise ValueError(f"one of the dict value is not dict")
                logging.warning(f"one of the dict value is not dict")
                dict3[key] = [value, dict2[key]]

    return dict3


def add_done_info(part_meta: Dict, done_file_info: Dict, done_file_mapping: Dict):
    rtn = {}
    for name, meta in part_meta.items():
        done_meta = {}
        if name in done_file_info:
            # TODO: check done_file_info[name] value is a dict
            done_meta = done_file_info[name]
        elif name in done_file_mapping and done_file_mapping[name] in done_file_info:
            done_meta = done_file_info[done_file_mapping[name]]
        else:
            logging.warning(f"Done file information not available for {name}, {done_file_info}, {done_file_mapping}")
            done_meta = {"done_flag": "Unknown"}
        rtn[name] = {**meta, **done_meta}
    return rtn


# def add_done_file_info(table_list: List[Dict]) -> List[Dict]:
#     # done_file = {}
#     # commands = []
#     # for tbl in table_list:
#     #     if tbl is not None and tbl.get("table_name", None) is not None and tbl.get("max_partition", None) is not None:
#     #         # find done files
#     #         done_file[tbl["table_name"]] = None
#     #         part = tbl["max_partition"]
#     #         if '-' in part:
#     #             part = part.replace('-', '/')
#     #             # print(f"{part}")
#     #         else:
#     #             matched = re.match(part, '([1-9][0-9]{3})([01][0-9])([0-3][0-9])')
#     #             if matched:
#     #                 logging.warning(f"Partition value format change: {part}")
#     #                 part = '/'.join(matched.groups())
#     #             else:
#     #                 logging.warning(f"Unknown partition value format {part}, SKIP")
#     #     commands.append(f"""hdfs dfs -ls /common/MMA/data/ready/{DB_NAME}/{part}/{tbl["table_name"]}*""")
#
#     commands = done_commands_from_table(table_list=table_list)
#     done_file_results = run_asyncio_commands(commands=commands, max_concurrent_tasks=MAX_CONCURRENCY)
#
#     done_file = extract_done_flag(done_file_results)
#     # for cmd, rc, output in done_file_results:
#     #     logging.debug(f"Done file checking output: {output}")
#     #     if output is not None and str(output).strip() != "":
#     #         tbl_name = cmd.split('/')[-1][:-1]
#     #         if "No such file" in output:
#     #             logging.warning(f"Done file not found: {output}")
#     #             done_file[tbl_name] = "Not Exist"
#     #         else:
#     #             done_file[tbl_name] = output.split('/')[-1]
#     #     else:
#     #         logging.warning(f"No output from {cmd}")
#     for tbl in table_list:
#         tbl["done_flag"] = done_file[tbl["table_name"]]
#
#     return table_list


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Send Hive table metadata to slack channel')
    parser.add_argument('--slack-webhook',
                        type=str,
                        required=True,
                        dest='slack_webhook',
                        help="The slack webhook URL")
    parser.add_argument(
        '--message-header',
        type=str,
        required=False,
        dest='message_header',
        default=f"Latest table information in *{DB_NAME}* {os.linesep}"
        f"Partition Status: _Completed_=Max Partition Loaded, {os.linesep}"
        f"                  _In Progress/NA_=Either Max Partition is being loaded or No Information Available "
        f"(Done flag not created/supported)",
        help="The slack message header added in front of the table information"
    )
    args = parser.parse_args()
    slack_webhook = args.slack_webhook
    message_header = args.message_header

    done_file_mapping = {
        "campaign_guest_line_performance": "campaign_report_performance",
        "campaign_line_performance": "campaign_report_performance",
        "campaign_guest_line_performance_ss": "campaign_performance_ss",
        "campaign_line_performance_ss": "campaign_performance_ss",
        "campaign_report_performance_ss": "campaign_performance_ss",
        "active_guest_exposure": "campaign_report_performance",
        "active_user_exposure": "campaign_report_performance",
        "guest_features_item": "whitewalker_test_control_final",
        "guest_features_item_final": "whitewalker_test_control_final",
        "sf_reporting_insights": "salesforce_reports",
    }
    start = time.perf_counter()
    # TODO: Change it to use queues between the two async commands
    # ----------------------------------
    # Get the DDLs for each table in the list
    # ----------------------------------
    #
    ddl_results = run_asyncio_commands(
        commands=get_ddl_commands(tables=TABLE_LIST),
        max_concurrent_tasks=min(len(TABLE_LIST), MAX_CONCURRENCY))

    # pprint(ddl_results)
    # ----------------------------------
    # parse the DDLs to get {name:[hdfs_location, load_frequency]} dictionary
    # ----------------------------------
    # table_meta = []
    # for name, data_loc, load_freq in get_meta_from_ddl_results(cmd_results=ddl_results):
    #     if data_loc is not None:
    #         table_meta.append({'table_name': name, 'data_loc': data_loc, 'load_frequency': load_freq})
    tbl_meta = {k: v
                for d in
                (parse_ddl_dict(ddl=ddl_result.output, pattern=DDL_META_PATTERN, load_pattern=DDL_META_FREQ_PATTERN)
                 for ddl_result in ddl_results)
                for k, v in d.items()
                }

    # ----------------------------------
    # Get max_partition info for each table in the dict
    # ----------------------------------

    results = run_asyncio_commands(commands=[
        f"hdfs dfs -ls {meta['hdfs_location']} | tail -1"
        for table_name, meta in tbl_meta.items()
        if meta is not None and meta['hdfs_location'] is not None], max_concurrent_tasks=MAX_CONCURRENCY)

    # results = run_asyncio_commands(commands=[
    #     f"hdfs dfs -ls {data_loc} | tail -1"
    #     for _, data_loc, load_freq in get_meta_from_ddl_results(cmd_results=ddl_results)
    #     if data_loc is not None
    # ],
    #                                max_concurrent_tasks=MAX_CONCURRENCY)
    # results = run_asyncio_commands(commands=[
    #             f"hdfs dfs -ls {tbl_info['data_loc']} | tail -1"
    #             for tbl_info in table_meta
    #         ], max_concurrent_tasks=MAX_CONCURRENCY)
    end = time.perf_counter()
    logging.info(f"Asyncio Time Taken: {round(end - start, 4):.4f}")
    print(f"Asyncio Time Taken: {round(end - start, 4):.4f}")

    # Send to Slack
    # pprint(results)
    #
    # Get max partition and update time for tables

    table_partition_meta_dict = \
        {k: v for d in (parse_partition_result(cmd_result=result) for result in results) for k, v in d.items()}

    # pprint(table_partition_meta_dict)
    # table_info = extract_info_from_results(cmd_results=results)

    # for i in table_info:
    #     # TODO: use collections.ChainMap?
    #     table_meta[i['table_name']].update(i)

    # table_info["table_info"] = add_done_file_info(table_list=table_info["table_info"])
    # commands = done_commands_from_table(table_list=table_info,
    #                                     done_file_mapping=done_file_mapping)
    done_file_results = run_asyncio_commands(
        commands=[done_command_str(
            table_name=name, max_partition=partition_meta["max_partition"], done_file_mapping=done_file_mapping
        )
            for name, partition_meta in table_partition_meta_dict.items()],
        max_concurrent_tasks=MAX_CONCURRENCY)

    done_file_info = {k: v for d in (parse_done_result(cmd_result=result)
                                     for result in done_file_results) for k, v in d.items()}
    # done_file = extract_done_flag(done_file_results)

    # table_meta_list = merge_meta_list(table_partition_meta_list, done_file_results)
    # for tbl in table_info:
    #     try:
    #         tbl["done_flag"] = done_file[done_file_mapping[tbl["table_name"]]]
    #     except KeyError:
    #         logging.info(
    #             f"""No mapping exists, use the original table name {tbl["table_name"]}"""
    #         )
    #         tbl["done_flag"] = done_file[tbl["table_name"]]
    #     # if done_file_mapping.get(tbl["table_name"], None) is not None:
    #     #     tbl["done_flag"] = done_file[done_file_mapping[tbl["table_name"]]]
    #     # else:
    #     #     tbl["done_flag"] = done_file[tbl["table_name"]]

    # from pprint import pprint
    # pprint(table_info)

    tbl_meta_partition_done = add_done_info(part_meta=table_partition_meta_dict,
                                            done_file_info=done_file_info, done_file_mapping=done_file_mapping)
    table_info = merge_dict(tbl_meta, tbl_meta_partition_done)

    coord_job_details = get_coord_jobs(user='SVMMAHLSTC', status='RUNNING')

    coord_job_str = format_coord_details(job_details=coord_job_details)
    table_info_str = format_table_info(data=table_info)
    status = send_slack(json_data={
        "channel": "datasciences-roundel-ops",
        "text": f"{message_header} {table_info_str} {coord_job_str}"
    },
        webhook=slack_webhook)

    if status != 200:
        logging.error(f"Error sending slack message: {status}")
    else:
        logging.info(f"Successfully sent slack message")

    # start = time.perf_counter()
    # results_sync = run_commands(shell_commands)
    # end = time.perf_counter()
    # # pprint(results_sync)
    # logging.info(f"synch Time Taken: {round(end - start, 4):.4f}")
    # print(f"Synch Time Taken: {round(end - start, 4):.4f}")


# For performance comparison
#
def run_command_shell_sync(command):
    completed_process = subprocess.run(command,
                                       capture_output=True,
                                       shell=True)
    if completed_process.returncode == 0:
        result = CommandResult(cmd=command,
                               returncode=completed_process.returncode,
                               output=completed_process.stdout)
    else:
        result = CommandResult(cmd=command,
                               returncode=completed_process.returncode,
                               output=completed_process.stderr)

    return result


def run_commands(commands):
    return [run_command_shell_sync(cmd) for cmd in commands]


if __name__ == "__main__":
    main()
