<template>
<div>
    <!-- 面包屑导航-->
    <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{path: '/welcome'}">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{client_ip}}</el-breadcrumb-item>
        <el-breadcrumb-item>备份</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 分割线-->
    <el-divider></el-divider>
    <h1>此页面还在开发中</h1>
</div>
</template>

<script>
export default {
    data() {
        return {
            client_ip: ''
        }
    },
    mounted() {
        this.get_ip_from_router();
    },
    methods: {
        get_ip_from_router() {
            this.client_ip = this.$route.params.ip
        }
    }
}
</script>

<style lang="less" scoped>

</style>
