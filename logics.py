import os 
import logging
from datetime import date

import requests
import pandas as pd 
from urllib3 import disable_warnings

from commen import HSDError
from settings import static
from settings import proxies
from settings import headers
from settings import DEVELOPER
from log_handler import handler

disable_warnings()
logger = logging.getLogger('logics')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def send_warning_to_dev(class_name:str, func_name:str, error_name:str, error_info:str) -> bool:
    """
    :param class_name: currently executing class  
    :param func_name: currently executing function
    :param error_name: error introduction
    :param error_info: error informations 
    """
    send_content="<h1>Project taas_api_fature_cover</h1><br><h2> class:{}, function:{}, error:</h2>{}<br><h3>error information:</h3>{}".format(class_name, func_name, error_name, error_info.replace('\n', '<br>')),
    url = 'http://metrix-dev.sh.intel.com:15501/send_email'
    param = {'TO': DEVELOPER, 'CC': DEVELOPER, 'subject': "taas_api_report_approval error, please fix.", 'content': send_content, 'bcc': DEVELOPER}
    try:
        requests.post(url=url, data=param, verify=False, proxies=proxies)
        return True
    except Exception as e:
        logger.error('send email fail error is :{}'.format(str(e)))
        return False


def req_hsd_data_by_query_id( query_id: str ) -> list :
    """
    :param query_id:
    :return: hsd_data
    """
    link = "https://metrix.sh.intel.com/api/hsdes/query?query_id={}&include_text_fields=y&start_at=1&max_results=9999"
    resp = requests.post(url=link.format(query_id), verify=False, headers=headers, proxies=proxies)
    if resp.status_code != 200:
        logger.error(f'Warning !!!! get data by query_id fail, query_id is :{query_id}, HSD return ifno {resp.text}')
        raise HSDError(f'Failed to get data from HSD, query id is {query_id}')
    result = resp.json()
    if 'data' not in result:
        logger.error(f'Error !!!! get data by query_id fail, query_id is :{query_id}, HSD return ifno {resp.text}')
        raise HSDError(f'Failed to get data from HSD, query id is {query_id}')
    return result.get('data')


def list_dic_2_file(query_id:str, data:list) -> str:
    file_name = f"{query_id}_{date.today().strftime('%y_%m_%d')}.csv"
    file_path = os.path.join(static, file_name)
    
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return file_name



def select_tcd_by_fr_ids( fr_ids :list) -> dict:
    tcd_id_list = []
    fr_map_tcd = {}
    for i in fr_ids:
        if i.isdigit():
            tcd_id_list.append(i)
    for index in range((len(tcd_id_list) // 200) + 2 ):
        start = index * 200
        end = (index + 1 )* 200
        if end > len(tcd_id_list) : end = len(tcd_id_list)
        limit_tcd_id_list = tcd_id_list[start: end]
        if not limit_tcd_id_list: continue
        param = {"EQL": "select id, title, subject, status, owner, domain, release_affected, family_affected where Parent(central_firmware.feature.id in ({hsd_id})), Child(central_firmware.test_case_definition.id > 0 )".format(hsd_id=','.join(limit_tcd_id_list)),"START": 1, "LIMIT": 9999}
        response = requests.get(url='https://metrix.sh.intel.com/api/hsdes/query/eql', params=param, verify=False, headers=headers, proxies=proxies)
        for info in response.json().get('data'):
            sub = info.get('subject')
            if sub == 'test_case_definition':
                feature_id = info.get('source_id')
                if feature_id not in fr_map_tcd:
                    info['test_case_definition'] = [info]
                    fr_map_tcd[feature_id] = info
                else:
                    fr_map_tcd[feature_id]['test_case_definition'].append(info)
            elif sub == 'feature':
                feature_id = info.get('id')
                info['test_case_definition'] = []
                if feature_id not in fr_map_tcd:
                    fr_map_tcd[feature_id] = info
    return fr_map_tcd


def statistics_fr_cover_data( query_id: str ) -> dict:
    f_map_tcd_lt = dict()
    feature_ids = [info.get('id') for info in req_hsd_data_by_query_id(query_id)]
    try:
        data = select_tcd_by_fr_ids(feature_ids)
    except:
        logger.error(f'Error !!!! select_tcd_by_fr_ids fail, query_id is :{query_id}.')
        raise HSDError(F'Failed to get data from HSD, query id is {query_id}')
    for k, v in data.items():
        f_map_tcd_lt[k] = v.get('test_case_definition')
    map_num = 0
    regression_num = 0
    tcd_data = {}
    for f_id in feature_ids:
        tcds = f_map_tcd_lt.get(f_id)

        if not tcds: continue

        map_num += 1
        for tcd in tcds:
            tcd_id = tcd.get('id')
            title = tcd.get('title', '').lower()
            if 'regression' in title and len(tcds) < 2 :
                regression_num += 1
            if tcd_id not in tcd_data:
                tcd['cover by feature'] = [f_id]
                tcd_data[tcd_id] = tcd
            else:
                tcd_data[tcd_id]['cover by feature'].append(f_id)
    
    return { 'cover': map_num, 'total': len(feature_ids), 'regression': regression_num, 'data': tcd_data}
    

if __name__ == '__main__':
    # send_warning_to_dev()
    data = statistics_fr_cover_data('15011704623')
    infos = list(data.get('data').values())
    list_dic_2_file('15011704623', infos)
