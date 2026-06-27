# django_learning

Django development environment configured with a local Python virtual environment.

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m django --version
```

Current Django version:

```text
6.0.6
```

## 本地开发账号

Admin 后台地址：

```text
http://127.0.0.1:8000/admin/
```

超级用户：

```text
username: admin
password: admin123456
```

演示借阅用户：

```text
username: demo_borrower
password: demo123456
```

这些账号仅用于本地学习和开发。

## 学习大纲

这个项目按 MDN Django LocalLibrary 教程顺序实现。建议按下面顺序学习，每一部分都先看文件结构，再看请求从 URL 到视图、模板、数据库的流动。

1. 项目入口与启动流程
   - `manage.py`
   - `locallibrary/settings.py`
   - `locallibrary/urls.py`
2. Django 项目与应用的关系
   - 项目包：`locallibrary/`
   - 应用包：`catalog/`
   - `INSTALLED_APPS` 如何启用应用
3. URL 路由
   - 根路由如何分发到 `catalog.urls`
   - `catalog/urls.py` 如何把路径绑定到视图
   - URL name 如何被模板和代码反向引用
4. 数据模型
   - `catalog/models.py`
   - `Author`、`Book`、`Genre`、`Language`、`BookInstance`
   - 字段、外键、多对多、模型方法、权限
5. 数据库迁移
   - `catalog/migrations/`
   - `makemigrations` 和 `migrate` 的作用
6. Admin 后台
   - `catalog/admin.py`
   - 模型注册、列表展示、过滤、内联编辑
7. 视图层
   - `catalog/views.py`
   - 函数视图 `index`
   - 通用类视图 `ListView`、`DetailView`
   - 登录和权限 mixin
8. 模板层
   - `catalog/templates/base_generic.html`
   - 首页、列表页、详情页、表单页
   - 模板继承、模板变量、URL 反向解析
9. 静态文件
   - `catalog/static/css/styles.css`
   - `STATIC_URL`
   - `{% load static %}` 和 `{% static %}`
10. Session
    - 首页访问次数 `num_visits`
    - `request.session` 的读写
11. 认证与权限
    - `django.contrib.auth.urls`
    - 登录、退出、当前用户
    - `LoginRequiredMixin`
    - `PermissionRequiredMixin`
    - `@permission_required`
12. 表单
    - `catalog/forms.py`
    - `RenewBookForm`
    - 表单校验和错误提示
13. 测试
    - `catalog/tests.py`
    - 模型测试、表单测试、视图测试、权限测试
