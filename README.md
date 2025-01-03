# 图书管理系统

一个使用Flask框架构建的简单图书管理系统Web应用。

## 主要页面

1. `/login` 用户登录
2. `/home` 主页面
3. `/home/search` 查找图书
4. `/home/add` 增加图书
5. `/home/delete` 删除图书
6. `/home/edit` 更改图书信息

## 运行步骤

1. 克隆仓库到本地：
    ```bash
    git clone https://github.com/Zhe-xue-shou/sql-homework.git
    cd sql-homework
    ```

2. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

3. 运行应用：
    ```bash
    python src/main.py
    ```

4. 在浏览器中打开 `http://127.0.0.1:5000` 查看应用。

## 文件结构

```
/d:/Code/SQL/
│
├── src/
│   |── main.py  # 主应用脚本
|   |── operations.py # 逻辑函数
|   |── orm.py  # 映射函数
│   └── templates/
│       ├── login.html  # 登录页面
│       ├── home.html  # 主页面
│       ├── search/  # 查找图书
│       ├── add/  # 增加图书
│       ├── delete/  # 删除图书
│       └── edit/  # 更改图书信息
│
└── requirements.txt  # 依赖文件
```
