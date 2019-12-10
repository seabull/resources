# import sys
import time
import platform
import asyncio
import subprocess
from collections import namedtuple
import requests
import json

from pprint import pprint
import logging
import os
from typing import List, Dict

CommandResult = namedtuple("CommandResult", "cmd returncode output")


async def run_command(*args) -> CommandResult:
    """Run command in subprocess.

    Example from:
        http://asyncio.readthedocs.io/en/latest/subprocess.html
    """
    # Create subprocess
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    logging.info(f"Started: {args}, pid={process.pid}")   # , flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        logging.info(f"Done: {args}, pid={process.pid}, result: {stdout.decode().strip()}")   # , flush=True)
        result = CommandResult(cmd=str(args), returncode=process.returncode, output=stdout.decode().strip())
    else:
        logging.error(f"Failed: {args}, pid={process.pid}, result: {stderr.decode().strip()}")   # , flush=True)
        result = CommandResult(cmd=str(args), returncode=process.returncode, output=stderr.decode().strip())

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
    process = await asyncio.create_subprocess_shell(command,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE)

    # Status
    logging.info(f"Started:{command}, (pid = {str(process.pid)})")   # , flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        logging.info(f"Done:{command}, pid = {str(process.pid)}")   # , flush=True)
        result = CommandResult(cmd=command, returncode=process.returncode, output=stdout.decode().strip())
    else:
        logging.error(f"Failed:{command}, pid = {str(process.pid)}")   # , flush=True)
        result = CommandResult(cmd=command, returncode=process.returncode, output=stderr.decode().strip())

    # Result
    # result = stdout.decode().strip()

    # Return stdout
    return result


def run_command_shell_sync(command):
    completed_process = subprocess.run(command, capture_output=True, shell=True)
    if completed_process.returncode == 0:
        result = CommandResult(cmd=command, returncode=completed_process.returncode, output=completed_process.stdout)
    else:
        result = CommandResult(cmd=command, returncode=completed_process.returncode, output=completed_process.stderr)

    return result


def make_chunks(l, n):
    """Yield successive n-sized chunks from l.

    Note:
        Taken from https://stackoverflow.com/a/312464
    """
    # Assume Python 3
    for i in range(0, len(l), n):
        yield l[i : i + n]


def run_asyncio_commands(commands: List[str], max_concurrent_tasks: int=0) -> List[CommandResult]:
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
        chunks = make_chunks(l=tasks, n=max_concurrent_tasks)
        num_chunks = len(list(make_chunks(l=tasks, n=max_concurrent_tasks)))

    if asyncio.get_event_loop().is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
    # if platform.system() == "Windows":
    #     asyncio.set_event_loop(asyncio.ProactorEventLoop())
    loop = asyncio.get_event_loop()

    for chunk, tasks_in_chunk in enumerate(chunks):
        logging.debug(f"Beginning work on chunk {chunk}/{num_chunks}")   # , flush=True)
        commands = asyncio.gather(*tasks_in_chunk)  # Unpack list using *
        results = loop.run_until_complete(commands)
        consolidated_results += results
        logging.debug(f"Completed work on chunk {chunk}/{num_chunks}")   # , flush=True)

    loop.close()
    return consolidated_results


def run_commands(commands):
    return [run_command_shell_sync(cmd) for cmd in commands]


def get_info() -> None:
    commands = (
        ["hdfs", "dfs", "-ls", "/apps/hive/warehouse/prd_roundel_fnd.db/guest_spend"],
        ["hdfs", "dfs", "-ls", "/apps/hive/warehouse/prd_roundel_fnd.db/guest_behavior"],
        ["hdfs", "dfs", "-ls", "/apps/hive/warehouse/prd_roundel_fnd.db/campaign_guest_line_performance"],
        ["hdfs", "dfs", "-ls", "/apps/hive/warehouse/prd_roundel_fnd.db/campaign_line_performance"],
        ["hdfs", "dfs", "-ls", "/apps/hive/warehouse/prd_roundel_fnd.db/campaign_report_performance"],
    )
    shell_commands = (
        "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/guest_spend | tail -1",
        "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/guest_behavior | tail -1 ",
        "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/campaign_guest_line_performance | tail -1",
        "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/campaign_line_performance | tail -1",
        "hdfs dfs -ls /apps/hive/warehouse/prd_roundel_fnd.db/campaign_report_performance | tail -1",
    )
    start = time.perf_counter()
    results = run_asyncio_commands([
        f"hdfs dfs -ls {data_loc} | tail -1" for _, data_loc in get_table_location(get_tables("prd_roundel_fnd"))
    ], max_concurrent_tasks=5)
    end = time.perf_counter()
    logging.info(f"Asyncio Time Taken: {round(end - start, 4):.4f}")
    print(f"Asyncio Time Taken: {round(end - start, 4):.4f}")

    # Send to Slack
    pprint(results)

    # start = time.perf_counter()
    # results_sync = run_commands(shell_commands)
    # end = time.perf_counter()
    # # pprint(results_sync)
    # logging.info(f"synch Time Taken: {round(end - start, 4):.4f}")
    # print(f"Synch Time Taken: {round(end - start, 4):.4f}")


def command_results_to_json(cmd_results: List[CommandResult]) -> str:
    # TODO: convert to __str__
    for cmd, rc, output in cmd_results:
        if str(output).strip() == '':
            # skip
            pass


def get_tables(dbname: str):
            # """hive -e "use {dbname}; show tables;" """)
    completed_process = subprocess.run(f"""
        hive -e "use {dbname}; show tables;"
        """, capture_output=True, shell=True)
    if completed_process.returncode == 0:
        result = completed_process.stdout.decode().strip().split(os.linesep)
    else:
        logging.error(f"ERROR getting tables {completed_process}")
        result = []

    return (f"{dbname}.{tbl}" for tbl in result)


def get_table_location(tables: List[str]):
    table_name, hdfs_location, load_freq = None, None, None
    import re
    ddl_location_re = r"CREATE\s+[EXTERNAL]\s+TABLE\s+`(\w+.\w+)`.+LOCATION\s*[\n]\s*[']([\w/:.]+)[']"
                      # r".*TBLPROPERTIES.+'LOAD_FREQUENCY'\s*='(\w+)'.+"
    ddl_location_freq = re.compile(ddl_location_re, re.DOTALL | re.MULTILINE)
    commands = [f"""hive -e "show create table {tbl};" """ for tbl in tables]
    ddl_strings = run_asyncio_commands(commands=commands, max_concurrent_tasks=min(len(tables), 10))
    for cmd, rc, ddl in ddl_strings:
        matched = ddl_location_freq.match(ddl)
        if matched:
            # pprint(matched.groups())
            # table_name, hdfs_location, load_freq = matched.groups()
            table_name, hdfs_location = matched.groups()
        else:
            print("Not matched!")
        yield table_name, hdfs_location


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


def run_asyncio_tasks(tasks, max_concurrent_tasks=0):
    """Run tasks asynchronously using asyncio and return results.

    If max_concurrent_tasks are set to 0, no limit is applied.

    Note:
        By default, Windows uses SelectorEventLoop, which does not support
        subprocesses. Therefore ProactorEventLoop is used on Windows.
        https://docs.python.org/3/library/asyncio-eventloops.html#windows
    """
    consolidated_results = []

    if max_concurrent_tasks == 0:
        chunks = [tasks]
        num_chunks = len(chunks)
    else:
        chunks = make_chunks(l=tasks, n=max_concurrent_tasks)
        num_chunks = len(list(make_chunks(l=tasks, n=max_concurrent_tasks)))

    if asyncio.get_event_loop().is_closed():
        asyncio.set_event_loop(asyncio.new_event_loop())
    # if platform.system() == "Windows":
    #     asyncio.set_event_loop(asyncio.ProactorEventLoop())
    loop = asyncio.get_event_loop()

    for chunk, tasks_in_chunk in enumerate(chunks):
        print(f"Beginning work on chunk {chunk}/{num_chunks}", flush=True)
        commands = asyncio.gather(*tasks_in_chunk)  # Unpack list using *
        results = loop.run_until_complete(commands)
        consolidated_results += results
        print(f"Completed work on chunk {chunk}/{num_chunks}", flush=True)

    loop.close()
    return consolidated_results


def main():
    start = time.time()

    if platform.system() == "Windows":
        # Commands to be executed on Windows
        commands = [["hostname"]]
    else:
        # Commands to be executed on Unix
        commands = [["du", "-sh", "/var/tmp"], ["hostname"]]

    tasks = []
    for command in commands:
        tasks.append(run_command(*command))

    # # Shell execution example
    # tasks = [run_command_shell('copy c:/somefile d:/new_file')]
    tasks.append(run_command_shell('ls -lrt | tail -1' ))

    # # List comprehension example
    # tasks = [
    #     run_command(*command, get_project_path(project))
    #     for project in accessible_projects(all_projects)
    # ]

    results = run_asyncio_commands(
        tasks, max_concurrent_tasks=20
    )  # At most 20 parallel tasks
    print("Results:")
    pprint(results)

    end = time.time()
    rounded_end = f"{round(end - start, 4):.4f}"
    print(f"Script ran in about {rounded_end} seconds", flush=True)


if __name__ == "__main__":
    # main()
    get_info()
