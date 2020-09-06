export default {
    // name: 'Config',
    data() {
        return {
            client_ip: '',
            // file_path_list: [],
            file_path_dir_dict_list: [],
            editing_file_path_list: [],           
            all_file_and_content_list: [],
            //当点击编辑时不可执行nginx -t 和nginx -s reload
            isdiabled_check_or_reload_nginx: false,
            //当点击编辑时不可执行添加或删除文件
            isdisabled_create_or_delete: false,
            //文件是否只读,当点击编辑按钮时变为可写,且激活保存按钮、取消按钮
            isReadOnly: {},
            //文件被修改时，触发浏览器刷新和路由跳转事件监听
            modified: {},
            //添加目录和文件对话框
            dialogDelFileFormVisible: false,
            dialogAddFileFormVisible: false,
            create_or_delete_form: {
                file_path: '/etc/nginx/conf.d/',
            },
        }
    },
    mounted() {
       
        //从路由参数中获取ip
        this.get_ip_from_router()
        //获取当前client_ip的配置文件内容
        this.read_all_file(this.client_ip)
        //监听页面刷新和关闭事件,
        window.addEventListener('beforeunload', e => this.beforeunloadHandler(e))
    },
    //同组件不同路由跳转时调用
    beforeRouteUpdate(to, from, next) {
        let obj = this.modified
        let true_num = 0
        Object.keys(obj).forEach(function (key) {
            if (obj[key] === true) {
                true_num += 1
            }
        })
        if (true_num === 0) {
            next();
            return;
        }
        this.$confirm('当前页面数据未保存，确定要离开？', '提示', {
                type: 'warning'
            })
            .then( () => {                    
                next();
            })
            .catch(() => {
                next(false);
            });
    },
    //导航离开组件时调用
    beforeRouteLeave(to, from, next) {
        let obj = this.modified
        let true_num = 0
        Object.keys(obj).forEach(function (key) {
            if (obj[key] === true) {
                true_num += 1
            }
        })
        if (true_num === 0) {
            next();
            return;
        }
        this.$confirm('当前页面数据未保存，确定要离开？', '提示', {
                type: 'warning'
            })
            .then(() => {           
                next();
            })
            .catch(() => {
                next(false);
            });
    },
     destroyed() {
       
        //组件卸载的时候销毁对onbeforeunload事件的监听
        window.removeEventListener('beforeunload', e => this.beforeunloadHandler(e))     
    },

    methods: {

        beforeunloadHandler(e) {
            let obj = this.modified
            let true_num = 0
            Object.keys(obj).forEach(function (key) {
                if (obj[key] === true) {
                    true_num += 1
                }
            })
            if (true_num === 0) {
                return;
            }
            // 通知浏览器不要执行与事件关联的默认动作
            e.preventDefault();
            // Chrome 需要 returnValue 被设置成空字符串
            e.returnValue = '';
        },

        //初始化页面：获取路由参数中的ip
        get_ip_from_router() {
            this.client_ip = this.$route.params.ip
        },
        //初始化页面：获取当前ip的所有文件内容
        async read_all_file(client_ip) {             
            const {
                data: all_file_and_content_list
            } = await this.$http.get('/nginx/conf/readAll',{
                    params : {
                        client_ip: client_ip,
                    }
            })

            this.all_file_and_content_list = all_file_and_content_list
            console.log(this.all_file_and_content_list)

            //遍历this.all_file_and_content_list,初始化按钮状态，生成文件父目录路径的列表
            let isReadOnly = {}
            let modified ={}
            let file_path_dir_list =[]
            let file_path_dir_dict_list = []
            all_file_and_content_list.forEach(function(item,index){
                let file_path = item.file_path
                //禁用保存、取消按钮，不显示编辑图标
                isReadOnly[file_path] = true
                //将浏览器刷新、路由跳转检测置为false
                modified[file_path] = false
                //生成文件父目录路径列表
                let file_path_dir_dict ={}
                let file_path_dir = file_path.split('/').slice(0, -1).join('/') + '/'
                file_path_dir_dict['file_path_dir'] = file_path_dir
                let result = file_path_dir_list.includes(file_path_dir)
                if (!result) {
                    file_path_dir_list.push(file_path_dir)
                    file_path_dir_dict_list.push(file_path_dir_dict)
                }                
            })           
            this.isReadOnly = isReadOnly
            this.modified = modified
            this.file_path_dir_dict_list = file_path_dir_dict_list
            // console.log(this.file_path_dir_dict_list)
        },
        //刷新所有配置文件内容
        async fresh_all_file_content(){
            const {
                data: all_file_and_content_list
            } = await this.$http.get('/nginx/conf/readAll', {
                params: {
                    client_ip: this.client_ip,
                }
            })
            this.all_file_and_content_list = all_file_and_content_list
        },
        //刷新指定文件的配置文件内容
        async fresh_single_file_content(index,client_ip,file_path) {
            const {
                data: res
            } = await this.$http.get('/nginx_conf/read', {
                params: {
                    client_ip: client_ip,
                    file_path: file_path
                }
            })
            if (res.status !== 200) return this.$message.error(res.msg)
            this.all_file_and_content_list[index]['file_content'] = res.msg
            // this.$message.success(res.msg)
        },

        //检测nginx配置文件
        async checkNginxConf(){
            let params = {
                client_ip: this.client_ip
            }
            const {
                data: res
            } = await this.$http.post('/nginx_conf/check', params) 
            let str = res.join('<br/>')
            this.$alert(str, {
                dangerouslyUseHTMLString: true,               
                
            })
        },
        //重载nginx配置
        async reloadNginxConf(){
            let params = {
                client_ip: this.client_ip
            }
            const {
                data: res
            } = await this.$http.post('/nginx_conf/reload', params)
            if (res.status !== 200) return this.$alert(res.msg,{
                type: 'error',
            })
            this.$message.success(res.msg)
        },
        
        //添加文件
        async createNewFile(file_path){
            let params = {
                client_ip: this.client_ip,
                file_path: file_path
            }
            const {
                data: res
            } = await this.$http.post('/nginx_conf/create', params)
            if (res.status !== 200) return this.$alert(res.msg,{
                type:'error'
            })
            this.fresh_all_file_content()
            this.$message.success(res.msg)
        },
        //删除文件
        async deleteFile(file_path){
            let params = {
                client_ip: this.client_ip,
                file_path: file_path
            }
            const {
                data: res
            } = await this.$http.post('/nginx_conf/delete', params)
            if (res.status !== 200) return this.$alert(res.msg, {
                type: 'error'
            })
            this.fresh_all_file_content()
            this.$message.success(res.msg)
        },
        //编辑按钮
        editFileContent(file_path){
            //将正在编辑的文件记录到一个列表中
            this.editing_file_path_list.push(file_path)
            //将显示编辑icon、激活保存按钮、取消按钮；
            this.isReadOnly[file_path] = false
            //禁用 nginx -t 和nginx -s reload
            this.isdiabled_check_or_reload_nginx = true
            //编辑期间禁止添加、删除文件
            this.isdisabled_create_or_delete = true
            //开启刷新和路由跳转事件监听
            this.modified[file_path] = true

        },
        //保存按钮
        async saveFileContent(file_path, file_content){
            let params = {
                client_ip: this.client_ip,
                file_path: file_path,
                file_content: file_content
            }
            const {
                data: res
            } = await this.$http.post('/nginx_conf/update', params)
            if (res.status !== 200) return this.$alert(res.msg, {
                type: 'error'
            })
            //将文件从编辑列表中剔除
            this.editing_file_path_list.splice(this.editing_file_path_list.indexOf(file_path), 1)
            //隐藏编辑icon、禁用保存按钮、取消按钮；
            this.isReadOnly[file_path] = true
            //关闭刷新和路由跳转事件监听
            this.modified[file_path] = false
            //激活nginx -t 和 nginx -s reload 按钮
            this.isdiabled_check_or_reload_nginx = false
            //激活添加、删除文件按钮
            this.isdisabled_create_or_delete = false
            this.$message.success(res.msg)
        },
        //取消按钮
        async cancelSaveFileContent(index,file_path){
            let params = {
                client_ip: this.client_ip,
                file_path: file_path
            }
            const {
                data: res
            } = await this.$http.post('/nginx_conf/cancelUpdate', params)
            if (res.status !== 200) return this.$alert(res.msg, {
                type: 'error'
            })
            //将文件从编辑列表中剔除
            this.editing_file_path_list.splice(this.editing_file_path_list.indexOf(file_path), 1)
            //隐藏编辑icon、禁用保存按钮、取消按钮；
            this.isReadOnly[file_path] = true
            //关闭刷新和路由跳转事件监听
            this.modified[file_path] = false
            //激活nginx -t 和 nginx -s reload 按钮
            this.isdiabled_check_or_reload_nginx = false
            //激活添加、删除文件按钮
            this.isdisabled_create_or_delete = false
            //刷新页面
            // console.log(this.all_file_and_content_list[index])
            this.fresh_single_file_content(index,this.client_ip,file_path)
            // this.$message.success(res.msg)
        }

    },
}