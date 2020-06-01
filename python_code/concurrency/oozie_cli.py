import os
from typing import List, Dict
import logging
import pytest
from datetime import datetime
import re
from operator import itemgetter

from asyncio_command.command import run_asyncio_commands, CommandResult
from pprint import pprint

# TODO: Change CLI to use APIs

# TODO: Move it to another module/package

OOZIE_URL='http://bigoozie:11000/oozie'

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


def get_coord_jobs(users: List, status: str) -> Dict:
    command_strs = (f"""oozie jobs -oozie {OOZIE_URL} -jobtype coordinator -filter user={u.upper()}\\;status={status.upper()} | grep '{status.upper()}'""" for u in users)
    coord_jobs_output = run_asyncio_commands(commands=command_strs, max_concurrent_tasks=1)
    coord_jobs_list = (parse_jobs_coord(cmd_result=output) for output in coord_jobs_output)
    # Flatten the list of dict into a dict { 'coord_job_id': {} }
    coord_jobs = {k: v for coord in coord_jobs_list for k, v in coord.items()}
    coord_ids = coord_jobs.keys()
    # [id for job_ids in (job.keys() for job in coord_jobs_list) for id in job_ids]

    coord_job_output = run_asyncio_commands(commands=oozie_cli_job_info_command(job_ids=coord_ids), max_concurrent_tasks=10)
    coord_job_list = (parse_coord_last_run(cmd_result=coord_job) for coord_job in coord_job_output)
    coord_details = {k: v for coord in coord_job_list for k, v in coord.items()}

    # wf_id == '-' if WAITING for dependency
    wf_id_list = [v['wf_id'] for v in coord_details.values() if v.get('wf_id', None) is not None and v.get('wf_id', None) != '-']
    if len(wf_id_list) < len(coord_details.keys()):
        coord_id_list = ['@'.join([k, v['run#']]) for k, v in coord_details.items()
                         if v.get('wf_id', None) == '-' and v.get('status', None) == 'WAITING']
        # pprint(coord_id_list)

        if len(coord_id_list) > 0:
            coord_waiting = run_asyncio_commands(commands=oozie_cli_job_info(job_ids=coord_id_list), max_concurrent_tasks=10)
            # TODO:
            coord_waiting_list = (parse_job_waiting(cmd_result=coord) for coord in coord_waiting)
            coord_waiting_details = {k: v for c in coord_waiting_list for k, v in c.items()}
            coord_details = merge_dict(coord_details, coord_waiting_details)

    coord_wf_output = run_asyncio_commands(commands=oozie_cli_job_info_wf(job_ids=wf_id_list), max_concurrent_tasks=10)
    coord_wf_list = (parse_job_wf(cmd_result=coord_wf) for coord_wf in coord_wf_output)
    coord_wf_details = {k: v for wf in coord_wf_list for k, v in wf.items()}

    # merge coord details with wf details (i.e. oozie job <coord_id> and oozie job <wf_id> output results)
    return merge_dict(coord_details, merge_dict(coord_wf_details, coord_jobs))


def get_coord_job_details():
    pass


def format_coord_details(job_details: Dict) -> str:
    job_name_mapping = {
        'SalesForceDataLanding': 'Saleforce Pipeline',
        'guest_sales_daily_load': 'Guest Sales',
        'selfservice_lift': 'Lift SelfService',
        'lift_metrics': 'Lift',
        'guest_features_wf': 'Guest Features and WhiteWalker',
        'guest_behavior_ads': 'Guest Behavior',
        'camp_gst_and_line_perf': 'Campaign Performance Pipeline',
        'global_feat_ads': 'Global Feature Pipeline',
        'selfservice_performance': 'Campaign Performance SelfService',
        'selfservice_performance_gst_cntc_test': 'Perf SelfService GCH Test',
        'daily_batch_performance': 'Campaign Performance',
    }
    slack_text = f"""
|{"Job Name":>32}|{"status":>11}|{"Start Time":>20}|{"Duration":>10}|{"Scheduled Time":>20}|{"Missing Dependency":>20}|
|{"":->32}|{"":->11}|{"":->20}|{"":->10}|{"":->20}|{"":->20}|"""

    # job_by_name = {}
    # for coord_id, coord_detail in job_details.items():
    for coord_detail in sorted(job_details.values(), key=itemgetter('name')):
        coord_name = coord_detail.get('name', coord_detail.get('wf_name', 'unknown'))
        name = job_name_mapping.get(coord_name, coord_name)

        # job_by_name[name] = {
        #     'nominal_time': coord_detail.get('nominal_time', ''),
        #     'status': coord_detail.get('status', 'unknown'),
        #     'start_ts': coord_detail.get('start_ts', ''),
        #     'end_ts': coord_detail.get('end_ts', ''),
        #     'modify_ts': coord_detail.get('start_ts', ''),
        #     'missing_dependency': coord_detail.get('missing_dependency', ''),
        #     'run_seq': coord_detail.get('run_seq', ''),
        # }
        duration = ''
        if coord_detail.get("modify_ts", "").strip() != "" or coord_detail.get("end_ts", "").strip() != "":
            try:
                start_time = oozie_str2datetime(coord_detail['start_ts'])
                end_time = coord_detail.get('modify_ts', None)
                if end_time is None:
                    end_time = coord_detail['end_ts']
                duration = oozie_str2datetime(datetime_str=end_time) - start_time
            except ValueError as e:
                logging.warning(f"Start or end/modify Time not found {e} - {coord_detail}")
            except TypeError as e:
                logging.warning(f"Start or end/modify Time not found {e} - {coord_detail}")
            except KeyError as e:
                start_time = ''
                logging.warning(f"Start or end/modify Time not found {e} - {coord_detail}")

        slack_text += f"""{os.linesep}|{name:>32}|{coord_detail.get("status", "unknown"):>11}|{coord_detail.get("start_ts", ""):>20}|{str(duration):>10}|{coord_detail.get("nominal_time", ""):>20}|{coord_detail.get("missing_dependency", ""):>20}|"""
    # slack_text += "```"
    return slack_text


# def oozie_cli_coord_jobs_command(user: str = 'SVMMAHLSTC', status: str = 'RUNNING'):
#     return f"""oozie jobs -jobtype coordinator -filter user={user.upper()}\\;status={status.upper()} | grep '{status.upper()}'"""
#
#
def oozie_cli_job_info_command(job_ids: List):
    return (f"""oozie job -oozie {OOZIE_URL} -info {job_id} | grep oozie | tail -1""" for job_id in job_ids)


def oozie_cli_job_info_wf(job_ids: List):
    return (f"""oozie job -oozie {OOZIE_URL} -info {job_id} | head -16""" for job_id in job_ids)


def oozie_cli_job_info(job_ids: List) -> str:
    return (f"""oozie job -oozie {OOZIE_URL} -info {job_id}""" for job_id in job_ids)


def oozie_str2datetime(datetime_str: str, format_str: str = '%Y-%m-%d %H:%M %Z'):
    return datetime.strptime(datetime_str, format_str)


def parse_job_waiting(cmd_result: CommandResult) -> Dict:
    # SVMMAHLSTC@brdn1176:slack_notice $ oozie job -info 0124845-191021133335811-oozie-oozi-C@87
    # ID : 0124845-191021133335811-oozie-oozi-C@87
    # ------------------------------------------------------------------------------------------------------------------------------------
    # Action Number        : 87
    # Console URL          : -
    # Error Code           : -
    # Error Message        : -
    # External ID          : -
    # External Status      : -
    # Job ID               : 0124845-191021133335811-oozie-oozi-C
    # Tracker URI          : -
    # Created              : 2020-01-31 15:55 GMT
    # Nominal Time         : 2020-01-31 16:00 GMT
    # Status               : WAITING
    # Last Modified        : 2020-01-31 18:00 GMT
    # First Missing Dependency : hdfs://bigredns/apps/hive/warehouse/prd_roundel_stg.db/dfa_data_poc/filedate_pst=20200129/
    # ------------------------------------------------------------------------------------------------------------------------------------
    coord_header_pattern = re.compile(r".*ID\s*:\s*([\w-]+)@(\d+).*"
                                   r"Created\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"Nominal Time\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"Status\s+?:\s*?([\w-]+).*"
                                   r"Last Modified\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"First Missing Dependency\s*:\s*([\w:/\.=-]*)",
                                   re.DOTALL | re.MULTILINE)
    coord_info = {}
    if cmd_result is not None and cmd_result.output is not None and str(cmd_result.output).strip() != '':
        try:
            matched = coord_header_pattern.match(cmd_result.output)
        except TypeError as e:
            print(f"Error {e}")
        if matched:
            logging.debug(f"{matched.groups()}")
            coord_id, coord_seq, create_ts, nominal_ts, status, modify_ts, missing_dep = matched.groups()
            coord_info = {
                coord_id: {
                    'run_seq': coord_seq,
                    'status': status,
                    'create_ts': create_ts,
                    'modify_ts': modify_ts,
                    'nominal_time': nominal_ts,
                    'missing_dependency': missing_dep,
                }
            }
        else:
            print(f"not matched!")
            logging.warning(f"Coord Information NOT extracted {cmd_result.output}")
    return coord_info


def parse_job_wf(cmd_result: CommandResult) -> Dict:
    # Job ID : 0905354-191021133335811-oozie-oozi-W
    # ------------------------------------------------------------------------------------------------------------------------------------
    # Workflow Name : global_feat_ads-wf
    # App Path      : hdfs://bigredns/common/MMA/source/holistic/oozie/global_feat_ads/coordinator/workflow/workflow.xml
    # Status        : SUCCEEDED
    # Run           : 0
    # User          : SVMMAHLSTC
    # Group         : -
    # Created       : 2020-01-30 15:45 GMT
    # Started       : 2020-01-30 15:45 GMT
    # Last Modified : 2020-01-30 15:52 GMT
    # Ended         : 2020-01-30 15:52 GMT
    # CoordAction ID: 3564699-180612065206168-oozie-oozi-C@142

    # wf_header_pattern = re.compile(r"Job ID\s*?:\s*?(\w*).*Workflow Name\s*?:\s*?(\w+).+Status\s+?:\s*?(\w+).*Run\s+?:\s+?(\d+).+Created\s+?:\s+?([\d-:\s]+\w*?)?.*Started\s+?:\s+?([\d-:\s]+[\w*]).*Last Modified[\s+]:[\s+]([\d-:\s]*[\w*]).*Ended[\s+]:[\s+]([\d-:\s]*[\w*]).*CoordAction ID:[\s*]([\w*][@][\d*])",
    #                                re.DOTALL | re.MULTILINE)

    wf_header_pattern = re.compile(r".*Job ID[\s]*:[\s]*([\w-]+).*"
                                   r"Workflow Name\s*?:\s*?([\w-]+).+"
                                   r"Status\s+?:\s*?([\w-]+).*Run\s+?:\s+?(\d+).*"
                                   r"Created\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"Started\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"Last Modified\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"Ended\s+:\s*([\d-]+\s[\d:]+\s*\w+)?.*"
                                   r"CoordAction ID:\s*([\w-]*)?@?(\d*)?",
                                   re.DOTALL | re.MULTILINE)
    wf_info = {}
    if cmd_result is not None and cmd_result.output is not None and str(cmd_result.output).strip() != '':
        try:
            matched = wf_header_pattern.match(cmd_result.output)
        except TypeError as e:
            print(f"Error {e}")
        if matched:
            # print(f"{matched.groups()}")
            logging.debug(f"{matched.groups()}")
            job_id, wf_name, status, run_seq, create_ts, start_ts, modify_ts, end_ts, coord_id, coord_seq = matched.groups()
            if coord_id is None or str(coord_id).strip() == '':
                coord_id = job_id
            wf_info = {
                coord_id: {
                    'wf_id': job_id,
                    'run_seq': coord_seq,
                    'wf_name': wf_name,
                    'status' : status,
                    'create_ts': create_ts,
                    'start_ts': start_ts,
                    'modify_ts': modify_ts,
                    'end_ts': end_ts,
                }
            }
        else:
            print(f"not matched!")
            logging.warning(f"WF Information NOT extracted {cmd_result.output}")
    return wf_info


def parse_jobs_coord(cmd_result: CommandResult) -> Dict:
    coord_info = {}
    if cmd_result is not None and cmd_result.output is not None and str(cmd_result.output).strip() != '':
        for coord in str(cmd_result.output).split(os.linesep):
            coord_part = coord.split()
            coord_name = coord_part[1]
            if len(coord_part) > 9:
                if coord_part[2] != 'RUNNING' and coord_part[1][-7:] == 'RUNNING':
                # e.g. 0720898-191021133539902-oozie-oozi-C     SalesForceDataLandingRUNNING   1    DAY          2020-01-22 07:00 GMT    2020-01-29 07:00 GMT
                    coord_part.insert(2, coord_name[-7:])
                    coord_part[1] = coord_name[:-7]
                if len(coord_part) != 11:
                    # raise ValueError(f"Expected 10 components from the oozie jobs command, got {coord} {coord_part}")
                    logging.error(f"Expected 10 components from the oozie jobs command, got {coord} {coord_part}")
                else:
                    coord_info[coord_part[0]] = {"name": coord_part[1]}
            else:
                logging.warning(f"Expect at least 10 fields from oozie jobs command, got {len(coord_part)}")
    else:
        logging.warning(f"Command result is none or output is empty {cmd_result}")
    return coord_info


def parse_coord_last_run(cmd_result: CommandResult) -> Dict:
    coord_info = {}
    if cmd_result is not None and cmd_result.output is not None and str(cmd_result.output).strip() != '':
        part = str(cmd_result.output).split()
        coord_id, coord_seq = part[0].split('@')
        coord_info = {
            coord_id: {
                "run#": coord_seq,
                "status": part[1],
                "wf_id": part[2],
                "create_date": part[4],
                "nominal_time": ' '.join(part[-3:])
            }
        }
    return coord_info


@pytest.mark.parametrize("data, expected", [
    ({'0124845-191021133335811-oozie-oozi-C': {'create_date': '2020-01-31',
                                          'create_ts': '2020-01-31 20:58 GMT',
                                          'end_ts': '2020-01-31 22:29 GMT',
                                          'modify_ts': '2020-01-31 22:29 GMT',
                                          'name': 'camp_gst_and_line_perf',
                                          'nominal_time': '2020-01-31 16:00 '
                                                          'GMT',
                                          'run#': '87',
                                          'run_seq': '87',
                                          'start_ts': '2020-01-31 20:58 GMT',
                                          'status': 'SUCCEEDED',
                                          'wf_id': '0915351-191021133335811-oozie-oozi-W',
                                          'wf_name': 'camp_gst_and_line_perf-wf'},
 '0207489-191021133335811-oozie-oozi-C': {'create_date': '2020-02-01',
                                          'create_ts': '2020-02-01 10:45 GMT',
                                          'end_ts': '2020-02-01 11:01 GMT',
                                          'modify_ts': '2020-02-01 11:01 GMT',
                                          'name': 'guest_behavior_ads',
                                          'nominal_time': '2020-02-01 10:45 '
                                                          'GMT',
                                          'run#': '83',
                                          'run_seq': '83',
                                          'start_ts': '2020-02-01 10:45 GMT',
                                          'status': 'SUCCEEDED',
                                          'wf_id': '0813162-191021133539902-oozie-oozi-W',
                                          'wf_name': 'guest_behavior_ads-wf'},
 '0251605-191021133335811-oozie-oozi-C': {'create_date': '2020-01-27',
                                          'create_ts': '2020-01-27 18:05 GMT',
                                          'end_ts': '2020-01-27 22:01 GMT',
                                          'modify_ts': '2020-01-27 22:01 GMT',
                                          'name': 'guest_features_wf',
                                          'nominal_time': '2020-01-27 08:10 '
                                                          'GMT',
                                          'run#': '12',
                                          'run_seq': '12',
                                          'start_ts': '2020-01-27 18:05 GMT',
                                          'status': 'SUCCEEDED',
                                          'wf_id': '0878021-191021133335811-oozie-oozi-W',
                                          'wf_name': 'guest_features_wf-wf'},
 '0296326-191021133335811-oozie-oozi-C': {'create_date': '2020-01-26',
                                          'create_ts': '2020-01-26 20:10 GMT',
                                          'end_ts': '2020-01-26 20:20 GMT',
                                          'modify_ts': '2020-01-26 20:20 GMT',
                                          'name': 'lift_metrics',
                                          'nominal_time': '2020-01-26 20:10 '
                                                          'GMT',
                                          'run#': '10',
                                          'run_seq': '10',
                                          'start_ts': '2020-01-26 20:10 GMT',
                                          'status': 'SUCCEEDED',
                                          'wf_id': '0765103-191021133539902-oozie-oozi-W',
                                          'wf_name': 'lift_metrics-wf'},
 '0449756-191021133539902-oozie-oozi-C': {'create_date': '2020-02-01',
                                          'create_ts': '2020-02-01 07:12 GMT',
                                          'end_ts': '2020-02-01 10:23 GMT',
                                          'modify_ts': '2020-02-01 10:23 GMT',
                                          'name': 'selfservice_lift',
                                          'nominal_time': '2020-02-01 07:00 '
                                                          'GMT',
                                          'run#': '44',
                                          'run_seq': '44',
                                          'start_ts': '2020-02-01 07:12 GMT',
                                          'status': 'SUCCEEDED',
                                          'wf_id': '0919006-191021133335811-oozie-oozi-W',
                                          'wf_name': 'selfservice_lift-wf'},
      '0661230-191021133539902-oozie-oozi-C': {'create_date': '2020-02-01',
                                               'create_ts': '2020-02-01 11:01 GMT',
                                               'end_ts': '2020-02-01 12:01 GMT',
                                               'modify_ts': '2020-02-01 12:01 GMT',
                                               'name': 'guest_sales_daily_load',
                                               'nominal_time': '2020-02-01 11:00 '
                                                               'GMT',
                                               'run#': '19',
                                               'run_seq': '19',
                                               'start_ts': '2020-02-01 11:01 GMT',
                                               'status': 'SUCCEEDED',
                                               'wf_id': '0813300-191021133539902-oozie-oozi-W',
                                               'wf_name': 'guest_sales_daily_load-wf'},
      '0720898-191021133539902-oozie-oozi-C': {'create_date': '2020-02-01',
                                               'create_ts': '2020-02-01 07:00 GMT',
                                               'end_ts': '2020-02-01 07:11 GMT',
                                               'modify_ts': '2020-02-01 07:11 GMT',
                                               'name': 'SalesForceDataLanding',
                                               'nominal_time': '2020-02-01 07:00 '
                                                               'GMT',
                                               'run#': '11',
                                               'run_seq': '11',
                                               'start_ts': '2020-02-01 07:00 GMT',
                                               'status': 'SUCCEEDED',
                                               'wf_id': '0918872-191021133335811-oozie-oozi-W',
                                               'wf_name': 'SalesForceDataLanding-wf'},
      '3564699-180612065206168-oozie-oozi-C': {'create_date': '2020-01-31',
                                               'create_ts': '2020-01-31 18:01 GMT',
                                               'end_ts': '2020-01-31 18:06 GMT',
                                               'modify_ts': '2020-01-31 18:06 GMT',
                                               'name': 'global_feat_ads',
                                               'nominal_time': '2020-01-31 18:01 '
                                                               'GMT',
                                               'run#': '145',
                                               'run_seq': '145',
                                               'start_ts': '2020-01-31 18:01 GMT',
                                               'status': 'SUCCEEDED',
                                               'wf_id': '0807121-191021133539902-oozie-oozi-W',
                                               'wf_name': 'global_feat_ads-wf'}}
     , """
            ```
|                                Job Name|     status|          Start Time|  Duration|      Scheduled Time|  Missing Dependency|
|----------------------------------------|-----------|--------------------|----------|--------------------|--------------------|
|                      Saleforce Pipeline|  SUCCEEDED|2020-02-01 07:00 GMT|   0:11:00|2020-02-01 07:00 GMT|                    |
|           Campaign Performance Pipeline|  SUCCEEDED|2020-01-31 20:58 GMT|   1:31:00|2020-01-31 16:00 GMT|                    |
|                 Global Feature Pipeline|  SUCCEEDED|2020-01-31 18:01 GMT|   0:05:00|2020-01-31 18:01 GMT|                    |
|                          Guest Behavior|  SUCCEEDED|2020-02-01 10:45 GMT|   0:16:00|2020-02-01 10:45 GMT|                    |
|          Guest Features and WhiteWalker|  SUCCEEDED|2020-01-27 18:05 GMT|   3:56:00|2020-01-27 08:10 GMT|                    |
|                             Guest Sales|  SUCCEEDED|2020-02-01 11:01 GMT|   1:00:00|2020-02-01 11:00 GMT|                    |
|                                    Lift|  SUCCEEDED|2020-01-26 20:10 GMT|   0:10:00|2020-01-26 20:10 GMT|                    |
|                        Lift SelfService|  SUCCEEDED|2020-02-01 07:12 GMT|   3:11:00|2020-02-01 07:00 GMT|                    |```"""),
])
def test_format_coord_details(data, expected):
    rtn = format_coord_details(job_details=data)
    # print(rtn)
    assert rtn == expected


@pytest.mark.parametrize("cmd_result, expected",
                         [
                             (CommandResult(cmd='', returncode=0, output="""
    ID : 0124845-191021133335811-oozie-oozi-C@87
    ------------------------------------------------------------------------------------------------------------------------------------
    Action Number        : 87
    Console URL          : -
    Error Code           : -
    Error Message        : -
    External ID          : -
    External Status      : -
    Job ID               : 0124845-191021133335811-oozie-oozi-C
    Tracker URI          : -
    Created              : 2020-01-31 15:55 GMT
    Nominal Time         : 2020-01-31 16:00 GMT
    Status               : WAITING
    Last Modified        : 2020-01-31 18:00 GMT
    First Missing Dependency : hdfs://bigredns/apps/hive/warehouse/prd_roundel_stg.db/dfa_data_poc/filedate_pst=20200129/
    ------------------------------------------------------------------------------------------------------------------------------------
                             """),
                            {'0124845-191021133335811-oozie-oozi-C':
                                 {'run_seq': '87',
                                  'status': 'WAITING',
                                  'create_ts': '2020-01-31 15:55 GMT',
                                  'modify_ts': '2020-01-31 18:00 GMT',
                                  'nominal_time': '2020-01-31 16:00 GMT',
                                  'missing_dependency': 'hdfs://bigredns/apps/hive/warehouse/prd_roundel_stg.db/dfa_data_poc/filedate_pst=20200129/'
                                  }
                             }

                              ),
])
def test_parse_job_waiting(cmd_result, expected):
    rtn = parse_job_waiting(cmd_result=cmd_result)
    # from pprint import pprint
    # print(rtn)
    assert rtn == expected


@pytest.mark.parametrize("cmd_result, expected",
                         [
                             (CommandResult(cmd='', returncode=0, output="""
    Job ID : 0905354-191021133335811-oozie-oozi-W
    ------------------------------------------------------------------------------------------------------------------------------------
    Workflow Name : global_feat_ads-wf
    App Path      : hdfs://bigredns/common/MMA/source/holistic/oozie/global_feat_ads/coordinator/workflow/workflow.xml
    Status        : SUCCEEDED
    Run           : 0
    User          : SVMMAHLSTC
    Group         : -
    Created       : 2020-01-30 15:45 GMT
    Started       : 2020-01-30 15:45 GMT
    Last Modified : 2020-01-30 15:52 GMT
    Ended         : 2020-01-30 15:52 GMT
    CoordAction ID: 3564699-180612065206168-oozie-oozi-C@142
"""),
                              {'3564699-180612065206168-oozie-oozi-C':
                                   {
                                        'create_ts': '2020-01-30 15:45 GMT',
                                        'end_ts': '2020-01-30 15:52 GMT',
                                        'modify_ts': '2020-01-30 15:52 GMT',
                                        'run_seq': '142',
                                        'start_ts': '2020-01-30 15:45 GMT',
                                        'status': 'SUCCEEDED',
                                        'wf_id': '0905354-191021133335811-oozie-oozi-W',
                                        'wf_name': 'global_feat_ads-wf',
                                  }
                              }
                                                  ),
                             (CommandResult(cmd='', returncode=0, output="""
    Job ID : 0905354-191021133335811-oozie-oozi-W
    ------------------------------------------------------------------------------------------------------------------------------------
    Workflow Name : global_feat_ads-wf
    App Path      : hdfs://bigredns/common/MMA/source/holistic/oozie/global_feat_ads/coordinator/workflow/workflow.xml
    Status        : RUNNING
    Run           : 0
    User          : SVMMAHLSTC
    Group         : -
    Created       : 2020-01-30 15:45 GMT
    Started       : 2020-01-30 15:45 GMT
    Last Modified : 2020-01-30 15:52 GMT
    Ended         : -
    CoordAction ID:
"""),
                              {'0905354-191021133335811-oozie-oozi-W':
                                   {
                                        'create_ts': '2020-01-30 15:45 GMT',
                                        'end_ts': None,
                                        'modify_ts': '2020-01-30 15:52 GMT',
                                        'run_seq': '',
                                        'start_ts': '2020-01-30 15:45 GMT',
                                        'status': 'RUNNING',
                                        'wf_id': '0905354-191021133335811-oozie-oozi-W',
                                        'wf_name': 'global_feat_ads-wf',
                                  }
                              }
                                                  ),
                         ])
def test_parse_job_wf(cmd_result, expected):
    rtn = parse_job_wf(cmd_result)
    assert rtn == expected


@pytest.mark.parametrize("datetime_str, format_str, expected",
[
    ('2020-01-29 17:58 GMT', '%Y-%m-%d %H:%M %Z', datetime(2020, 1, 29, 17, 58)),
    ('2020-01-29 10:00 GMT', '%Y-%m-%d %H:%M %Z', datetime(2020, 1, 29, 10, 00)),
    ('2020-01-29 10:00 CST', '%Y-%m-%d %H:%M %Z', datetime(2020, 1, 29, 10, 00)),
]
                         )
def test_oozie_str2datetime(datetime_str, format_str, expected):
    rtn = oozie_str2datetime(datetime_str=datetime_str, format_str=format_str)
    assert rtn == expected


@pytest.mark.parametrize("cmd_result, expected",
                         [
                             (CommandResult(cmd='', returncode=0,
                                            output='0661230-191021133539902-oozie-oozi-C@16    RUNNING   0897694-191021133335811-oozie-oozi-W -         2020-01-29 10:59 GMT 2020-01-29 11:00 GMT'),
                              {
                                  '0661230-191021133539902-oozie-oozi-C': {
                                      "run#": '16',
                                      "status": 'RUNNING',
                                      "wf_id": '0897694-191021133335811-oozie-oozi-W',
                                      "create_date": '2020-01-29',
                                      "nominal_time": '2020-01-29 11:00 GMT'
                                  }
                               }),
                         ])
def test_parse_last_coord_info(cmd_result, expected):
    rtn = parse_coord_last_run(cmd_result=cmd_result)
    assert rtn == expected


@pytest.mark.parametrize("cmd_result, expected",
                         [
                             (CommandResult(cmd='', returncode=0,
                                            output='0720898-191021133539902-oozie-oozi-C     SalesForceDataLanding RUNNING   1    DAY          2020-01-22 07:00 GMT    2020-01-29 07:00 GMT'),
                              {'0720898-191021133539902-oozie-oozi-C': {"name": 'SalesForceDataLanding'}}),
                             (CommandResult(cmd='', returncode=0,
                                            output='0720898-191021133539902-oozie-oozi-C     SalesForceDataLandingRUNNING   1    DAY          2020-01-22 07:00 GMT    2020-01-29 07:00 GMT'),
                              {'0720898-191021133539902-oozie-oozi-C': {"name": 'SalesForceDataLanding'}})
                         ])
def test_parse_jobs_coord(cmd_result, expected):
    rtn = parse_jobs_coord(cmd_result=cmd_result)
    assert rtn == expected


def main():
    jobs = get_coord_jobs(users=['SVMMAHLSTC'], status='RUNNING')
    # from pprint import pprint
    pprint(jobs)


if __name__ == "__main__":
    main()