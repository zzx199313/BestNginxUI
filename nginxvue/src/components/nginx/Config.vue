<template>
<div>
    <!-- 面包屑导航-->
    <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{path: '/welcome'}">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{client_ip}}</el-breadcrumb-item>
        <el-breadcrumb-item>配置文件</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 分割线-->
    <el-divider></el-divider>
    <!--卡片区域-->
    <el-card class="box-card">
        <!-- 头部按钮-->
        <div slot="header" class="clearfix">
            <!-- nginx -t 按钮-->
            <el-button round type="primary" @click="checkNginxConf" :disabled="isdiabled_check_or_reload_nginx">nginx -t</el-button>
            <!-- nginx -s reload 按钮-->
            <el-button round type="success" @click="reloadNginxConf" :disabled="isdiabled_check_or_reload_nginx">nginx -s reload</el-button>
            <!-- 删除文件按钮-->
            <el-button style="font-size:15px; float: right; padding: 3px 20px" type="text" @click="dialogDelFileFormVisible = true" :disabled="isdisabled_create_or_delete">删除文件</el-button>
            <el-dialog title="删除文件" :visible.sync="dialogDelFileFormVisible">
                <el-form :model="create_or_delete_form">
                    <el-form-item>
                        <el-input v-model="create_or_delete_form.file_path" autocomplete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click="dialogDelFileFormVisible = false">取 消</el-button>
                    <el-button type="primary" @click="dialogDelFileFormVisible = false;deleteFile(create_or_delete_form.file_path)">确 定</el-button>
                </div>
            </el-dialog>
            <!-- 添加文件按钮-->
            <el-button style="font-size:15px; float: right; padding: 3px 20px" type="text" @click="dialogAddFileFormVisible = true" :disabled="isdisabled_create_or_delete">添加文件</el-button>
            <el-dialog title="添加文件" :visible.sync="dialogAddFileFormVisible">
                <el-form :model="create_or_delete_form">
                    <el-form-item>
                        <el-input v-model="create_or_delete_form.file_path" autocomplete="off"></el-input>
                    </el-form-item>
                </el-form>
                <div slot="footer" class="dialog-footer">
                    <el-button @click="dialogAddFileFormVisible = false">取 消</el-button>
                    <el-button type="primary" @click="dialogAddFileFormVisible = false;createNewFile(create_or_delete_form.file_path)">确 定</el-button>
                </div>
            </el-dialog>
        </div>
        <!-- 手风琴折叠面板区域-->
        <el-collapse accordion>
            <el-collapse-item :key="item.file_path" v-for="(item,index) in all_file_and_content_list" :name="item.file_path">
                <template slot="title">
                    {{item.file_path}}
                    <!--编辑icon是否显示-->
                    <i v-show="!isReadOnly[item.file_path]" class="el-icon-edit"></i>
                </template>
                <!-- 渲染表单-->
                <el-form :model="item">
                    <!-- 文本域-->
                    <el-form-item>
                        <el-input size="medium" rows="12" type="textarea" v-model="item.file_content" :readonly="isReadOnly[item.file_path]"></el-input>
                    </el-form-item>
                    <!-- 按钮 -->
                    <el-form-item style="text-align: center">
                        <!-- 编辑按钮 -->
                        <el-button type="primary" @click="editFileContent(item.file_path)">
                            编辑
                        </el-button>
                        <!-- 保存按钮 -->
                        <el-button type="success" @click="saveFileContent(item.file_path, item.file_content)" :disabled="isReadOnly[item.file_path]">
                            保存
                        </el-button>
                        <!-- 回退按钮 -->
                        <el-button type="info" @click="cancelSaveFileContent(index,item.file_path)" :disabled="isReadOnly[item.file_path]">
                            回退
                        </el-button>
                    </el-form-item>
                </el-form>
            </el-collapse-item>
        </el-collapse>
    </el-card>
</div>
</template>

<script>
import config from './config.js'
export default config
</script>

<style lang="less" scoped>
.el-icon-edit {
    margin-left: 10px;
}
</style>
