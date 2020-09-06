<template>
<el-container class="home-container">
    <!-- 头部区域  -->
    <el-header>
        <div @click="backHome">
            <img src="../assets/IAMI.png" alt="">
            <span>BestNginxUI</span>
        </div>
        <el-button type="info" @click="logout">退出</el-button>
    </el-header>
    <!-- 页面主体区域  -->
    <el-container>
        <!-- 侧边栏  -->
        <el-aside :width="isCollapse ? '64px':'200px'">
            <!-- 点击折叠与展开  -->
            <div class="toggle-button" @click="toggleCollp">|||</div>
            <!-- 侧边栏菜单  -->
            <el-menu :default-active="activePath" router :collapse="isCollapse" :collapse-transition="false" unique-opened background-color="#99CCCC" text-color="black" active-text-color="#9933FF">
                <!-- 一级菜单  -->
                <el-submenu :index="client_ip" :key="client_ip" v-for="client_ip in client_ip_list">
                    <!-- 模板区域  -->
                    <template slot="title">
                        <!-- 图标 -->
                        <i class="iconfont icon-nginx"></i>
                        <!-- 文本  -->
                        <span>{{client_ip}}</span>
                    </template>
                    <!-- 二级菜单  -->
                    <el-menu-item :index=" '/' +client_ip +'/config'" @click="saveNavState('/' +client_ip +'/config')">
                        <!-- 模板区域  -->
                        <template slot="title">
                            <!-- 图标 -->
                            <i class="iconfont icon-wenjian"></i>
                            <!-- 文本  -->
                            <span>配置文件</span>
                        </template>
                    </el-menu-item>
                    <el-menu-item :index=" '/' +client_ip +'/upstreams'" @click="saveNavState('/' +client_ip +'/upstreams')">
                        <!-- 模板区域  -->
                        <template slot="title">
                            <!-- 图标 -->
                            <i class="iconfont icon-icon-test"></i>
                            <!-- 文本  -->
                            <span>upstream管理</span>
                        </template>
                    </el-menu-item>
                    <el-menu-item :index="'/' +client_ip +'/backup'" @click="saveNavState('/' +client_ip + '/backup')">
                        <!-- 模板区域  -->
                        <template slot="title">
                            <!-- 图标 -->
                            <i class="iconfont icon-lishi"></i>
                            <!-- 文本  -->
                            <span>备份</span>
                        </template>
                    </el-menu-item>
                </el-submenu>
            </el-menu>
        </el-aside>
        <!-- 右侧内容主体  -->
        <el-main :style="{left:leftStyle}">
            <!-- 路由占位符 -->
            <router-view :key="key"></router-view>
        </el-main>
    </el-container>
</el-container>
</template>

<script>
export default {
    data() {
        return {
            client_ip_list: {},
            isCollapse: false,
            leftStyle: '200px',
            activePath: '',

        }

    },
    created() {
        this.activePath = window.sessionStorage.getItem('activePath')
        this.get_client_ip_list()
    },
    computed: {
        //路由复用同一个组件时，重新加载页面。
        key() {
            return this.$route.name !== undefined ? this.$route.name + new Date() : this.$route + new Date()
        }
    },
    methods: {
        logout() {
            window.sessionStorage.clear()
            this.$router.push('/login')
        },
        async get_client_ip_list() {
            const {
                data: res
            } = await this.$http.get('get_client_ip_list')
            if (res === []) return this.$message.error('获取ip列表失败！')
            this.client_ip_list = res
            // console.log(res)
        },
        //点击按钮，实现菜单的折叠与展开
        toggleCollp() {
            this.isCollapse = !this.isCollapse
            if (this.isCollapse === true) {
                this.leftStyle = '64px'
            } else {
                this.leftStyle = '200px'
            }
        },
        //点击左上角图标跳回首页
        backHome() {
            this.$router.push('/welcome')
        },
        //保存菜单激活状态
        saveNavState(activePath) {
            window.sessionStorage.setItem('activePath', activePath)
            this.activePath = activePath
        }
    }
}
</script>

<style lang="less" scoped>
.home-container {
    height: 100%;
}

.el-header {
    position: relative;
    width: 100%;
    background-color: #339999;
    display: flex;
    justify-content: space-between;
    padding-left: 0;
    align-items: center;
    color: #fff;
    font-size: 20px;

    >div {
        display: flex;
        align-items: center;

        img {
            width: 60px;
            height: 60px;
        }

        span {
            margin-left: 15px;
        }
    }

}

.el-aside {
    display: block;
    position: absolute;
    left: 0;
    top: 60px;
    bottom: 0;
    background-color: #99CCCC;

    .el-menu {
        border-right: none;
    }
}

.el-main {
    position: absolute;
    right: 0;
    top: 60px;
    bottom: 0;
    overflow-y: scroll;
    background-color: #EAEDF1;
}

.iconfont {
    margin-right: 10px;
}

.toggle-button {
    background-color: #99CCFF;
    font-size: 10px;
    line-height: 24px;
    text-align: center;
    letter-spacing: 0.2em;
    cursor: pointer;
}
</style>
