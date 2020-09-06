import os,crossplane,copy,re


# nginx_all_conf_build=crossplane.build()

my_nginx_obj_dict=\
{"status":"ok","errors":[],"config":[{"file":"/etc/nginx/nginx.conf","status":"ok","errors":[],"parsed":[{"directive":"user","line":1,"args":["nginx"]},{"directive":"worker_processes","line":2,"args":["1"]},{"directive":"error_log","line":3,"args":["/var/log/nginx/error.log","warn"]},{"directive":"pid","line":4,"args":["/var/run/nginx.pid"]},{"directive":"events","line":5,"args":[],"block":[{"directive":"worker_connections","line":6,"args":["1024"]}]},{"directive":"http","line":8,"args":[],"block":[{"directive":"include","line":9,"args":["/etc/nginx/mime.types"],"includes":[1]},{"directive":"default_type","line":10,"args":["application/octet-stream"]},{"directive":"log_format","line":11,"args":["main","$remote_addr - $remote_user [$time_local] \"$request\" ","$status $body_bytes_sent \"$http_referer\" ","\"$http_user_agent\" \"$http_x_forwarded_for\""]},{"directive":"access_log","line":12,"args":["/var/log/nginx/access.log","main"]},{"directive":"sendfile","line":13,"args":["on"]},{"directive":"keepalive_timeout","line":14,"args":["65"]},{"directive":"include","line":15,"args":["conf.d/*.conf"],"includes":[2,3]}]},{"directive":"#","line":20,"args":[],"comment":"stream {"},{"directive":"#","line":21,"args":[],"comment":"    upstream up1 {"},{"directive":"#","line":22,"args":[],"comment":"        hash $remote_addr consistent;"},{"directive":"#","line":23,"args":[],"comment":"        server 127.0.0.1:12346 weight=5;"},{"directive":"#","line":24,"args":[],"comment":"        server 127.0.0.1:12347            max_fails=3 fail_timeout=30s;"},{"directive":"#","line":25,"args":[],"comment":"        server 127.0.0.1:12348            max_fails=3 fail_timeout=30s;"},{"directive":"#","line":26,"args":[],"comment":"    }"},{"directive":"#","line":27,"args":[],"comment":"    upstream dns {"},{"directive":"#","line":28,"args":[],"comment":"       server 17.61.29.79:53;"},{"directive":"#","line":29,"args":[],"comment":"       server 17.61.29.80:53;"},{"directive":"#","line":30,"args":[],"comment":"       server 17.61.29.81:53;"},{"directive":"#","line":31,"args":[],"comment":"       server 17.61.29.82:53;"},{"directive":"#","line":32,"args":[],"comment":"    }"},{"directive":"#","line":33,"args":[],"comment":"    server {"},{"directive":"#","line":34,"args":[],"comment":"        listen 12345;"},{"directive":"#","line":35,"args":[],"comment":"        proxy_connect_timeout 1s;"},{"directive":"#","line":36,"args":[],"comment":"        proxy_timeout 3s;"},{"directive":"#","line":37,"args":[],"comment":"        proxy_pass up1;"},{"directive":"#","line":38,"args":[],"comment":"    }"},{"directive":"#","line":39,"args":[],"comment":"    server {"},{"directive":"#","line":40,"args":[],"comment":"        listen 127.0.0.1:53 udp;"},{"directive":"#","line":41,"args":[],"comment":"        proxy_responses 1;"},{"directive":"#","line":42,"args":[],"comment":"        proxy_timeout 20s;"},{"directive":"#","line":43,"args":[],"comment":"        proxy_pass dns;"},{"directive":"#","line":44,"args":[],"comment":"    }"}]},{"file":"/etc/nginx/mime.types","status":"ok","errors":[],"parsed":[{"directive":"types","line":2,"args":[],"block":[{"directive":"text/html","line":3,"args":["html","htm","shtml"]},{"directive":"text/css","line":4,"args":["css"]},{"directive":"text/xml","line":5,"args":["xml"]},{"directive":"image/gif","line":6,"args":["gif"]},{"directive":"image/jpeg","line":7,"args":["jpeg","jpg"]},{"directive":"application/javascript","line":8,"args":["js"]},{"directive":"application/atom+xml","line":9,"args":["atom"]},{"directive":"application/rss+xml","line":10,"args":["rss"]},{"directive":"text/mathml","line":11,"args":["mml"]},{"directive":"text/plain","line":12,"args":["txt"]},{"directive":"text/vnd.sun.j2me.app-descriptor","line":13,"args":["jad"]},{"directive":"text/vnd.wap.wml","line":14,"args":["wml"]},{"directive":"text/x-component","line":15,"args":["htc"]},{"directive":"image/png","line":16,"args":["png"]},{"directive":"image/svg+xml","line":17,"args":["svg","svgz"]},{"directive":"image/tiff","line":18,"args":["tif","tiff"]},{"directive":"image/vnd.wap.wbmp","line":19,"args":["wbmp"]},{"directive":"image/webp","line":20,"args":["webp"]},{"directive":"image/x-icon","line":21,"args":["ico"]},{"directive":"image/x-jng","line":22,"args":["jng"]},{"directive":"image/x-ms-bmp","line":23,"args":["bmp"]},{"directive":"font/woff","line":24,"args":["woff"]},{"directive":"font/woff2","line":25,"args":["woff2"]},{"directive":"application/java-archive","line":26,"args":["jar","war","ear"]},{"directive":"application/json","line":27,"args":["json"]},{"directive":"application/mac-binhex40","line":28,"args":["hqx"]},{"directive":"application/msword","line":29,"args":["doc"]},{"directive":"application/pdf","line":30,"args":["pdf"]},{"directive":"application/postscript","line":31,"args":["ps","eps","ai"]},{"directive":"application/rtf","line":32,"args":["rtf"]},{"directive":"application/vnd.apple.mpegurl","line":33,"args":["m3u8"]},{"directive":"application/vnd.google-earth.kml+xml","line":34,"args":["kml"]},{"directive":"application/vnd.google-earth.kmz","line":35,"args":["kmz"]},{"directive":"application/vnd.ms-excel","line":36,"args":["xls"]},{"directive":"application/vnd.ms-fontobject","line":37,"args":["eot"]},{"directive":"application/vnd.ms-powerpoint","line":38,"args":["ppt"]},{"directive":"application/vnd.oasis.opendocument.graphics","line":39,"args":["odg"]},{"directive":"application/vnd.oasis.opendocument.presentation","line":40,"args":["odp"]},{"directive":"application/vnd.oasis.opendocument.spreadsheet","line":41,"args":["ods"]},{"directive":"application/vnd.oasis.opendocument.text","line":42,"args":["odt"]},{"directive":"application/vnd.openxmlformats-officedocument.presentationml.presentation","line":43,"args":["pptx"]},{"directive":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","line":44,"args":["xlsx"]},{"directive":"application/vnd.openxmlformats-officedocument.wordprocessingml.document","line":45,"args":["docx"]},{"directive":"application/vnd.wap.wmlc","line":46,"args":["wmlc"]},{"directive":"application/x-7z-compressed","line":47,"args":["7z"]},{"directive":"application/x-cocoa","line":48,"args":["cco"]},{"directive":"application/x-java-archive-diff","line":49,"args":["jardiff"]},{"directive":"application/x-java-jnlp-file","line":50,"args":["jnlp"]},{"directive":"application/x-makeself","line":51,"args":["run"]},{"directive":"application/x-perl","line":52,"args":["pl","pm"]},{"directive":"application/x-pilot","line":53,"args":["prc","pdb"]},{"directive":"application/x-rar-compressed","line":54,"args":["rar"]},{"directive":"application/x-redhat-package-manager","line":55,"args":["rpm"]},{"directive":"application/x-sea","line":56,"args":["sea"]},{"directive":"application/x-shockwave-flash","line":57,"args":["swf"]},{"directive":"application/x-stuffit","line":58,"args":["sit"]},{"directive":"application/x-tcl","line":59,"args":["tcl","tk"]},{"directive":"application/x-x509-ca-cert","line":60,"args":["der","pem","crt"]},{"directive":"application/x-xpinstall","line":61,"args":["xpi"]},{"directive":"application/xhtml+xml","line":62,"args":["xhtml"]},{"directive":"application/xspf+xml","line":63,"args":["xspf"]},{"directive":"application/zip","line":64,"args":["zip"]},{"directive":"application/octet-stream","line":65,"args":["bin","exe","dll"]},{"directive":"application/octet-stream","line":66,"args":["deb"]},{"directive":"application/octet-stream","line":67,"args":["dmg"]},{"directive":"application/octet-stream","line":68,"args":["iso","img"]},{"directive":"application/octet-stream","line":69,"args":["msi","msp","msm"]},{"directive":"audio/midi","line":70,"args":["mid","midi","kar"]},{"directive":"audio/mpeg","line":71,"args":["mp3"]},{"directive":"audio/ogg","line":72,"args":["ogg"]},{"directive":"audio/x-m4a","line":73,"args":["m4a"]},{"directive":"audio/x-realaudio","line":74,"args":["ra"]},{"directive":"video/3gpp","line":75,"args":["3gpp","3gp"]},{"directive":"video/mp2t","line":76,"args":["ts"]},{"directive":"video/mp4","line":77,"args":["mp4"]},{"directive":"video/mpeg","line":78,"args":["mpeg","mpg"]},{"directive":"video/quicktime","line":79,"args":["mov"]},{"directive":"video/webm","line":80,"args":["webm"]},{"directive":"video/x-flv","line":81,"args":["flv"]},{"directive":"video/x-m4v","line":82,"args":["m4v"]},{"directive":"video/x-mng","line":83,"args":["mng"]},{"directive":"video/x-ms-asf","line":84,"args":["asx","asf"]},{"directive":"video/x-ms-wmv","line":85,"args":["wmv"]},{"directive":"video/x-msvideo","line":86,"args":["avi"]}]}]},{"file":"/etc/nginx/conf.d/default.conf","status":"ok","errors":[],"parsed":[{"directive":"server","line":1,"args":[],"block":[{"directive":"listen","line":2,"args":["80"]},{"directive":"server_name","line":3,"args":["localhost"]},{"directive":"location","line":4,"args":["/"],"block":[{"directive":"root","line":5,"args":["/usr/share/nginx/html"]},{"directive":"index","line":6,"args":["index.html","index.htm"]}]},{"directive":"error_page","line":8,"args":["500","502","503","504","/50x.html"]},{"directive":"location","line":9,"args":["=","/50x.html"],"block":[{"directive":"root","line":10,"args":["/usr/share/nginx/html"]}]}]}]},{"file":"/etc/nginx/conf.d/test.conf","status":"ok","errors":[],"parsed":[{"directive":"server","line":1,"args":[],"block":[{"directive":"listen","line":2,"args":["8081"]},{"directive":"server_name","line":3,"args":["jan.test.com"]},{"directive":"root","line":4,"args":["/usr/share/nginx/jan"]},{"directive":"set","line":5,"args":["$test",""]},{"directive":"if","line":6,"args":["$request_uri","~*","/img/test.php"],"block":[{"directive":"set","line":7,"args":["$test","P"]}]},{"directive":"location","line":9,"args":["/mulu"],"block":[{"directive":"default_type","line":10,"args":["application/json"]},{"directive":"alias","line":11,"args":["mulu"]},{"directive":"index","line":12,"args":["index.html","jan.index"]},{"directive":"return","line":13,"args":["200","good\\nuri: $uri\\nhost: $http_host\\n$host\\nremoteaddr: $remote_addr\\n"]}]},{"directive":"location","line":15,"args":["/"],"block":[{"directive":"proxy_pass","line":16,"args":["http://up1"]},{"directive":"#","line":16,"args":[],"comment":"\u6d4b\u8bd5"}]}]},{"directive":"server","line":19,"args":[],"block":[{"directive":"listen","line":20,"args":["8080"]},{"directive":"server_name","line":21,"args":["jan.test1.com","jan.test2.com"]},{"directive":"root","line":22,"args":["/usr/share/nginx/jan"]},{"directive":"set","line":23,"args":["$test",""]},{"directive":"location","line":24,"args":["/mulu"],"block":[{"directive":"default_type","line":25,"args":["application/json"]},{"directive":"alias","line":26,"args":["mulu"]},{"directive":"index","line":27,"args":["index.html","jan.index"]},{"directive":"return","line":28,"args":["200","good\\nuri: $uri\\nhost: $http_host\\n$host\\nremoteaddr: $remote_addr\\n"]}]},{"directive":"location","line":30,"args":["/a"],"block":[{"directive":"proxy_pass","line":31,"args":["http://up2"]}]},{"directive":"location","line":33,"args":["/"],"block":[{"directive":"proxy_pass","line":34,"args":["http://up1"]}]}]},{"directive":"upstream","line":37,"args":["up1"],"block":[{"directive":"server","line":38,"args":["192.168.1.1"]},{"directive":"server","line":39,"args":["192.168.1.2:8090","down","weight=1"]}]},{"directive":"upstream","line":41,"args":["up2"],"block":[{"directive":"ip_hash","line":42,"args":[]},{"directive":"server","line":43,"args":["192.168.1.2"]},{"directive":"#","line":43,"args":[],"comment":"ok  "},{"directive":"server","line":44,"args":["192.168.1.3:9000","down","weight=3"]}]},{"directive":"#","line":46,"args":[],"comment":"ok"}]}]}

basedir=os.path.abspath(os.path.dirname(__file__))

class Nginx:
    # nginx_obj_dict:  接收crossplane对nginx配置文件parse后生成的字典。
    #crossplane parse --no-catch --include-comments /etc/nginx/nginx.conf -o /root/nginxjson.conf

    #nginx_main_conf_paths:  nginx主配置文件绝对路径
    def __init__(self,
                 nginx_main_conf_path:str="/etc/nginx/nginx.conf",
                 nginx_obj_dict:dict={}
                 ):
        self.nginx_obj_dict = nginx_obj_dict
        self.nginx_conf = self.nginx_obj_dict["config"]
        self.nginx_main_conf_path = nginx_main_conf_path


    def get_pid_file_path(self):
        nginx_conf = self.nginx_conf
        for file in nginx_conf:
            file_path = file['file']
            if file_path == self.nginx_main_conf_path:
                file_all_directives_list = file['parsed']  # 取到本文件所有directive配置
                for file_per_directive_dict in file_all_directives_list:
                    if file_per_directive_dict['directive'] == 'pid':
                        return file_per_directive_dict['args'][0]
    def get_file_path_list(self)->list:
        '''
        file_path_list=[]
        返回所有配置文件的路径列表
        '''
        file_path_list = []
        nginx_conf = self.nginx_conf
        for file in nginx_conf:
            file_path = file['file']
            file_path_list.append(file_path)
        return file_path_list

    def check_file_path_is_under_main_file_dir(self):
        '''检测nginx配置文件是否都在主配置文件父目录下'''
        file_path_list=self.get_file_path_list()
        nginx_main_conf_path_dir = os.path.dirname(self.nginx_main_conf_path)
        for per_file_path in file_path_list:
            if not nginx_main_conf_path_dir in per_file_path:
                exit(f'''
        以下配置文件不在{nginx_main_conf_path_dir}目录或其子目录下,请修改对应的include指令和配置文件路径：
        {per_file_path}
                        ''')
    def check_main_conf_file(self):
        '''检测主配置文件是否有server和upstream指令'''
        for file in self.nginx_conf:
            file_path = file['file']
            if file_path == self.nginx_main_conf_path:
                nginx_main_conf_all_directives_dict = file['parsed']  # 取到本文件所有directive配置
                for file_per_directive_dict in nginx_main_conf_all_directives_dict:
                    if file_per_directive_dict["directive"] == "http":
                        for http_per_directive_dict in file_per_directive_dict['block']:
                            # print(http_per_directive_dict)
                            if http_per_directive_dict['directive'] == 'server' or \
                                    http_per_directive_dict['directive'] == 'upstream':
                                exit("请把http块下的server块和upstream块的配置移出主配置文件")
                    if file_per_directive_dict["directive"] == "stream":
                        for http_per_directive_dict in file_per_directive_dict['block']:
                            print(http_per_directive_dict)
                            if http_per_directive_dict['directive'] == 'server' or http_per_directive_dict[
                                'directive'] == 'upstream':
                                exit("请把stream块下的server块和upstream块的配置移出主配置文件")



    def get_backend_server_info_dict(self) ->dict :
        backend_server_info_dict  = {}
        nginx_conf = self.nginx_conf
        for file in nginx_conf:
            file_path = file['file']
            '''跳过主配置文件'''
            if file_path == self.nginx_main_conf_path:
                continue
            '''跳过mime.types文件'''
            if 'mime.types' in file_path:
                continue
            file_all_directives_list = file['parsed']  # 取到本文件所有directive配置
            for file_per_directive_dict in file_all_directives_list:
                if file_per_directive_dict['directive'] == 'upstream':
                    # print(file_per_directive_dict)
                    '''获取upstream_name'''
                    upstream_name = "".join(file_per_directive_dict['args'])

                    upstream_all_directives_list = file_per_directive_dict['block']
                    # print(upstream_all_directives_dict)
                    for upstream_per_directive_dict in upstream_all_directives_list:
                        # print(upstream_per_directive_dict)
                        if upstream_per_directive_dict['directive'] == 'server':
                            backend_server_args_list = upstream_per_directive_dict['args']
                            '''获取backend_server_addr'''
                            backend_server_addr =backend_server_args_list[0]
                            backend_server_info_dict[backend_server_addr] = {}
                            '''将backend_server的file_path、upstream_name、status存入backend_servers_info_dict字典。'''
                            backend_server_info_dict[backend_server_addr]['file_path'] = file_path
                            backend_server_info_dict[backend_server_addr]['upstream'] = upstream_name
                            if 'down' in backend_server_args_list:
                                backend_server_info_dict[backend_server_addr]['status'] = 'down'
                            elif 'backup' in backend_server_args_list:
                                backend_server_info_dict[backend_server_addr]['status'] = 'backup'
                            else:
                                backend_server_info_dict[backend_server_addr]['status'] = ''
        return backend_server_info_dict


    def analysis_nginx_all_conf(self) -> (list,dict,list,dict,list,dict):
        '''
        对全部的nginx配置进行分析，得到以下三个list，三个dict：
        1、
        virtual_server_name_list=[]
        记录所有虚拟主机列表：
        例如：['jan.test.com', 'jan.test1.com,jan.test2.com']
        2、
        virtual_servers_info={}
        所有虚拟主机信息，包括：所属配置文件路径、每个upstream及其对应的location规则(如果有配置proxy_pass指令)。
        例如：{'jan.test.com': {'filepath': '/etc/nginx/conf.d/test.conf', 'location_proxy': {'/': 'up1'}}, 'jan.test1.com,jan.test2.com': {'filepath': '/etc/nginx/conf.d/test.conf', 'location_proxy': {'/a': 'up2', '/': 'up1'}}}
        3、
        upstream_name_list=[]
        所有upstream名字列表：
        例如：['up1', 'up2']
        4、
        upstreams_info= {}
        所有upstream信息，包括：所属配置文件路径、backend server及其配置参数
        例如：{'up1': {'file_path': '/etc/nginx/conf.d/test.conf', 'servers': [['192.168.1.1'], ['192.168.1.2', 'down', 'weight=1']]}, 'up2': {'file_path': '/etc/nginx/conf.d/test.conf', 'servers': [['192.168.1.1'], ['192.168.1.2', 'down', 'weight=3']]}}
        5、
        backend_server_ip_port_list=[]  #应该做个判断，对元素进行过滤判断，如果有重复，则发出警告。
        所有backend_server的ip_port列表
        例如：['192.168.1.1:8080', '192.168.1.2', '192.168.1.3:8090', '192.168.1.2']
        6、
        backend_servers_info={}
        所有backend_server的信息：包括：所属配置文件路径、所属upsream名字、配置参数
        例如：{'192.168.1.1': {'file_path': '/etc/nginx/conf.d/test.conf', 'upstream': 'up2', 'args': ['192.168.1.1']}, '192.168.1.2': {'file_path': '/etc/nginx/conf.d/test.conf', 'upstream': 'up2', 'args': ['192.168.1.2', 'down', 'weight=3']}}
        '''
        virtual_server_name_list = []
        virtual_servers_info_dict = {}
        upstream_name_list = []
        upstreams_info_dict = {}

        '''一般backend_server_ip_port在不同的upstream中不会重复配置，如果存在重复，
        则下面的backend_servers_info的信息会出现覆盖的情况。
        '''
        backend_server_ip_port_list = []
        backend_servers_info_dict = {}

        #先保证主配置文件中没有server指令和upstream指令，不然以下结果不准确
        self.check_main_conf_file()

        nginx_conf = self.nginx_conf
        for file in nginx_conf:
            file_path = file['file']
            if  file_path == self.nginx_main_conf_path:
                continue
            if 'mime.types' in file_path:
                continue
            file_all_directives_dict = file['parsed']  # 取到本文件所有directive配置
            for file_per_directive_dict in file_all_directives_dict:
                if file_per_directive_dict['directive'] == 'upstream':
                    # print(file_per_directive_dict)
                    upstream_name = "".join(file_per_directive_dict['args'])
                    # print(upstream_name)
                    # 将每个upstream_name记录到upstream_name_list列表
                    if  upstream_name not  in upstream_name_list:
                        upstream_name_list.append(upstream_name)
                    else:
                        exit(f'''
此{upstream_name} 命名重复。
若遇到此信息,那是因为你的stream下的upstream名字与http下的upstream名字重复，
请修改其中的一个，因为我的产品中不允许出现这样可读性很模糊的配置。
虽然您的配置是没有错误的，但您最好不要这样做，
我们建议您将所有的stream块下面的upsream的命名都加'tcp'前缀。         
                        ''')
                    # 获取每个upstream的信息，存入upstreams__info字典。
                    upstreams_info_dict[upstream_name] = {}
                    upstreams_info_dict[upstream_name]['file_path'] = file_path
                    upstreams_info_dict[upstream_name]['backend_servers'] = []
                    # print(upstreams__info)
                    upstream_all_directives_list = file_per_directive_dict['block']
                    # print(upstream_all_directives_dict)
                    for upstream_per_directive_dict in upstream_all_directives_list:
                        # print(upstream_per_directive_dict)
                        if upstream_per_directive_dict['directive'] == 'server':
                            backend_server_args_list = upstream_per_directive_dict['args']
                            backend_server_args_deepcopy_list = copy.deepcopy(backend_server_args_list) #用于存储的时候剔除ip：port，只留下weight和down|backup参数
                            upstreams_info_dict[upstream_name]['backend_servers'].append(backend_server_args_list)
                            backend_server_ip_port = backend_server_args_deepcopy_list[0]
                            backend_server_ip_port_list.append(backend_server_ip_port)
                            backend_server_args_deepcopy_list.pop(0)
                            # print(backend_server_ip_port)
                            # 获取每个backend_server的信息，存入backend_servers_info字典。
                            backend_servers_info_dict[backend_server_ip_port] = {}
                            backend_servers_info_dict[backend_server_ip_port]['file_path'] = file_path
                            backend_servers_info_dict[backend_server_ip_port]['upstream'] = upstream_name
                            backend_servers_info_dict[backend_server_ip_port]['args'] = backend_server_args_deepcopy_list
                if file_per_directive_dict['directive'] == 'server':
                    server_all_directives_list=file_per_directive_dict['block']
                    directive_server_name_sum = 0
                    # print(server_all_directives_list)

                    server_name = ""
                    #做两次循环，第一次循环获取当前server块的server_name,第二次循环获取server_name的location args 机器对应的proxy_pass
                    for index, server_per_directive_dict in enumerate(server_all_directives_list):
                        # print(server_per_directive_dict)
                        if server_per_directive_dict['directive'] == "server_name":
                            # print(server_per_directive_dict)
                            directive_server_name_sum += 1
                            if directive_server_name_sum > 1:
                                exit("所有的server_name请写在同一行")
                            server_name_agrs_list=server_per_directive_dict['args']
                            examine_server_name = ''.join(server_name_agrs_list)
                            if not re.match("^[A-Za-z0-9.]*$", examine_server_name):
                                exit(f'''
以下域名中存在字母和数字以外的字符，请核对您的配置：
{server_name_agrs_list}
                                ''')
                            server_name = ",".join(server_per_directive_dict['args'])
                            # print(server_name)
                            # 将每个virtual_server_name存入virtual_server_name_list列表
                            virtual_server_name_list.append(server_name)
                            # 获取每个virtual_server的信息，并存入virtual_servers_info字典
                            virtual_servers_info_dict[server_name] = {}
                            virtual_servers_info_dict[server_name]['filepath'] = file_path
                            # virtual_servers_info[server_name]['current_server_directive_index']=index
                            virtual_servers_info_dict[server_name]['location_proxy'] = {}
                            virtual_servers_info_dict[server_name]['proxy_pass']=[]
                            # directive_server_name_index = index
                    #这是第二次循环
                    for server_per_directive_dict in server_all_directives_list:
                        # print(server_per_directive_dict)
                        if server_per_directive_dict['directive'] == "location":
                            location_arg = "".join(server_per_directive_dict['args'])
                            # print(location_arg)
                            location_all_directives_list=server_per_directive_dict['block']
                            for location_per_directive_dict in location_all_directives_list:
                                # print(location_per_directive_dict)
                                if location_per_directive_dict["directive"] == "proxy_pass":
                                    proxy_pass = "".join(location_per_directive_dict["args"]).split('//')[1]
                                    virtual_servers_info_dict[server_name]['proxy_pass'].append(proxy_pass)
                                    virtual_servers_info_dict[server_name]['location_proxy'][location_arg] = proxy_pass

        if not len(set(backend_server_ip_port_list)) == len(backend_server_ip_port_list):
            temp_set=set()
            duplicate_ackend_server_ip_port_list = []
            for backend_server_ip_port in backend_server_ip_port_list:
                if backend_server_ip_port not in temp_set:
                    temp_set.add(backend_server_ip_port)
                else:
                    duplicate_ackend_server_ip_port_list.append(backend_server_ip_port)
            exit( f'''
以下列表中的backend_server:ip在不同的upstream中重复了，请检查配置。
{duplicate_ackend_server_ip_port_list}
            ''')
        # print(self.analysis_nginx_all_conf.__annotations__)
        return virtual_server_name_list,virtual_servers_info_dict,\
               upstream_name_list,upstreams_info_dict, \
               backend_server_ip_port_list,backend_servers_info_dict

if __name__ == '__main__':
    testdict={"name":"jan","age":27,"sex":"man"}
    testlist=["jan",27,"man"]


    nginx_instance= Nginx(nginx_obj_dict=my_nginx_obj_dict)
    nginx_instance.check_main_conf_file()
    nginx_instance.check_file_path_is_under_main_file_dir()
    pid_file = nginx_instance.get_pid_file_path()
    backend_server_info_dict=nginx_instance.get_backend_server_info_dict()
    print(pid_file)




