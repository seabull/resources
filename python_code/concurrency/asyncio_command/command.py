import logging
import asyncio
from typing import List
from collections import namedtuple

CommandResult = namedtuple("CommandResult", "cmd returncode output")

# async def run_command(*args) -> CommandResult:
#     """Run command in subprocess.
#
#     Example from:
#         http://asyncio.readthedocs.io/en/latest/subprocess.html
#     """
#     # Create subprocess
#     process = await asyncio.create_subprocess_exec(
#         *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
#
#     logging.info(f"Started: {args}, pid={process.pid}")  # , flush=True)
#
#     # Wait for the subprocess to finish
#     stdout, stderr = await process.communicate()
#
#     # Progress
#     if process.returncode == 0:
#         logging.info(
#             f"Done: {args}, pid={process.pid}, result: {stdout.decode().strip()}"
#         )  # , flush=True)
#         result = CommandResult(cmd=str(args),
#                                returncode=process.returncode,
#                                output=stdout.decode().strip())
#     else:
#         logging.error(
#             f"Failed: {args}, pid={process.pid}, result: {stderr.decode().strip()}"
#         )  # , flush=True)
#         result = CommandResult(cmd=str(args),
#                                returncode=process.returncode,
#                                output=stderr.decode().strip())
#
#     # Result
#     # result = stdout.decode().strip()
#
#     # Return stdout
#     return result


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
        logging.info(
            f"Done:{command}, pid = {str(process.pid)}")  # , flush=True)
        result = CommandResult(cmd=command,
                               returncode=process.returncode,
                               output=stdout.decode().strip())
    else:
        logging.error(
            f"Failed:{command}, pid = {str(process.pid)}")  # , flush=True)
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
