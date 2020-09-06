# 一、指令

## v-cloak（用v-text代替）

- 示例

  ```
  <style>
  [v-cloak] {  
  
  display: none; 
  
  }
  </style>
  
  <div v-cloak>  
  
   {{ message }} 
  
  </div>
  ```

- 不推荐使用，用下面的v-text代替。

## v-text*

- 示例

  `<div v-text="msg"></div>`

## v-html

- 将带有html标签的纯文本解析后再填充。
- 存在安全问题，不推荐使用

## v-pre

- 示例

  `<div v-pre>{{msg}}</div>`

- 跳过编译，显示原始内容，用法比较少

## v-once

- 只渲染元素和组件一次。
- 应用场景：如果显示的信息后续不需要再修改，可以提高性能。

## v-model*

- 含义：

  数据和页面内容双向绑定，而默认是单向绑定，即模型中的数据改变会影响页面内容；而双向绑定时，修改页面内容也会影响模型中的数据。

- 应用场景：

  多用于表单控件中，与用户进行交互的场景。如：

  input、select标签

- MVVM设计思想：

  <img src="C:\Users\wakaka\AppData\Roaming\Typora\typora-user-images\image-20200828141722542.png" alt="image-20200828141722542" style="zoom:80%;" />

  1. M   --- model，提供数据

  2. V    --- view,即dom元素

  3. VM --- View-Model

     从视图到模型用dom监听，从模型到视图用数据绑定

- 底层实现原理：

  v-bind绑定属性，v-on绑定事件。两者结合实现双向v-model双向绑定

  `<input v-bind:value='msg' v-on:input="msg=$event.target.value">`

## v-on(@)*

- 缩写：@

- 示例：

  `<button v-on:click="num++">点击事件</button>`

  `<button @click='num++'>点击事件</button>`

- this ===  (var vm = new Vue())
- 函数调用时有两种方式，直接函数名调用和加括号调用：fun 和fun()

### 事件绑定

```
<div>
    <button v-on:click='handle1'>点击1</button>
    <button v-on:click='handle2(123,456,$event)'>点击2</button>
</div>

methods:{
	handle1: function() <==> function(event){  #默认会有一个event参数
		console.log(event.target.innerHTML)
	},
	handle2: function(p,p1,event){
		console.log(p,p1)
		console.log(envetn.target.tagName)   //获取事件所在标签名
		console.log(envetn.target.innerHTML) //获取事件所在标签内容
	}
}
```

1. 如果事件直接绑定函数名称，那么默认会传递事件对象作为事件函数的第一个参数。
2. 如果事件绑定函数调用，即函数名加括号的方式，那么事件对象必须作为最后一个参数显示传递，并且事件对象的名称必须是固定的名称：$event

### 事件修饰符

#### 1.冒泡示例：

```
<div>{{num}}</div>
<div v-on:click='handle0'>
    <button v-on:click='handle1'>点击1</button>
</div>

data:{
	num:0
}

methods:{
	handle0: function(){ 
		this.num++
	},
	handle1: function(){

	}
}
结果描述：点击1的时候 ，因为冒泡，出发了handle0，导致num值 +1。
```

#### 2.stop修饰符阻止冒泡：

```
<div>{{num}}</div>
<div v-on:click='handle0'>
    <button v-on:click.stop='handle1'>点击1</button>  //用vue方式：加一个stop修饰符
</div>

data:{
	num:0
}

methods:{
	handle0: function(){ 
		this.num++
	},
	handle1: function(){

	}
}
结果描述：点击1的时候，num不会自增。

以上操作等价于：
<div>{{num}}</div>
<div v-on:click='handle0'>
    <button v-on:click='handle1'>点击1</button>
</div>

data:{
	num:0
}

methods:{
	handle0: function(){ 
		this.num++
	},
	handle1: function(event){
	//阻止冒泡，传统js方式。
		event.stopPropagation()
	}
}
备注：.stop 其实是调用 event.stopPropagation()
```

#### 	3.prevent修饰符阻止事件：

```
<a href="http://www.baidu.com" v-on:click.prevent='handle3'>百度</a>  //prevent修饰符
methods:{
	handle3: function(event){

	}
}

以上操作等价于：
<a href="http://www.baidu.com" v-on:click='handle3'>百度</a>
methods:{
	handle3: function(event){
	//阻止默认行为，传统js方式。
		event.preventDefault()
	}
}
结果描述：点击上述a标签时不会跳转到百度。
备注：.prevent 其实是调用 event.preventDefault()
```

#### 4.keyup按键修饰符：

```
原生通过点击的放式:
<form action="">
    <div>
    用户名：<input type="text">
    </div>
    <div>
    密码：<input type="text">
    </div>
	<input type="button" v-on:click="handleSubmit" value="提交"> //点击提交按钮时提交
</form>

methods:{
	handleSubmit: function(){
		console.log(1)
	}
}

增强用户体验，添加回车修饰符：
<form action="">
    <div>
    用户名：<input type="text">
    </div>
    <div>
    密码：<input v-on:keyup.enter.native="handleSubmit"  type="text">  //按回车键时提交
    </div>
	<input type="button" v-on:click="handleSubmit" value="提交"> //点击提交按钮时提交
</form>

methods:{
	handleSubmit: function(){
		console.log(1)
	}
}

```

#### 5.自定义按键修饰符：

##### 5.1获取按键对应的ascii码：

```
<input type="text" v-on:keyup="handle">

methods:{
	handle: function(event){
		console.log(event.keyCode)
	}
}
```

##### 	5.2使用相应的按键修饰符：

```
<input type="text" v-on:keyup.space="handle">
或者
<input type="text" v-on:keyup.65="handle">

Vue.config.keyCodes.space= 65   //这里给空格键起别名，65是空格键

var vm= new Vue()
methods:{
	handle: function(event){
		console.log(event.keyCode)
	}
}
```

#### 6.串联修饰符：

`<!--  串联修饰符 --> <button @click.stop.prevent="doThis"></button>`

#### 7.鼠标修饰符：

```
.left - (2.2.0) 只当点击鼠标左键时触发。
.right - (2.2.0) 只当点击鼠标右键时触发。
.middle - (2.2.0) 只当点击鼠标中键时触发。
```

parseInt(str):将字符串转成数字类型。

## v-bind(:)*

- 缩写：:

### 1.属性绑定:

```
<a v-bind:href="url">百度</a>

data:{
url:'http:/www.baidu.com'
}
```

### 2.样式绑定：

#### 2.1class样式处理

- 对象语法

  ```
  <style>
  .className1 {
  border: 1px,
  with:
  height:
  }
  .className2 {}
  </style>
  
  <div v-bind:class="{className1:isActive1,className2:isactive2}"></div>
  
  data: {
  isActive1:true,
  isActive2:true
  }
  ```

- 数组语法

  ```
  <style>
  .className3 {}
  .className4 {}
  </style>
  
  <div v-bind:class="[classVar3, classVar4]"></div>
  
  data: {
  	classVar3:className3,
  	classVar4:className4
  }
  ```

- 数组中可以嵌套对象来使用。

  `v-bind:class="[classVar3, classVar4, {className1:isActive1}]"`

- 简化操作

  ```
  数组简化
  <div v-bind:class="arrClasses"></div>
  
  data:{
  	arrClasses:[className3,className4]
  }
  ```

  ```
  对象简化
  <div v-bind:class="objClasses"></div>
  
  data:{
  	objClasses:{className1:true,className2:true}
  }
  ```

#### 2.2style样式处理

- 对象语法

  ```
  <div v-bind:style="{border:borderStyle, width:widthStyle, height:heightStyle}"></div>
  
  data:{
  	borderStyle: '1px solid blue',
  	widthStyle: '100px',
  	heightStyle: '200px'
  }
  ```

  

- 数组语法

  ```
  <div v-bind:style="[style1,style2]"></div>
  
  data: {
  	style1: {
  		borderStyle: '1px solid blue',
  		backgroundColor: 'blue'
  	}
  	style2: {widthStyle: '100px'}
  }
  ```

- 简化操作

  ```
  对象简化
  <div v-bind:style="objStyles"></div>
  
  data:{
  	objstyles:{
  		borderStyle: '1px solid blue',
  		widthStyle: '100px',
  		heightStyle: '200px'
  	}
  }
  ```

## v-if*

## v-show

示例：

v-if与v-show的区别：

- v-show控制元素是否显示(已经渲染到页面)
- v-if 控制元素是否渲染到页面

总结：v-if不满足条件不会渲染。v-show会先渲染，然后根据display的值决定要不要显示

## v-for*

- 遍历数组：

  ```
  没有索引：
  <div>水果列表</div>
  <ul>
  	<li v-for="item in fruits" >{{item}}</li>
  </ul>
  
  data:{
  fruits: ['apple', 'orange', 'banana']
  }
  ```

  ```
  添加索引：
  <div>水果列表</div>
  <ul>
  	<li v-for="(item,index) in fruits">{{item}}---{{index}}</li>
  </ul>
  
  data:{
  	fruits: ['apple', 'orange', 'banana']
  }
  ```

  ```
  添加key：
  <div>水果列表</div>
  <ul>
  	<li :key="index" v-for="(item,index) in objfruits">
  		<span>{{item.ename}}</span>
  		<span>---</span>
  		<span>{{item.cname}}</span>
  	</li>
  </ul>
  
  data:{
  	objfruits: [{
  	ename:'apple',
  	cname:'苹果'
  	},{
  	ename:'orange',
  	cname:'橘子'
  	},{
  	ename:'banana',
  	cname:'香蕉'
  	},
  	]
  }
  ```

  ```
  如果被遍历的数据本身有唯一id，可以用数据的id绑定到key上：
  <div>水果列表</div>
  <ul>
  	<li :key="item.id" v-for="(item,index) in objfruits">
  		<span>{{item.ename}}</span>
  		<span>---</span>
  		<span>{{item.cname}}</span>
  	</li>
  </ul>
  
  data:{
  	objfruits: [{
  	id: 1,
  	ename: 'apple',
  	cname: '苹果'
  	},{
  	id: 2,
  	ename: 'orange',
  	cname: '橘子'
  	},{
  	id: 3,
  	ename: 'banana',
  	cname: '香蕉'
  	},
  	]
  }
  ```

- key的作用：
  - 帮助Vue区分不同的元素，从而提高性能。 key的名字是固定的，通过 :key来绑定key的值
  - 对我们开发来说其实没有任何影响
  - 建议所有的遍历都加上:key

- 遍历对象：

  ~~~
  <div :key='i' v-for="(v,k,i) in obj">{{v}}--{{k}}---{{i}}</div>
  
  data: {
  	obj:{
  	unmae:'lisi',
  	age:12,
  	gender:'male'
  	}
  }
  ~~~

  

# 二、Vue常用特性

## 1、表单操作

### 表单域修饰符：输入域

- number：专户为数值
- trim：去掉首位空格
- lazy：将input事件切换为change事件，即失去焦点时触发

```
<input v-model.number="age"  type="number">
<input v-model.trim="msg">
<input v-model.lazy="msg">
```

## 2、自定义指令

- 全局自定义指令示例：刷新页面，鼠标自动聚焦到input输入框。

```
<input type="text" v-foucs>

//定义指令，使用的时候用v-focus
Vue.directive('focus',{
	inserted: function(el){
		//el表示指令所绑定的元素
		el.foucs();
	}
});

var vm = new Vue()
```

- 带参数的自定义全局指令

~~~
<input type="text" v-color='msg'>
或者：
<input type="text" v-color='{color:'orange'}'>

//定义指令
Vue.directive('color',{
	bind: function(el,binding){
		//binding.name==='color',binding.value===msg
		console.log(binding)
		console.log(binding.value.color)
		//根据指令参数设置背景色
		el.style.backgroundColor = bind.value.color;
	}
});

var vm = new Vue(){
...
	data: {
	msg: {
		color:'orange'
	}
	}
}
~~~

- ​	自定义局部指令

  备注：跟自定义全局指令是一样的，只是换了个位置

~~~
var vm = new Vue({
	el:'#app',
	data:{},
	methods:{},
	directives:{
		color:{
		bind: function(el,binding){
		//binding.name==='color',binding.value===msg
		console.log(binding)
		console.log(binding.value.color)
		//根据指令参数设置背景色
		el.style.backgroundColor = bind.value.color;
	}
		}
	}
})

~~~

## 3、计算属性

- 示例：反转字符串

~~~
<div>{{reverseString}}</div>


data:{
	msg:'hello'
}，
computed:{
	reverseString: function(){
		return this.msg.split('').reverse().join('');
}
}
~~~

- 计算属性(computed)与方法(methods)的区别：
  - 计算属性是有缓存的, console.log里看到只打印一次
  - 方法不存在缓存

## 4、过滤器

## 5、侦听器

## 6、生命周期

- 挂载（初始化相关属性）
  1. beforeCreate
  2. created：实例创建完毕后立即调用
  3. beforeMount
  4. mounted：一旦挂在完成，表示实例初始化完毕
- 更新（元素或者组件的变更操作）
  1. beforeUpdate
  2. updated
- 销毁（销毁相关属性）
  1. beforeDestory
  2. destoryed

```
data:{}
beforeCreate: function(){
	console.log('beforeCreate')
},
created: function(){
	console.log('created')
},
beforeMount: function(){
	console.log('beforeMount')
},
mounted: function(){
	console.log('mounted')
},
beforeUpdate: function(){
	console.log('beforeUpdate')
},
updated: function(){
	console.log('updated')
},
beforeDestory: function(){
	console.log('beforeDestory')
},
destoryed: function(){
	console.log('destoryed')
}
```

# 三、Vue脚手架

## vue调试工具

1. 克隆仓库

   git clone https://github.com/vuejs/vue-devtools.git

2. 安装依赖包并构建 

   - npm install -g yarn
   - yarn install
   - yarn run build

3. 打开chrome扩展页面

4. 选中开发者模式

5. 加载已解压扩展，选择vue-devtools/packages/shell-chrome

## vue单文件组件的结构

- template：组件的模板区域
- script：业务逻辑区域
- style：样式区域 ----为每个style添加scoped指令，从而防止指令样式之间的冲突。scoped表示样式只在当前组件生效。没有scoped表示样式全局生效

## axios

- axios默认是发送json格式数据

- 要发送表单数据，必须通过 new URLSearchParams将字典进行转换。
- 将token保存到浏览器的sessinStorage 而不是 localStorage，因为localStorage是持久化的存储机制；sessinStorage 是会话的存储机制

## 路由导航守卫

//挂载路由导航守卫

router.beforeEach((to, from, next) => {

 //to 将要访问的路径

 //from 代表从哪个路径跳转而来

 //next 是一个函数，表示放行

 if (to.path === '/login') return next()

 //获取token

 const tokenStr = window.sessionStorage.getItem('access_token');

 if (!tokenStr) return next('/login');

 next()

})

## eslint语法格式化

在项目vue根目录下，创建一个文件： .prettierr，并且添加以下内容：

{
    "semi": false,
    "singleQuote": true
}

然后点击右键-->格式化文档

## element-ui按需导入

