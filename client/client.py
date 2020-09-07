from configparser import ConfigParser
import uvicorn
import hashlib
from loguru import logger
import sys
from fastapi import FastAPI,Query
from pydantic import BaseModel
from fastapi.responses import FileResponse
import subprocess
import requests
import os
import json
import time
import nginx
app= FastAPI()
basedir=os.path.abspath(os.path.dirname(__file__))

#日志配置
log_path = os.path.join(basedir, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_path_error = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_error.log')
logger.add(log_path_error,colorize=True, rotation="00:00", retention="5 days", enqueue=True)
logger.add(sys.stdout,filter='my_module')
logger.add(sys.stderr,filter='my_module')


#从conf_client.ini配置文件中读取配置
config_ini = ConfigParser()
config_ini.read('conf/conf_client.ini')
server_ip=config_ini.get("server","ip")
server_port=config_ini.get("server","port")
nginx_ip=config_ini.get("nginx","nginx_ip")
nginx_main_conf_path=config_ini.get("nginx","nginx_main_conf_path")
uvicorn_ip=config_ini.get('uvicorn','ip')
uvicorn_port=config_ini.get('uvicorn','port')

#获取nginx主配置文件根目录
nginx_main_conf_path_dir = os.path.dirname(nginx_main_conf_path)

#创建数据目录
client_data_dir=  basedir + '/data'
if not os.path.exists(client_data_dir):
    os.mkdir(client_data_dir)

if not os.path.isfile(nginx_main_conf_path):
    exit(f'{nginx_main_conf_path}不存在，请检查配置文件！')

#nginx json文件名规范：ip-nginxconf.json
all_nginx_json_file = nginx_ip + '-nginxconf.json'
all_nginx_json_file_path= os.path.join(client_data_dir,all_nginx_json_file)

#解析nginx配置文件cmd
parse_all_nginx_conf_cmd = \
    ['crossplane', 'parse', '--no-catch', '--include-comments', nginx_main_conf_path, '-o',
     all_nginx_json_file_path]
#构建nginx配置文件cmd
# build_all_nginx_conf_cmd = \
#     ['crossplane', 'build', '--no-headers', '-f', '-d',nginx_main_conf_path_dir,
#      all_nginx_json_file_path]

'''nginx -t cmd'''
nginx_check_cmd=['nginx','-t','-c',nginx_main_conf_path]
'''nginx -s reload cmd'''
nginx_reload_cmd=['nginx','-c',nginx_main_conf_path,'-s','reload']



'''获取nginx -t 结果'''
def get_check_nginx_conf_result() ->str:
    try:
        out_bytes = subprocess.check_output(nginx_check_cmd,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        out_bytes = e.output       # Output generated before error
    #    code      = e.returncode   # Return code
    return out_bytes.decode('utf-8')

'''判断nginx是否在运行中'''
def is_nginx_running() ->bool:
    with open(all_nginx_json_file_path) as f:
        nginx_obj_str=f.read()
    nginx_obj_dict =  json.loads(nginx_obj_str)
    nginx_instace = nginx.Nginx(nginx_obj_dict=nginx_obj_dict,nginx_main_conf_path=nginx_main_conf_path)
    pid_file_path = nginx_instace.get_pid_file_path()
    if not os.path.exists(pid_file_path):
        return False
    with open(pid_file_path) as f:
        pid = f.read()
    if pid == '':
        return False
    return True

'''解析nginx 配置文件'''
async def check_and_parse_nginx_conf():
    '''进行nginx -t 检查,检查通过则将nginx配置文件解析到指定路径'''
    out_text = get_check_nginx_conf_result()

    if '[emerg]' in out_text or 'failed' in out_text or '[warn]' in out_text:
        print(f'''
\033[0;31;40m{out_text}\033[0m
        ''')
        raise Exception(f'''
\033[0;31;40m{out_text}\033[0m
        ''')

    if 'syntax is ok' in out_text and 'test is successful' in out_text  and '[warn]' not in out_text:
        subprocess.check_output(parse_all_nginx_conf_cmd, stderr=subprocess.STDOUT)

    else:
        logger.error(f'''
\033[0;31;40m{out_text}\033[0m
        ''')
        raise Exception(f'''
\033[0;31;40m{out_text}\033[0m
        ''')

'''获取file_path_list'''
def get_file_path_list()->list:
    with open(all_nginx_json_file_path) as f:
        nginx_obj_str=f.read()
    nginx_obj_dict =  json.loads(nginx_obj_str)
    nginx_instace = nginx.Nginx(nginx_obj_dict=nginx_obj_dict,nginx_main_conf_path=nginx_main_conf_path)
    return nginx_instace.get_file_path_list()

'''获取backendbackend_server_info_dict'''
def get_backend_server_info_dict():
    with open(all_nginx_json_file_path) as f:
        nginx_obj_str = f.read()
    nginx_obj_dict = json.loads(nginx_obj_str)
    nginx_instace = nginx.Nginx(nginx_obj_dict=nginx_obj_dict, nginx_main_conf_path=nginx_main_conf_path)
    return nginx_instace.get_backend_server_info_dict()

'''发送客户端ip和port给服务端'''
def post_client_info_to_server():
    url = f'http://{server_ip}:{server_port}/receive_client_info'

    client_info_dict=json.dumps({'client_uvicorn_ip':nginx_ip,
                     'client_uvicorn_port':uvicorn_port})
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    r=requests.post(url=url,data=client_info_dict,headers=headers)
    return r.text

'''将解析后的文件发送给服务端'''
def post_nginx_parsed_file_to_server():
    url = f'http://{server_ip}:{server_port}/receive_nginx_parsed_file'
    path = all_nginx_json_file_path
    files = {'file': open(path, 'rb')}
    r = requests.post(url, files=files)
    return r.text

'''根据解析后的文件获取文件列表和文件内容'''
def get_file_path_and_content_dict()->dict:
    file_path_and_content_dict = {}
    file_path_and_content_dict['client_ip']= nginx_ip
    file_path_list = get_file_path_list()
    for file_path in file_path_list:
        with open(file_path) as f:
            file_path_and_content_dict[file_path] = f.read()
    return file_path_and_content_dict

'''发送file_path_and_content_dict到服务端'''
def post_file_path_and_content_dict_to_server():
    url = f'http://{server_ip}:{server_port}/receive_nginx_file_path_and_content_dict'
    file_path_and_content_dict = get_file_path_and_content_dict()
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    r = requests.post(url=url, data=json.dumps(file_path_and_content_dict), headers=headers)
    return  r.text

'''根据解析后的文件生成get_backend_server_info_dict_new'''
def get_backend_server_info_dict_new()->dict:
    backend_server_info_dict_new = {}
    backend_server_info_dict = get_backend_server_info_dict()
    backend_server_info_dict_new['client_ip']= nginx_ip
    backend_server_info_dict_new['backend_server_info_dict'] = backend_server_info_dict
    return backend_server_info_dict_new

'''发送get_backend_server_info_dict_new到服务端'''
def post_backend_server_info_dict_to_server():
    url = f'http://{server_ip}:{server_port}/receive_nginx_backend_server_info_dict'
    backend_server_info_dict_new = get_backend_server_info_dict_new()
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    r = requests.post(url=url, data=json.dumps(backend_server_info_dict_new), headers=headers)
    return  r.text

# def build_nginx_conf():
#     subprocess.check_output(build_all_nginx_conf_cmd, stderr=subprocess.STDOUT)

@app.on_event('startup')
async def send_client_init_info_to_server():
    try:
        '''每次启动都将自己的ip、port、nginx主配置文件路径发送给服务端'''
        res1=post_client_info_to_server()
        logger.info(json.loads(res1))
        '''检测nginx配置文件并解析'''
        await check_and_parse_nginx_conf()
        '''将解析好的nginx文件发送给服务端'''
        res2=post_nginx_parsed_file_to_server()
        logger.info(json.loads(res2))
        '''将nginx的文件路径和文件内容发送给服务端'''
        res3 = post_file_path_and_content_dict_to_server()
        logger.info(json.loads(res3))
        '''将nginx的backend server info发送给服务端'''
        res4 = post_backend_server_info_dict_to_server()
        logger.info(json.loads(res4))
    except Exception as e:
        logger.error(str(e))
        raise Exception(f'message: {str(e)}')

@app.on_event("shutdown")
def shutdown_event():
        logger.error("Application shutdown\n")

@app.get('/download_nginx_parsed_file',description='dowload nginx parsed json file')
def download_json_file():
    path = all_nginx_json_file_path
    if not os.path.exists(path):
        logger.error(f'文件{path}不存在！')
        return {'success': False, 'msg': f'文件{path}不存在！'}
    response = FileResponse(path,filename=all_nginx_json_file)
    return response

class Item(BaseModel):
    file_path:str
    file_content:str =None

@app.post('/nginx_conf/create',description='新增配置文件')
async def create_new_file(item:Item):
    file_path = item.file_path
    '''获取文件父目录'''
    file_path_dir = os.path.dirname(file_path)
    if not os.path.exists(file_path_dir):
        logger.info(f'{file_path_dir}此目录不存在')
        return {'msg':f'{file_path_dir}此目录不存在','status':201}
    if os.path.isfile(file_path):
        logger.info(f'{file_path}此文件已存在')
        return {'msg':f'{file_path}此文件已存在','status':201}
    try:
        with open(file_path,'w') as f:
            f.write(f'#{file_path}')
        '''重新解析配置文件并发送给服务端'''
        await check_and_parse_nginx_conf()
        res2 = post_nginx_parsed_file_to_server()
        logger.info(json.loads(res2))
        res3 = post_file_path_and_content_dict_to_server()
        logger.info(json.loads(res3))
        res4 = post_backend_server_info_dict_to_server()
        logger.info(json.loads(res4))
        logger.info(f'{file_path}，此文件创建成功')
        return {'msg':f'{file_path}，此文件创建成功','status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.post('/nginx_conf/delete',description='删除配置文件')
async def delete_file(item:Item):
    file_path = item.file_path
    try:
        os.remove(file_path)
        '''重新解析配置文件并发送给服务端'''
        await check_and_parse_nginx_conf()
        res2 = post_nginx_parsed_file_to_server()
        logger.info(json.loads(res2))
        res3 = post_file_path_and_content_dict_to_server()
        logger.info(json.loads(res3))
        res4 = post_backend_server_info_dict_to_server()
        logger.info(json.loads(res4))
        logger.info(f'{file_path}，此文件删除成功')
        return {'msg': f'{file_path}，此文件删除成功', 'status': 200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}
@app.post('/nginx_conf/update',description='更新文件内容')
async def update_file(item:Item):
    file_path = item.file_path
    file_content = item.file_content
    if not os.path.exists(file_path):
        logger.info(f'{file_path}此文件不存在')
        return {'msg':f'{file_path}此文件不存在','status':201}
    try:
        with open(file_path, 'w') as f:
            f.write(file_content)
        '''重新解析配置文件并发送给服务端'''
        await check_and_parse_nginx_conf()
        res2 = post_nginx_parsed_file_to_server()
        logger.info(json.loads(res2))
        res3 = post_file_path_and_content_dict_to_server()
        logger.info(json.loads(res3))
        res4 = post_backend_server_info_dict_to_server()
        logger.info(json.loads(res4))
        logger.info(f'{file_path}，此文件内容更新成功)')
        return {'msg':f'{file_path}，此文件内容更新成功','status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.post('/nginx_conf/cancelUpdate',description='取消更新文件内容,将文件内容还原到上一次成功的状态')
async def cancel_update_file(item:Item):
    file_path = item.file_path
    file_content = item.file_content
    if not os.path.exists(file_path):
        logger.info(f'{file_path}此文件不存在')
        return {'msg':f'{file_path}此文件不存在','status':201}
    '''对比服务端和本地的文件内容md5，若相同则无需重新写入'''
    file_content_md5_from_db = hashlib.md5(file_content.encode('utf-8')).hexdigest()

    with open(file_path) as f:
        file_content_local = f.read()
    file_content_local_md5 = hashlib.md5(file_content_local.encode('utf-8')).hexdigest()

    if file_content_local_md5 == file_content_md5_from_db:
        # print('没改变')
        return {'msg':'文件内容未发生改变，无需修改','status':200}
    try:
        with open(file_path, 'w') as f:
            f.write(file_content)
        '''重新解析配置文件并发送给服务端'''
        logger.info(f'{file_path}，此文件内容还原到上一次成功的状态)')
        return {'msg':f'{file_path}，此文件内容还原到上一次成功的状态成功','status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.get('/nginx_conf/read',description='查询文件内容')
async def read_file(file_path:str=Query(...)):
    try:
        with open(file_path) as f:
            file_content=f.read()
        return {'msg':file_content,'status':200}
    except Exception as e:
        return {'msg': str(e), 'status': 201}

@app.post('/nginx_conf/check',description='检测nginx配置文件语法')
async def check_nginx_conf() ->str :
    check_result_str = get_check_nginx_conf_result()
    out_text_list = check_result_str.rstrip('\n').split('\n')
    return  out_text_list

@app.post('/nginx_conf/reload',description='重载nginx配置文件')
async def reload_nginx_conf():

    if not is_nginx_running():
        logger.error('nginx进程不存在,请先启动nginx')
        return {'msg': 'nginx进程不存在,请先启动nginx', 'status': 201}
    try:
        subprocess.check_output(nginx_check_cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return {'msg': e.output.decode('utf-8'), 'status': 201}


    try:
        subprocess.check_output(nginx_reload_cmd, stderr=subprocess.STDOUT)
        return {'msg': 'nginx配置文件重载重载成功', 'status': 200}
    except subprocess.CalledProcessError as e:
        logger.error(e.output.decode('utf-8'))
        return {'msg': e.output.decode('utf-8'), 'status': 201}

'''读取backend_server的配置'''
def read_backend_server_conf(file_path,backend_server_addr):
    if ':' in backend_server_addr:
        '''查非80端口'''
        sed_select = ['sed', '-nr', f"/\<server\>\s+{backend_server_addr}[^0-9]+/p", file_path]
    else:
        '''查80端口'''
        sed_select = ['sed', '-nr', f"/\<server\>\s+{backend_server_addr}[^:]*;/p", file_path]
    try:
        out_bytes = subprocess.check_output(sed_select,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        out_bytes = e.output       # Output generated before error
    #    code      = e.returncode   # Return code
    return out_bytes.decode('utf-8')


@app.get('/backend_server/read',description='读取backend_server的信息')
async def read_backend_server(file_path:str=Query(...),backend_server_addr:str=Query(...)):
    return  read_backend_server_conf(file_path=file_path,backend_server_addr=backend_server_addr)

class BackendServer(BaseModel):
    file_path: str
    backend_server_addr: str
    weight: int =None
    status: str =None

@app.post('/backend_server/status/update',description='修改backend_server的状态')
async def update_backend_server_status(item:BackendServer):
    '''先判断nginx是否在运行'''
    if not is_nginx_running() :
        return {'msg':'nginx进程不存在,请先启动nginx','status':201}
    file_path = item.file_path
    backend_server_addr = item.backend_server_addr
    status = item.status
    res_str = read_backend_server_conf(file_path=file_path, backend_server_addr=backend_server_addr)
    if ':' in backend_server_addr:
        '''改非80端口'''
        if status == 'down' or status == 'backup':
            if 'down' in res_str or 'backup' in res_str:
                sed_update = ['sed', '-i', '-r', f"/\<server\>\s+{backend_server_addr}[^0-9]+/s/down|backup/{status}/", file_path]
            else:
                sed_update = ['sed', '-i','-r', f"/\<server\>\s+{backend_server_addr}[^0-9]+/s/\s*;/ {status};/", file_path]
        else:
            if 'down' in res_str or 'backup' in res_str:
                sed_update = ['sed', '-i','-r', f"/\<server\>\s+{backend_server_addr}[^0-9]+/s/down|backup//", file_path]
            else:
                return {'msg':'修改状态成功','status':200}
    else:
        '''改80端口'''
        if status == 'down' or status == 'backup':
            if 'down' in res_str or 'backup' in res_str:
                sed_update = ['sed', '-i', '-r',f"/\<server\>\s+{backend_server_addr}[^:]*;/s/down|backup/{status}/", file_path]
            else:
                sed_update = ['sed','-i','-r',f"/\<server\>\s+{backend_server_addr}[^:]*;/s/\s*;/ {status};/",file_path]
        else:
            if 'down' in res_str or 'backup' in res_str:
                sed_update = ['sed','-i','-r',f"/\<server\>\s+{backend_server_addr}[^:]*;/s/down|backup//",file_path]
            else:
                return {'msg':'修改状态成功','status':200}
    try:
        '''执行sed替换命令'''
        subprocess.check_output(sed_update,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return {'msg': e.output.decode('utf-8'), 'status': 201}

    # try:
    #     '''执行nginx -t'''
    #     subprocess.check_output(nginx_check_cmd, stderr=subprocess.STDOUT)
    # except subprocess.CalledProcessError as e:
    #     return {'msg': e.output.decode('utf-8'), 'status': 201}

    try:
        '''重新解析配置文件并发送给服务端'''
        await  check_and_parse_nginx_conf()
        subprocess.check_output(nginx_reload_cmd, stderr=subprocess.STDOUT)
        logger.info('reload配置成功！')
        res2 = post_nginx_parsed_file_to_server()
        logger.info(json.loads(res2))
        res3 = post_file_path_and_content_dict_to_server()
        logger.info(json.loads(res3))
        res4 = post_backend_server_info_dict_to_server()
        logger.info(json.loads(res4))
        logger.info(f'成功修改{backend_server_addr}的状态为{status}')
        return {'msg':'修改状态成功','status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.post('/backend_server/weight/update',description='修改backend_server的权重')
async def update_backend_server_weight(item:BackendServer):
    file_path = item.file_path
    backend_server_addr = item.backend_server_addr
    weight = item.weight
    res_str = read_backend_server_conf(file_path=file_path, backend_server_addr=backend_server_addr)
    if ':' in backend_server_addr:
        '''改非80端口'''
        if 'weight' in res_str :
            sed_update = ['sed', '-i.bak', '-r', f"/\<server\>\s+{backend_server_addr}[^0-9]+/s/weight=\w/weight={weight}/", file_path]
        else:
            sed_update = ['sed', '-i.bak','-r', f"/\<server\>\s+{backend_server_addr}[^0-9]+/s/;/ weight={weight};/", file_path]

    else:
        '''改80端口'''
        if 'weight' in res_str :
            sed_update = ['sed', '-i.bak', '-r',f"/\<server\>\s+{backend_server_addr}[^:]*;/weight=\w/weight={weight}/", file_path]
        else:
            sed_update = ['sed','-i.bak','-r',f"/\<server\>\s+{backend_server_addr}[^:]*;/s/;/ weight={weight};/",file_path]

    try:
        subprocess.check_output(sed_update,stderr=subprocess.STDOUT)
        return {'msg':f'成功修改权重为{weight}','status':200}
    except subprocess.CalledProcessError as e:
        out_bytes = e.output       # Output generated before error
    #    code      = e.returncode   # Return code
        out_str = out_bytes.decode('utf-8')
        logger.error(out_str)
        return {'msg':out_str,'status':201}

if __name__ == '__main__':
    uvicorn.run(app,host=uvicorn_ip,port=int(uvicorn_port))