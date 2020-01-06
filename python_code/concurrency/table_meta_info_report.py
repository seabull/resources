import sys
import time
# import platform
import asyncio
import subprocess
from collections import namedtuple, defaultdict
import requests
import json
import argparse
import re

# from pprint import pprint
import logging
import os
from typing import List, Dict, DefaultDict, Pattern, Generator

for f in os.listdir(os.path.dirname(os.path.abspath(__file__))):
    if os.path.isfile(f) and (f.endswith(".egg") or f.endswith(".zip")):
        logging.debug(f"Adding {f} to PYTHONPATH")
        sys.path.insert(0, f)

CommandResult = namedtuple("CommandResult", "cmd returncode output")
TableMeta = namedtuple("TableMeta", "name location load_frequency")
DDL_META_RE = r"CREATE\s+(?:EXTERNAL\s)*TABLE\s+[`]?(\w+.\w+)[`]?.+LOCATION\s*[\n]\s*[']([\w/:.]+)[']"
DDL_META_PATTERN = re.compile(DDL_META_RE, re.DOTALL | re.MULTILINE)

DB_NAME = "prd_roundel_fnd"
MAX_CONCURRENCY=10

# f"prd_roundel_fnd.salesforce_reports",
# f"{DB_NAME}.active_reports",
# f"{DB_NAME}.behavior_report_data",
# f"{DB_NAME}.camp_perf_reach_counts",
# f"{DB_NAME}.cumltv_camp_gst_line_metrics",
# f"{DB_NAME}.glob_item_feature_set",
# f"{DB_NAME}.line_impression_counts",
# f"{DB_NAME}.ss_report_logic",
# f"{DB_NAME}.frctnl_allctn",
TABLE_LIST = (
    f"{DB_NAME}.active_guest_exposure",
    f"{DB_NAME}.active_user_exposure",
    f"{DB_NAME}.campaign_guest_line_performance",
    f"{DB_NAME}.campaign_line_performance",
    f"{DB_NAME}.campaign_report_performance",
    f"{DB_NAME}.campaign_guest_line_performance_ss",
    f"{DB_NAME}.campaign_line_performance_ss",
    f"{DB_NAME}.campaign_report_performance_ss",
    f"{DB_NAME}.exception_table",
    f"{DB_NAME}.guest_behavior",
    f"{DB_NAME}.guest_features_global",
    f"{DB_NAME}.guest_features_item",
    f"{DB_NAME}.guest_features_item_final", f"{DB_NAME}.guest_spend",
    f"{DB_NAME}.lift_metrics", f"{DB_NAME}.lift_metrics_ss",
    f"{DB_NAME}.sf_reporting_insights",
    f"{DB_NAME}.whitewalker_test_control_final",
    f"{DB_NAME}.whitewalker_test_control_final_ss"
)


async def run_command(*args) -> CommandResult:
    """Run command in subprocess.

    Example from:
        http://asyncio.readthedocs.io/en/latest/subprocess.html
    """
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    logging.info(f"Started: {args}, pid={process.pid}")  # , flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        logging.info(
            f"Done: {args}, pid={process.pid}, result: {stdout.decode().strip()}"
        )  # , flush=True)
        result = CommandResult(cmd=str(args),
                               returncode=process.returncode,
                               output=stdout.decode().strip())
    else:
        logging.error(
            f"Failed: {args}, pid={process.pid}, result: {stderr.decode().strip()}"
        )  # , flush=True)
        result = CommandResult(cmd=str(args),
                               returncode=process.returncode,
                               output=stderr.decode().strip())

    # Result
    # result = stdout.decode().strip()

    # Return stdout
    return result


async def run_command_shell(command: str) -> CommandResult:
    """Run command in subprocess (shell).

    Note:
        This can be used if you wish to execute e.g. "copy"
        on Windows, which can only be executed in the shell.
    """
    # Create subprocess
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    # Status
    logging.info(
        f"Started:{command}, (pid = {str(process.pid)})")  # , flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        logging.info(f"Done:{command}, pid = {str(process.pid)}")  # , flush=True)
        result = CommandResult(cmd=command,
                               returncode=process.returncode,
                               output=stdout.decode().strip())
    else:
        logging.error(f"Failed:{command}, pid = {str(process.pid)}")  # , flush=True)
        result = CommandResult(cmd=command,
                               returncode=process.returncode,
                               output=stderr.decode().strip())

    # Result
    # result = stdout.decode().strip()

    # Return stdout
    return result


async def get_location_from_ddl(ddl: str) -> str:
    pass


def make_chunks(lst, n):
    """Yield successive n-sized chunks from l.

    Note:
        Taken from https://stackoverflow.com/a/312464
    """
    # Assume Python 3
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def run_asyncio_commands(commands: List[str],
                         max_concurrent_tasks: int = 0) -> List[CommandResult]:
    """Run tasks asynchronously using asyncio and return results.

    If max_concurrent_tasks are set to 0, no limit is applied.

    Note:
        By default, Windows uses SelectorEventLoop, which does not support
        subprocesses. Therefore ProactorEventLoop is used on Windows.
        https://docs.python.org/3/library/asyncio-eventloops.html#windows
    """
    consolidated_results = []
    tasks = [run_command_shell(cmd) for cmd in commands]

    if max_concurrent_tasks == 0:
        chunks = [tasks]
        num_chunks = len(chunks)
    else:
        chunks = make_chunks(lst=tasks, n=max_concurrent_tasks)
        num_chunks = len(list(make_chunks(lst=tasks, n=max_concurrent_tasks)))

    if asyncio.get_event_loop().is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
    # if platform.system() == "Windows":
    #     asyncio.set_event_loop(asyncio.ProactorEventLoop())
    loop = asyncio.get_event_loop()

    for chunk, tasks_in_chunk in enumerate(chunks):
        logging.debug(
            f"Beginning work on chunk {chunk}/{num_chunks}")  # , flush=True)
        commands = asyncio.gather(*tasks_in_chunk)  # Unpack list using *
        results = loop.run_until_complete(commands)
        consolidated_results += results
        logging.debug(
            f"Completed work on chunk {chunk}/{num_chunks}")  # , flush=True)

    loop.close()
    return consolidated_results


def format_table_info(data: Dict) -> str:
    slack_text = f"""
        ```
|{"Table Name":>40}|{"Date":>12}|{"Time":>12}|{"Max Partition":>15}|{"Partition Status":>16}|
|{"":->40}|{"":->12}|{"":->12}|{"":->15}|{"":->16}|"""
    for tbl in data.get("table_info", []):
        if tbl["done_flag"] == "Not Exist":
            done_status = "In Progress/NA"
        else:
            done_status = "Completed"

        slack_text += f"""{os.linesep}|{tbl["table_name"]:>40}|{tbl["update_date"]:>12}|{tbl["update_time"]:>12}|{tbl["max_partition"]:>15}|{done_status:>16}|"""
    slack_text += "```"
    return slack_text


def extract_info_from_results(cmd_results: List[CommandResult]) -> Dict:
    # TODO: convert to __str__
    rtn = {"table_info": []}
    for cmd, rc, output in cmd_results:
        if output is not None and str(output).strip() != '':
            logging.debug(f"cmd={cmd}, rc={rc}, output={output}")
            # print(f"cmd={cmd}, rc={rc}, output={output}")
            if '=' in output:
                # Example output:
                # drwxrwxr-x   - SVMMAHLSTC mmaholac          0
                # 2019-12-10 06:26 hdfs://bigredns/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend/sls_d=2019-12-08
                content, max_partition = str(output).strip().split('=')[:2]
                update_date, update_time, hdfs_path = content.split(' ')[-3:]
                tbl = hdfs_path.split('/')[-2]
                # print(f"table={tbl}, date={content_and_part_val[1]}")
                rtn["table_info"].append({"table_name": tbl,
                                          "update_date": update_date,
                                          "update_time": update_time,
                                          "max_partition": max_partition})
            else:
                logging.warning(f"No partition found in {output}")
        else:
            logging.warning(f"output is empty for {cmd}")

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


# def get_table_location(tables: List[str]) -> Generator:
#     table_name, hdfs_location, load_freq = None, None, None
#     # import re
#     # ddl_location_re = r"CREATE\s+(?:EXTERNAL\s)*TABLE\s+`(\w+.\w+)`.+LOCATION\s*[\n]\s*[']([\w/:.]+)[']"
#     # r".*TBLPROPERTIES.+'LOAD_FREQUENCY'\s*='(\w+)'.+"
#     # ddl_location_freq = DDL_META_PATTERN
#     commands = [f"""hive -e "show create table {tbl};" """ for tbl in tables]
#     ddl_strings = run_asyncio_commands(commands=commands,
#                                        max_concurrent_tasks=min(
#                                            len(tables), 10))
#     # for cmd, rc, ddl in ddl_strings:
#     #     matched = ddl_location_freq.match(ddl)
#     #     if matched:
#     #         # pprint(matched.groups())
#     #         # table_name, hdfs_location, load_freq = matched.groups()
#     #         table_name, hdfs_location = matched.groups()
#     #     else:
#     #         print(f"Not matched! {cmd}")
#     #         logging.warning(f"Not matched! {cmd}")
#     #     yield table_name, hdfs_location
#     return get_ddl_string(ddl_strings)


def get_ddl_commands(tables: List[str]) -> Generator:
    return (f"""hive -e "show create table {tbl};" """ for tbl in tables)


def get_meta_from_ddl_results(cmd_results: List[CommandResult]) -> Generator:
    for cmd, rc, ddl in cmd_results:
        meta = get_meta_from_ddl(ddl=ddl, pattern=DDL_META_PATTERN)
        yield meta.name, meta.location


def get_meta_from_ddl(ddl: str, pattern: Pattern = DDL_META_PATTERN) -> TableMeta:
    # ddl_location_freq = re.compile(ddl_location_re, re.DOTALL | re.MULTILINE)
    matched = pattern.match(ddl)

    table_name, hdfs_location = None, None
    if matched:
        # pprint(matched.groups())
        # table_name, hdfs_location, load_freq = matched.groups()
        table_name, hdfs_location = matched.groups()
    else:
        print(f"Not matched! {ddl}")
        logging.warning(f"Not matched! {ddl}")

    return TableMeta(name=table_name, location=hdfs_location, load_frequency="Daily")


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


def done_commands_from_table(table_list: List[Dict], done_file_mapping: Dict = None) -> List[str]:
    commands = []
    for tbl in table_list:
        table_name = tbl.get("table_name", None)
        if tbl is not None and table_name is not None and tbl.get("max_partition", None) is not None:
            # find done files
            # done_file[tbl["table_name"]] = None
            part = tbl["max_partition"]
            if '-' in part:
                part = part.replace('-', '/')
                # print(f"{part}")
            else:
                matched = re.match(part, '([1-9][0-9]{3})([01][0-9])([0-3][0-9])')
                if matched:
                    logging.warning(f"Partition value format change: {part}")
                    part = '/'.join(matched.groups())
                else:
                    logging.warning(f"Unknown partition value format {part}, SKIP")
            if done_file_mapping is not None and done_file_mapping.get(table_name, None) is not None:
                logging.debug(f"mapping found {table_name} : {done_file_mapping[table_name]}")
                table_name = done_file_mapping[table_name]
            else:
                logging.debug(f"No mappings!!! {done_file_mapping}")
            commands.append(f"""hdfs dfs -ls /common/MMA/data/ready/{DB_NAME}/{part}/{table_name}*""")
        else:
            logging.warning(f"Table name or max partition is None!")
    return commands


def extract_done_flag(done_file_cmd_results: List[CommandResult]) -> DefaultDict:
    # Use defaultdict to avoid missing key exception
    done_file = defaultdict(lambda: "Not Exist")

    for cmd, rc, output in done_file_cmd_results:
        logging.debug(f"Done file checking output: {output}")

        if cmd is not None and cmd.strip() != "" and output is not None and output.strip() != "":
            tbl_name = cmd.split('/')[-1][:-1]
            if "No such file" in output:
                logging.warning(f"Done file not found: {output}")
                done_file[tbl_name] = "Not Exist"
            elif f"{tbl_name}" in output:
                done_file[tbl_name] = output.strip().split('/')[-1]
            else:
                logging.warning(f"Unknown done file command output string {output}")
                done_file[tbl_name] = output.strip()
        else:
            logging.warning(f"No output from {cmd}")
    return done_file


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
    # commands = (
    #     [
    #         "hdfs", "dfs", "-ls",
    #         "/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend"
    #     ],
    #     [
    #         "hdfs", "dfs", "-ls",
    #         "/apps/hive/warehouse/prd_roundel_fnd.db/guest_behavior"
    #     ],
    #     [
    #         "hdfs", "dfs", "-ls",
    #         "/apps/hive/warehouse/prd_roundel_fnd.db/campaign_guest_line_performance"
    #     ],
    #     [
    #         "hdfs", "dfs", "-ls",
    #         "/apps/hive/warehouse/prd_roundel_fnd.db/campaign_line_performance"
    #     ],
    #     [
    #         "hdfs", "dfs", "-ls",
    #         "/apps/hive/warehouse/prd_roundel_fnd.db/campaign_report_performance"
    #     ],
    # )
    # shell_commands = (
    #     "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/guest_spend | tail -1",
    #     "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/guest_behavior | tail -1 ",
    #     "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/campaign_guest_line_performance | tail -1",
    #     "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/campaign_line_performance | tail -1",
    #     "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/campaign_report_performance | tail -1",
    # )

    parser = argparse.ArgumentParser(description='Send Hive table metadata to slack channel')
    parser.add_argument(
        '--slack-webhook',
        type=str,
        required=True,
        dest='slack_webhook',
        help=
        "The slack webhook URL"
    )
    parser.add_argument(
        '--message-header',
        type=str,
        required=False,
        dest='message_header',
        default=f"Latest table information in *{DB_NAME}* {os.linesep}"
        f"Partition Status: _Completed_=Max Partition Loaded, {os.linesep}"
        f"                  _In Progress/NA_=Either Max Partition is being loaded or No Information Available "
        f"(Done flag not created/supported)",
        help=
        "The slack message header added in front of the table information"
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
        "guest_features_item_final": "whitewalker_test_control_final"
    }
    start = time.perf_counter()
    # TODO: Change it to use queues between the two async commands
    ddl_results = run_asyncio_commands(commands=get_ddl_commands(tables=TABLE_LIST),
                                       max_concurrent_tasks=min(
                                           len(TABLE_LIST), 10))

    results = run_asyncio_commands(commands=[
                f"hdfs dfs -ls {data_loc} | tail -1"
                for _, data_loc in get_meta_from_ddl_results(cmd_results=ddl_results) if data_loc is not None
            ],
                                   max_concurrent_tasks=MAX_CONCURRENCY)
    end = time.perf_counter()
    logging.info(f"Asyncio Time Taken: {round(end - start, 4):.4f}")
    print(f"Asyncio Time Taken: {round(end - start, 4):.4f}")

    # Send to Slack
    # pprint(results)
    table_info = extract_info_from_results(cmd_results=results)

    # table_info["table_info"] = add_done_file_info(table_list=table_info["table_info"])
    commands = done_commands_from_table(table_list=table_info["table_info"],
                                        done_file_mapping=done_file_mapping)
    done_file_results = run_asyncio_commands(commands=commands, max_concurrent_tasks=MAX_CONCURRENCY)

    done_file = extract_done_flag(done_file_results)
    for tbl in table_info["table_info"]:
        try:
            tbl["done_flag"] = done_file[done_file_mapping[tbl["table_name"]]]
        except KeyError:
            logging.info(f"""No mapping exists, use the original table name {tbl["table_name"]}""")
            tbl["done_flag"] = done_file[tbl["table_name"]]
        # if done_file_mapping.get(tbl["table_name"], None) is not None:
        #     tbl["done_flag"] = done_file[done_file_mapping[tbl["table_name"]]]
        # else:
        #     tbl["done_flag"] = done_file[tbl["table_name"]]

    # from pprint import pprint
    # pprint(table_info)

    table_info_str = format_table_info(data=table_info)
    status = send_slack(json_data={
        "channel": "datasciences-roundel-ops",
        "text": f"{message_header} {table_info_str}"
    }, webhook=slack_webhook
    )

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
