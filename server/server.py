from configparser import  ConfigParser
import sqlite3
import hashlib
from fastapi import FastAPI, File, UploadFile, Body,Query, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import uvicorn
from loguru import logger
import requests
import os
import time
import json
import sys

from starlette.middleware.cors import CORSMiddleware

#加密私钥，算法，和token过期时间
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =300
#模拟数据库
users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$OqyamYSEtOPyzOWa3sK7RefPWjrDg0mFBCARHU6DspkeCuQ/9J/Nu",
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

class User(BaseModel):
    username: str
    email: str = None
    disabled: bool = None

class UserInDB(User):
    hashed_password: str

#初始化hash加密实例
passwd_context = CryptContext(schemes=["bcrypt"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

app= FastAPI()

#用户登录验证和token方法集：
def verify_password(plain_password, hashed_password):
    return passwd_context.verify(plain_password, hashed_password)

#此处没有用到，注册功能才会用到
def get_password_hash(password):
    return passwd_context.hash(password)

'''以下两个函数用于用户登录时校验用户名和密码'''
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return {'msg':'用户名错','status':401}
    if not verify_password(password, user.hashed_password):
        return {'msg':'密码错','status':401}
    return {'msg':user,'status':200}

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        #这里是时间戳，要进行转换
        expired_timestamp = payload.get('exp')
        expired_time_utc = datetime.utcfromtimestamp(expired_timestamp)
        # print('expired_time',expired_time_utc)
        # print(expired_time_utc-datetime.utcnow())
        if username is None:
            # return {'msg': '用户名为空', 'status': 403}
            raise credentials_exception
        token_data = TokenData(username=username)
        '''判断token是否过期'''
        # if expired_time_utc < datetime.utcnow() :
        #     # return {'msg':'token已过期','status':403}
        #     raise HTTPException(status_code=403, detail="token已过期")
    except PyJWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
        # return {'msg': '用户名为空', 'status': 403}
    return user


async def get_current_active_user(current_user:User = Depends(get_current_user)):
    # if current_user_info['status'] != 200:
    #     return current_user_info
    if current_user.disabled:
        # return {'msg':'用户状态为disabled，不允许登录','status':403}
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

#获取server.py文件所在目录的绝对路径
basedir=os.path.abspath(os.path.dirname(__file__))


#设置允许访问的域名
origins = ["*"]  #也可以设置为"*"，即为所有。
#origins = ["192.168.0.27"]  #也可以设置为"*"，即为所有。
#设置跨域传参
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  #设置允许的origins来源
    allow_credentials=True,
    allow_methods=["*"],  # 设置允许跨域的http方法，比如 get、post、put等。
    allow_headers=["*"])  #允许跨域的headers，可以用来鉴别来源等作用。

#日志配置
log_path = os.path.join(basedir, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)
log_path_error = os.path.join(log_path, f'{time.strftime("%Y-%m-%d")}_error.log')
logger.add(log_path_error,colorize=True, rotation="00:00", retention="5 days", enqueue=True)
logger.add(sys.stderr,filter='my_module')

#从conf_server.ini配置文件中读取配置
config_ini = ConfigParser()
config_ini.read('conf/conf_server.ini')
uvicorn_ip=config_ini.get('uvicorn','ip')
uvicorn_port=int(config_ini.get('uvicorn','port'))

'''创建数据目录'''
server_data_dir=  basedir + '/data'
if not os.path.exists(server_data_dir):
    os.mkdir(server_data_dir)
'''创建数据库目录'''
db_dir = basedir + '/db'
if not  os.path.exists(db_dir):
    os.mkdir(db_dir)

#数据库路径
file_path_and_content_db_path = os.path.join(db_dir, 'nginx_file_path_and_content.db')
backend_server_info_db_path = os.path.join(db_dir, 'nginx_backend_server_info.db')

ip_regex='(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)'

class ClientInfoItem(BaseModel):
    client_uvicorn_ip: Optional[str]=Body(...,regex=ip_regex)
    client_uvicorn_port: Optional[str]

class Item(BaseModel):
    client_ip: str
    file_path: str= None
    file_content: str = None

def get_client_port(client_ip) ->str:
    config_ini = ConfigParser()
    config_ini.read('conf/conf_server.ini')
    return config_ini.get('client',client_ip)


#response_model=Token
@app.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_res = authenticate_user(users_db, form_data.username, form_data.password)
    if user_res['status'] != 200:
        return user_res
    user = user_res['msg']

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # return {"access_token": access_token, "token_type": "Bearer", "status": 200}
    return {"access_token": access_token, "status": 200}

@app.post('/receive_client_info',
          description='客户端启动时将其ip和port发送过来，然后更新写入conf_server.ini')
def receive_client_info(client_info_dict:ClientInfoItem=Body(...)):
    client_uvicorn_ip=client_info_dict.client_uvicorn_ip
    client_uvicorn_port=client_info_dict.client_uvicorn_port
    config_ini = ConfigParser()
    config_ini.read('conf/conf_server.ini')
    try:
        config_ini.set('client',client_uvicorn_ip,client_uvicorn_port)
        config_ini.write(open('conf/conf_server.ini','w'))
        logger.info(f'以下配置已更新到服务端:\n[client]\n{client_uvicorn_ip}={client_uvicorn_port}')
        return {'msg':f'以下配置已更新到服务端:\n[client]\n{client_uvicorn_ip}={client_uvicorn_port}','status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.get('/get_client_ip_list',description='获取客户端ip列表')
async def get_client_ip_list():
    config_ini = ConfigParser()
    config_ini.read('conf/conf_server.ini')
    return  config_ini.options('client')

@app.post('/receive_nginx_parsed_file')
async def receive_nginx_parsed_file(file:UploadFile=File(...)):
    filename = file.filename
    nginx_parsed_file_path = os.path.join(server_data_dir,filename)
    try:
        res = await file.read()
        with open(nginx_parsed_file_path, "wb") as f:
            f.write(res)
        logger.info(f'{nginx_parsed_file_path}文件接收成功')
        return {'msg':f'{nginx_parsed_file_path}文件接收成功','status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.post('/receive_nginx_file_path_and_content_dict',description='接收客户端配置文件内容并更新数据库内容')
async def receive_nginx_file_path_and_content_dict(file_path_and_content_dict:dict =Body(...)):
    try:
        client_ip = file_path_and_content_dict['client_ip']
        file_path_and_content_dict.pop('client_ip')
        file_path_in_db_list =[]

        '''连接sqlite3数据库'''
        conn = sqlite3.connect(file_path_and_content_db_path)
        '''创建游标'''
        dbcurs = conn.cursor()
        '''创建表'''
        dbcurs.execute(f'''
        CREATE TABLE IF NOT EXISTS '{client_ip}'(
        file_path    TEXT           PRIMARY KEY,
        file_content TEXT,
        md5 TEXT
        )
        ''')
        '''如果文件路径不存在则insert，如果文件内容没变化则跳过，如果文件内容有变化则update'''
        for file_path,file_content in file_path_and_content_dict.items():
            file_content_md5 = hashlib.md5(file_content.encode('utf-8')).hexdigest()
            select_sql = f"select * from '{client_ip}' where file_path ='{file_path}'"
            select_sql_res = dbcurs.execute(select_sql)
            result_tuple = select_sql_res.fetchone()
            if result_tuple == None:
                insert_sql = f"insert into '{client_ip}' values(?,?,?)"
                data_tuple=(file_path,file_content,file_content_md5)
                dbcurs.execute(insert_sql,data_tuple)
            elif result_tuple[2] == file_content_md5:
                continue
            else:
                update_sql = f"update '{client_ip}' set file_content=?,md5=? where file_path=?"
                data_tuple = (file_content,file_content_md5,file_path)
                dbcurs.execute(update_sql,data_tuple)
        '''判断文件是否被删除，如果被删除，则清除表中的记录'''
        select_all_sql = f"select file_path from '{client_ip}'"
        select_all_sql_res = dbcurs.execute(select_all_sql)
        result_tuple = select_all_sql_res.fetchall()
        for per_tuple in result_tuple:
            file_path_in_db_list.append(per_tuple[0])
        for file_path_in_db in file_path_in_db_list:
            if not file_path_in_db in file_path_and_content_dict:
                delete_sql = f"delete from '{client_ip}' where file_path='{file_path_in_db}'"
                dbcurs.execute(delete_sql)
        dbcurs.close()
        conn.commit()
        conn.close()
        logger.info('配置文件同步到数据库成功')
        return {'msg':'配置文件同步数据库成功','status':200}
    except Exception as e:
        return {'msg':str(e),'status':201}

@app.post('/receive_nginx_backend_server_info_dict',description='接收客户端backend server info 并更新数据库内容')
async def receive_nginx_file_path_and_content_dict(backend_server_info_dict_new:dict =Body(...)):
    try:

        client_ip = backend_server_info_dict_new['client_ip']
        backend_server_info_dict = backend_server_info_dict_new['backend_server_info_dict']
        # print(backend_server_info_dict)
        '''连接sqlite3数据库'''
        conn = sqlite3.connect(backend_server_info_db_path)
        '''创建游标'''
        dbcurs = conn.cursor()
        '''删除之前的表'''
        dbcurs.execute(f"DROP TABLE IF EXISTS '{client_ip}'")
        '''创建表'''
        dbcurs.execute(f'''
        CREATE TABLE '{client_ip}'(
        backend_server_addr    TEXT           PRIMARY KEY,
        file_path TEXT,
        upstream TEXT, 
        status TEXT
        )
        ''')
        for backend_server_addr,v in backend_server_info_dict.items():
            insert_sql = f"insert into '{client_ip}' values(?,?,?,?)"
            data_tuple = (backend_server_addr, v['file_path'], v['upstream'],v['status'])
            dbcurs.execute(insert_sql, data_tuple)
        dbcurs.close()
        conn.commit()
        conn.close()
        logger.info('backend server info同步到数据库成功')
        return {'msg':'backend server info同步数据库成功','status':200}
    except Exception as e:
        return {'msg':str(e),'status':201}

@app.post('/nginx_conf/create',description='新增配置文件')
def create_new_file(item:Item):
    client_ip = item.client_ip
    file_path = item.file_path
    client_port = get_client_port(client_ip)
    url = f'http://{client_ip}:{client_port}/nginx_conf/create'
    params = {'file_path':file_path}
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    try:
        res=requests.post(url=url,data=json.dumps(params),headers=headers)
        logger.info(json.loads(res.text))
        return json.loads(res.text)
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.post('/nginx_conf/delete',description='删除配置文件')
def delete_file(item:Item):
    client_ip = item.client_ip
    file_path = item.file_path
    client_port = get_client_port(client_ip)
    url = f'http://{client_ip}:{client_port}/nginx_conf/delete'
    params = {'file_path': file_path}
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    try:
        res = requests.post(url=url, data=json.dumps(params), headers=headers)
        return json.loads(res.text)
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}
@app.post('/nginx_conf/update',description='更新配置文件')
def delete_file(item:Item):
    client_ip = item.client_ip
    file_path = item.file_path
    file_content = item.file_content
    client_port = get_client_port(client_ip)
    url = f'http://{client_ip}:{client_port}/nginx_conf/update'
    params = {'file_path': file_path,'file_content':file_content}
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    try:
        res = requests.post(url=url, data=json.dumps(params), headers=headers)
        return json.loads(res.text)
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.post('/nginx_conf/cancelUpdate',description='当前端页面取消更新配置文件时，读取数据库的内容返回给客户端')
def delete_file(item:Item):
    client_ip = item.client_ip
    file_path = item.file_path
    '''连接sqlite3数据库'''
    conn = sqlite3.connect(file_path_and_content_db_path)
    '''创建游标'''
    dbcurs = conn.cursor()
    select_sql = f"select file_content from '{client_ip}'  where file_path='{file_path}'"
    try:
        select_sql_res = dbcurs.execute(select_sql)
        result_tuple = select_sql_res.fetchone()
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}
    file_content = result_tuple[0]
    client_port = get_client_port(client_ip)
    url = f'http://{client_ip}:{client_port}/nginx_conf/cancelUpdate'
    params = {'file_path': file_path,'file_content':file_content}
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    try:
        res = requests.post(url=url, data=json.dumps(params), headers=headers)
        return json.loads(res.text)
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.get('/nginx_conf/read',description='读取单个配置文件')
async def read_file(client_ip: str=Query(...),file_path:str=Query(...)):
    '''连接sqlite3数据库'''
    conn = sqlite3.connect(file_path_and_content_db_path)
    '''创建游标'''
    dbcurs = conn.cursor()
    select_sql = f"select file_content from '{client_ip}'  where file_path='{file_path}'"
    try:
        select_sql_res = dbcurs.execute(select_sql)
        result_tuple = select_sql_res.fetchone()
        return {'msg':result_tuple[0],'status':200}
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

@app.get('/nginx/conf/readAll',description='读取所有配置文件')
async def read_all_file(client_ip:str =Query(...),current_user:User = Depends(get_current_active_user))->list:
    all_file_and_content_list=[]

    '''连接sqlite3数据库'''
    conn = sqlite3.connect(file_path_and_content_db_path)
    '''创建游标'''
    dbcurs = conn.cursor()
    select_all_sql = f"select file_path,file_content from '{client_ip}'"
    select_all_sql_res = dbcurs.execute(select_all_sql)
    result_tuple = select_all_sql_res.fetchall()
    # print(result_tuple)
    for per_record_tuple in result_tuple:
        per_file_and_content_dict = {}
        per_file_and_content_dict['file_path'] = per_record_tuple[0]
        per_file_and_content_dict['file_content'] = per_record_tuple[1]
        all_file_and_content_list.append(per_file_and_content_dict)
    dbcurs.close()
    conn.commit()
    conn.close()
    return all_file_and_content_list

@app.get('/nginx/backend_server/readAll',description='读取所有backend server 信息')
async def read_all_backend_server(client_ip:str =Query(...),current_user: User = Depends(get_current_active_user)) ->list:
    all_backend_server_info_list = []

    '''连接sqlite3数据库'''
    conn = sqlite3.connect(backend_server_info_db_path)
    '''创建游标'''
    dbcurs = conn.cursor()
    select_all_sql = f"select * from '{client_ip}'"
    select_all_sql_res = dbcurs.execute(select_all_sql)
    result_tuple = select_all_sql_res.fetchall()
    # print(result_tuple)
    for per_record_tuple in result_tuple:
        per_backend_server_info_dict = {}
        per_backend_server_info_dict['backend_server_addr'] = per_record_tuple[0]
        per_backend_server_info_dict['file_path'] = per_record_tuple[1]
        per_backend_server_info_dict['upstream'] = per_record_tuple[2]
        per_backend_server_info_dict['status'] = per_record_tuple[3]
        all_backend_server_info_list.append(per_backend_server_info_dict)
    dbcurs.close()
    conn.commit()
    conn.close()
    return all_backend_server_info_list

@app.get('/nginx/backend_server/readUpstream',description='读取给定upstream信息,支持模糊查找')
async def read_upstream_info(client_ip:str =Query(...),upstream:str=Query(...),current_user:User= Depends(get_current_active_user)) ->list:
    upstream_info_list = []

    '''连接sqlite3数据库'''
    conn = sqlite3.connect(backend_server_info_db_path)
    '''创建游标'''
    dbcurs = conn.cursor()
    select_upsream_sql = f"select * from '{client_ip}' where upstream like '%{upstream}%'"
    select_upsream_sql_res = dbcurs.execute(select_upsream_sql)
    result_tuple = select_upsream_sql_res.fetchall()
    # print(result_tuple)
    for per_record_tuple in result_tuple:
        per_backend_server_info_dict = {}
        per_backend_server_info_dict['backend_server_addr'] = per_record_tuple[0]
        per_backend_server_info_dict['file_path'] = per_record_tuple[1]
        per_backend_server_info_dict['upstream'] = per_record_tuple[2]
        per_backend_server_info_dict['status'] = per_record_tuple[3]
        upstream_info_list.append(per_backend_server_info_dict)
    dbcurs.close()
    conn.commit()
    conn.close()
    return upstream_info_list

@app.post('/nginx_conf/check',description='检测nginx配置文件语法')
async def check_nginx_conf(item:Item):
    client_ip = item.client_ip
    client_port = get_client_port(client_ip)
    url = f'http://{client_ip}:{client_port}/nginx_conf/check'
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    res = requests.post(url=url, headers=headers)
    return json.loads(res.text)


@app.post('/nginx_conf/reload',description='重载nginx配置文件')
async def reload_nginx_conf(item:Item):
    client_ip = item.client_ip
    client_port = get_client_port(client_ip)
    url = f'http://{client_ip}:{client_port}/nginx_conf/reload'
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    res = requests.post(url=url, headers=headers)
    return json.loads(res.text)

class BackendServer(BaseModel):
    client_ip: str
    file_path: str
    backend_server_addr: str
    weight: int =None
    status: str =None

@app.post('/backend_server/status/update',description='修改backend_server的状态')
def update_backend_server_status(item:BackendServer):
    client_ip = item.client_ip
    client_port = get_client_port(client_ip)
    file_path = item.file_path
    backend_server_addr = item.backend_server_addr
    status = item.status
    url = f'http://{client_ip}:{client_port}/backend_server/status/update'
    params = {'file_path': file_path,'backend_server_addr':backend_server_addr,'status':status}
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    try:
        res = requests.post(url=url, data=json.dumps(params), headers=headers)
        return json.loads(res.text)
    except Exception as e:
        logger.error(str(e))
        return {'msg':str(e),'status':201}

if __name__ == '__main__':
    uvicorn.run(app,host=uvicorn_ip,port=uvicorn_port)