<template>
<div>
    <!-- 面包屑导航-->
    <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{path: '/welcome'}">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{client_ip}}</el-breadcrumb-item>
        <el-breadcrumb-item>upstreams</el-breadcrumb-item>
    </el-breadcrumb>
    <el-divider></el-divider>
    <!--卡片区域-->
    <el-card class="box-card">

        <el-row>
            <el-col :span="6">
                <!--搜索框-->
                <el-input placeholder="请输入upsream,支持模糊查找" v-model="upstream_name">
                    <el-button slot="append" icon="el-icon-search" @click="read_upstream_info(upstream_name)"></el-button>
                </el-input>
            </el-col>
            <el-col :span="4"></el-col>
        </el-row>
        <!--表格区域-->
        <el-table :data="all_backend_server_info_list" border stripe highlight-current-row style="color:black;">
            <el-table-column label="#" type="index"></el-table-column>
            <el-table-column label="upstream" prop="upstream"></el-table-column>
            <el-table-column label="backend_server_addr" prop="backend_server_addr"></el-table-column>
            <el-table-column label="当前状态" prop="status"></el-table-column>
            <!--添加插槽-->
            <el-table-column label=" 修改状态" icon="el-icon-edit">
                <template slot-scope="scope">
                    <!-- {{scope.row.status}} -->
                    <!-- 给up状态添加文字提示 -->
                    <el-tooltip class="item" effect="dark" content="将状态置为空" :enterable="false" placement="top">
                        <el-popconfirm title="确定将状态置为空吗？" @onConfirm="changeStatus(scope.row,'')">
                            <el-button v-show="!(scope.row.status == '')" type="success" circle size='small' slot="reference">up</el-button>
                        </el-popconfirm>
                    </el-tooltip>
                    <!-- 将状态改为down -->
                    <el-popconfirm title="确定将状态改为down吗？" @onConfirm="changeStatus(scope.row,'down')">
                        <el-button v-show="!(scope.row.status == 'down')" type="info" circle size='small' slot="reference">down</el-button>
                    </el-popconfirm>
                    <!-- 将状态改为backup -->
                    <el-popconfirm title="确定将状态改为backup吗？" @onConfirm="changeStatus(scope.row,'backup')">
                        <el-button v-show="!(scope.row.status == 'backup')" type="primary" circle size='small' slot="reference">backup</el-button>
                    </el-popconfirm>
                </template>
            </el-table-column>
            <el-table-column label="ping"></el-table-column>
        </el-table>
    </el-card>
</div>
</template>

<script>
export default {
    data() {
        return {
            client_ip: '',
            all_backend_server_info_list: [],
            upstream_name: '',
        }
    },
    mounted() {
        this.get_ip_from_router();
        this.read_all_backend_server_info(this.client_ip)
    },
    methods: {
        get_ip_from_router() {
            this.client_ip = this.$route.params.ip
        },
        //初始化upstream页面
        async read_all_backend_server_info(client_ip) {
            const {
                data: all_backend_server_info_list
            } = await this.$http.get('/nginx/backend_server/readAll', {
                params: {
                    client_ip: client_ip,
                }
            })
            this.all_backend_server_info_list = all_backend_server_info_list
        },
        //根据upstream的名字过滤数据
        async read_upstream_info(upstream_name) {
            const {
                data: upstream_info_list
            } = await this.$http.get('/nginx/backend_server/readUpstream', {
                params: {
                    client_ip: this.client_ip,
                    upstream: upstream_name
                }
            })
            // console.log(upstream_info_list)
            this.all_backend_server_info_list = upstream_info_list
        },
        //修改backend server 的状态
        async changeStatus(backend_server_info, status) {
            console.log(backend_server_info)
            let params = {
                client_ip: this.client_ip,
                file_path: backend_server_info.file_path,
                backend_server_addr: backend_server_info.backend_server_addr,
                status: status
            }
            const {
                data: res
            } = await this.$http.post('/backend_server/status/update', params)
            // console.log(res)
            if (res.status !== 200) return this.$message.error(res.msg)
            backend_server_info.status = status
            // this.read_upstream_info(backend_server_info.upstream)
            // this.$message.success(res.msg)
        },

    },
}
</script>

<style lang="less" scoped>

</style>
