#!/usr/bin/env python3

import argparse
import os
import json
import time

def send_json_message(analysis_path:str, send_message_script: str, message: dict, step_file_name:str) -> None:
    os.system('bash {} \'{}\' 1>>final_message.log 2>&1'.format(send_message_script, json.dumps(message, ensure_ascii=False, indent=2)))
    with open('{}/{}'.format(analysis_path, step_file_name), 'w') as step_f:
        json.dump(message, fp=step_f, ensure_ascii=False, indent=4)

def steward(config_file_path:str, ukb_strelka2_variant_caller_path:str, send_message_script:str) -> None:
    analysis_path = os.path.dirname(config_file_path)
    os.chdir(analysis_path)
    # get paramters from the config.json
    with open(config_file_path, 'r') as config_f:
        config_d = json.load(config_f)
    task_id            = config_d['taskId']
    analysis_record_id = config_d['analysisRecordId']
    # make the params.json file
    params_d = {
        'fasta'           : config_d['fasta'],
        'fasta_index'     : config_d['fasta_index'],
        'tumor_cram'      : config_d['tumor_cram'],
        'tumor_cram_index': config_d['tumor_cram_index'],
        'normal_cram'      : config_d['normal_cram'],
        'normal_cram_index': config_d['normal_cram_index']
    }
    params_file_path = '{}/params.json'.format(analysis_path)
    with open(params_file_path, 'w') as params_f:
        json.dump(params_d, params_f, ensure_ascii=False, indent=4)
    ukb_strelka2_variant_caller_command = 'nextflow run -offline -profile singularity -bg -params-file {} {} >> run_log.txt'.format(params_file_path, ukb_strelka2_variant_caller_path)
    return_value = os.system(ukb_strelka2_variant_caller_command)
    with open('ukb_strelka2_variant_caller_command.txt', 'w') as command_f:
        command_f.write(ukb_strelka2_variant_caller_command + '\n')
        command_f.write('return value:{}\n'.format(str(return_value)))
    time.sleep(10)
    # send the result files 
    feedback_dict = {
        'tTaskId'         : task_id,
        'analysisRecordId': analysis_record_id,
        'pipelineName'    : 'ukb_strelka2_variant_caller',
        'analysisStatus'  : '',
        'startDate'       : time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'endDate'         : '',
        'error'           : 0,
        'taskName'        : 'Step'
    }
    if return_value == 0 and os.path.exists('{}/results'.format(analysis_path)):
        feedback_dict['analysisStatus'] = '分析开始'
        feedback_dict['endDate']        = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        feedback_dict['error']          = 0
        send_json_message(analysis_path, send_message_script, feedback_dict, 'start.json')
    else:
        feedback_dict['analysisStatus'] = '分析开始'
        feedback_dict['endDate']        = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        feedback_dict['error']          = 1
        send_json_message(analysis_path, send_message_script, feedback_dict, 'start.json')
    flag = 0
    while True:
        execution_trace_file = '{}/results'.format(analysis_path)
        if 'pipeline_info' in os.listdir(execution_trace_file):
            execution_trace_file += '/pipeline_info'
            for file in os.listdir(execution_trace_file):
                if file.startswith('execution_trace'):
                    execution_trace_file += '/{}'.format(file)
                    flag = 1
                    break
            if flag == 1 :
                break
        time.sleep(5)
    feedback_dict['analysisStatus'] = '分析结果'
    feedback_dict['endDate']        = ''
    feedback_dict['taskName']       = 'Result'
    feedback_dict['error']          = 0
    feedback_dict['data']           = []
    flag = 0
    while True:
        with open(execution_trace_file, encoding = 'UTF-8') as trace_f:
            for line in trace_f:
                if 'STRELKA_SOMATIC' in line:
                    if 'COMPLETED' in line:
                        feedback_dict['endDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        feedback_dict['error'] = 0
                        for file in os.listdir('{}/results'.format(analysis_path)):
                            if file.endswith('.somatic_indels.vcf.gz'):
                                somatic_indels_vcf_gz = '{}/results/{}'.format(analysis_path, file)
                            if file.endswith('.somatic_indels.vcf.gz.tbi'):
                                somatic_indels_vcf_gz_tbi = '{}/results/{}'.format(analysis_path, file)
                            if file.endswith('.somatic_snvs.vcf.gz'):
                                somatic_snvs_vcf_gz = '{}/results/{}'.format(analysis_path, file)
                            if file.endswith('.somatic_snvs.vcf.gz.tbi'):
                                somatic_snvs_vcf_gz_tbi = '{}/results/{}'.format(analysis_path, file)
                        report_download_dict = {
                            'sort' : 1,
                            'title': '分析结果文件',
                            'text' : [
                                {
                                    'sort'   : 1,
                                    'title'  : 'strelka检测somatic的SNPs和Indels结果1',
                                    'content': 'strelka检测somatic的SNPs和Indels结果1：#&{}'.format(somatic_indels_vcf_gz),
                                    'postDes': '',
                                    'memo'   : '',
                                    'preDes' : ''
                                },
                                {
                                    'sort'   : 2,
                                    'title'  : 'strelka检测somatic的SNPs和Indels结果2',
                                    'content': 'strelka检测somatic的SNPs和Indels结果2：#&{}'.format(somatic_indels_vcf_gz_tbi),
                                    'postDes': '',
                                    'memo'   : '',
                                    'preDes' : ''
                                },
                                {
                                    'sort'   : 3,
                                    'title'  : 'strelka检测somatic的SNPs和Indels结果3',
                                    'content': 'strelka检测somatic的SNPs和Indels结果3：#&{}'.format(somatic_snvs_vcf_gz),
                                    'postDes': '',
                                    'memo'   : '',
                                    'preDes' : ''
                                },
                                {
                                    'sort'   : 4,
                                    'title'  : 'strelka检测somatic的SNPs和Indels结果4',
                                    'content': 'strelka检测somatic的SNPs和Indels结果4：#&{}'.format(somatic_snvs_vcf_gz_tbi),
                                    'postDes': '',
                                    'memo'   : '',
                                    'preDes' : ''
                                }
                            ], 
                            'memo'     : '',
                            'subtitle1': '',
                            'subtitle2': ''
                        }
                        feedback_dict['data'].append(report_download_dict)
                    else:
                        feedback_dict['endDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                        feedback_dict['error'] = 1
                    send_json_message(analysis_path, send_message_script, feedback_dict, 'result.json')
                    flag = 1 
                    break
                else:
                    time.sleep(5)
            if flag == 1:
                break


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfp', required=True, help='the full path of the config.json')
    parser.add_argument('--ukb_strelka2_variant_caller_path', required=True, help='the full path of the ukb_strelka2_variant_caller')
    parser.add_argument('--send_message_script', required=True, help='the full path for the shell script: sendMessage.sh')
    args = parser.parse_args()
    config_file_path = args.cfp
    ukb_strelka2_variant_caller_path = args.ukb_strelka2_variant_caller_path
    send_message_script = args.send_message_script
    steward(config_file_path, ukb_strelka2_variant_caller_path, send_message_script)


if __name__ == '__main__':
    main()