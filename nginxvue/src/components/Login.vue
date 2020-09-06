<template>
<div class="login_container">
    <div>BestNginxUI</div>
    <div class="login_box">
        <!-- 头像区域 -->
        <div class="avatar_box">
            <img src="../assets/logo.png" alt="反对反对" />
        </div>
        <!-- 登录表单区域 -->
        <el-form ref="loginFormRef" :model="loginForm" :rules="loginFormRules" label-width="0px" class="login_form">
            <!-- 用户名 -->
            <el-form-item prop="username">
                <el-input v-model="loginForm.username" prefix-icon="iconfont icon-denglu-yonghuming"></el-input>
            </el-form-item>
            <!-- 密码 -->
            <el-form-item prop="password">
                <el-input show-password type="password" @keyup.enter.native="login" v-model="loginForm.password" prefix-icon="iconfont icon-denglu-mima"></el-input>
            </el-form-item>
            <!-- 按钮 -->
            <el-form-item class="btns">
                <el-button type="primary" @click="login">登录</el-button>
                <el-button type="info" @click="resetLoginForm">重置</el-button>
            </el-form-item>
        </el-form>
    </div>
</div>
</template>

<script>
export default {
    data() {
        return {
            loginForm: {
                username: '',
                password: '',
            },
            loginFormRules: {
                //验证用户名和密码是否合法
                username: [{
                    required: true,
                    message: '请输入用户名',
                    trigger: 'blur',
                }, ],
                password: [{
                    required: true,
                    message: '请输入密码',
                    trigger: 'blur',
                }, ],
            },
        }
    },
    methods: {
        //点击重置按钮，重置登陆表单
        resetLoginForm() {
            this.$refs.loginFormRef.resetFields()
        },
        login() {
            this.$refs.loginFormRef.validate(async (valid) => {
                // console.log(valid)  //true or false
                if (!valid) return
                const {
                    data: res
                } = await this.$http.post(
                    '/login',
                    new URLSearchParams(this.loginForm)
                )
                if (res.status !== 200) return this.$message.error(res.msg)
                this.$message.success('登录成功')
                window.sessionStorage.setItem('BestNginxUItoken', res.access_token)
                this.$router.push('/home')

            })
        },
    },
}
</script>

<style lang="less" scoped>
.login_container {
    background-color: #2b4b6b;
    height: 100%;
}

.login_box {
    width: 450px;
    height: 300px;
    background-color: #fff;
    border-radius: 3px;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}

.avatar_box {
    height: 130px;
    width: 130px;
    border: 1px solid #eee;
    border-radius: 50%;
    padding: 10px;
    box-shadow: 0 0 10px #ddd;
    position: absolute;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: #fff;

    img {
        height: 100%;
        width: 100%;
        border-radius: 50%;
        background-color: #eee;
    }
}

.btns {
    display: flex;
    justify-content: flex-end;
}

.login_form {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 0 20px;
    box-sizing: border-box;
}
</style>
