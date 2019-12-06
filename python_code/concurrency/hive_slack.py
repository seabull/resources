# import sys
import time
import platform
import asyncio
import subprocess
from pprint import pprint
import logging


async def run_command(*args):
    """Run command in subprocess.

    Example from:
        http://asyncio.readthedocs.io/en/latest/subprocess.html
    """
    # Create subprocess
    process = await asyncio.create_subprocess_exec(*args,
                                                   stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE)

    logging.info(f"Started: {args}, pid={process.pid}", flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        logging.info(f"Done: {args}, pid={process.pid}, result: {stdout.decode().strip()}", flush=True)
    else:
        logging.error(f"Failed: {args}, pid={process.pid}, result: {stderr.decode().strip()}", flush=True)

    # Result
    result = stdout.decode().strip()

    # Return stdout
    return result


async def run_command_shell(command):
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
    logging.info(f"Started:{command}, (pid = {str(process.pid)})", flush=True)

    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()

    # Progress
    if process.returncode == 0:
        logging.info(f"Done:{command}, pid = {str(process.pid)}", flush=True)
    else:
        logging.error(f"Failed:{command}, pid = {str(process.pid)}", flush=True)

    # Result
    result = stdout.decode().strip()

    # Return stdout
    return result


def run_command_shell_sync(command):
    completed_process = subprocess.run(command, capture_output=True, shell=True)
    if completed_process.returncode == 0:
        result = completed_process.stdout
    else:
        result = completed_process.stderr

    return result


def make_chunks(l, n):
    """Yield successive n-sized chunks from l.

    Note:
        Taken from https://stackoverflow.com/a/312464
    """
    # Assume Python 3
    for i in range(0, len(l), n):
        yield l[i : i + n]

def run_asyncio_commands(commands, max_concurrent_tasks=0):
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
        logging.debug(f"Beginning work on chunk {chunk}/{num_chunks}", flush=True)
        commands = asyncio.gather(*tasks_in_chunk)  # Unpack list using *
        results = loop.run_until_complete(commands)
        consolidated_results += results
        logging.debug(f"Completed work on chunk {chunk}/{num_chunks}", flush=True)

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
    results = run_asyncio_commands(shell_commands, max_concurrent_tasks=5)
    end = time.perf_counter()
    # pprint(results)
    logging.info(f"Asyncio Time Taken: {round(end - start, 4):.4f}")
    print(f"Asyncio Time Taken: {round(end - start, 4):.4f}")

    start = time.perf_counter()
    results_sync = run_commands(shell_commands)
    end = time.perf_counter()
    # pprint(results_sync)
    logging.info(f"synch Time Taken: {round(end - start, 4):.4f}")
    print(f"Synch Time Taken: {round(end - start, 4):.4f}")


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
