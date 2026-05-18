# ZBlog — 个人博客系统

基于 Django + Vue3 构建的个人博客系统，包含博客前台、管理后台、AI 聊天机器人和资源分享功能。

## 技术栈

### 后端
- **Django 6.0** + **Django REST Framework 3.16** — RESTful API
- **Simple JWT 5.5** — 基于 JWT 的用户认证
- **MySQL** — 主数据库（mysqlclient 2.2）
- **LangChain 1.3** + **LangGraph** — AI Agent 框架
- **LangGraph Checkpoint SQLite** — Agent 对话状态持久化
- **OpenAI API** — LLM 模型调用

### 前端
- **Vue 3.5** (Composition API + `<script setup>`)
- **Vue Router 5** — 路由管理
- **Pinia 3** — 状态管理
- **Element Plus 2.14** — UI 组件库
- **md-editor-v3** — Markdown 渲染（代码高亮）
- **Chart.js** + **vue-chartjs** — 数据图表
- **Vite 8** — 构建工具

## 项目结构

```
zblog/
├── zblog-master/                 # Django 后端
│   ├── config/                   # 项目配置（URL路由、settings）
│   ├── article/                  # 文章应用
│   │   ├── models.py             # Article、Category、Tag、Comment、Like
│   │   ├── serializers/          # 序列化器（列表/详情/评论）
│   │   ├── views/                # C端公开视图 + S端管理视图
│   │   ├── services/             # 业务逻辑层
│   │   └── urls.py               # 路由（/api/articles/c/、/api/articles/s/）
│   ├── user/                     # 用户应用
│   │   ├── views.py              # 注册、登录、用户信息
│   │   ├── serializers.py        # 用户序列化器
│   │   ├── captcha.py            # 图形验证码
│   │   ├── email_verification.py # 邮箱验证码
│   │   ├── permissions.py        # 权限控制
│   │   └── throttling.py         # 请求限流
│   ├── chat_robot/               # 聊天机器人应用
│   │   ├── agent.py              # LangGraph Agent 初始化
│   │   ├── models.py             # ChatMessage 模型（MySQL持久化）
│   │   ├── views.py              # SSE流式响应、历史管理
│   │   ├── tools.py              # Agent 工具（天气、搜索等）
│   │   ├── prompts.py            # System Prompt 定义
│   │   └── speak.py              # TTS 语音合成
│   ├── link/                     # 资源链接应用
│   │   ├── models.py             # ResourceLink 模型
│   │   └── views/                # C端列表 + S端CRUD
│   └── tools/                    # 工具模块（UUID v7 生成器等）
│
├── zblog-vue-c/                  # Vue3 C端（博客前台）
│   └── src/
│       ├── views/                # 页面组件
│       │   ├── HomeView.vue      # 首页
│       │   ├── ArticleListView.vue     # 文章列表
│       │   ├── ArticleDetailView.vue   # 文章详情
│       │   ├── ChatView.vue      # AI 聊天
│       │   └── ResourceView.vue  # 资源分享
│       ├── components/           # 公共组件
│       │   ├── ArticleCard.vue   # 文章卡片
│       │   ├── ArticleTOC.vue    # 文章目录
│       │   ├── AuthModal.vue     # 登录/注册弹窗
│       │   ├── CommentForm.vue   # 评论表单
│       │   ├── Pagination.vue    # 分页
│       │   └── SiteFooter.vue   # 页脚
│       ├── stores/auth.js        # 认证状态管理
│       ├── router/index.js       # 路由配置（含鉴权守卫）
│       └── api/index.js          # API 请求封装
│
└── zblog-vue-s/                  # Vue3 S端（管理后台）
    └── src/
        ├── views/                # 管理页面
        │   ├── DashboardView.vue       # 仪表盘
        │   ├── ArticleManageView.vue   # 文章管理
        │   ├── ArticleEditView.vue     # 文章编辑
        │   ├── TagManageView.vue       # 标签管理
        │   ├── CategoryManageView.vue  # 分类管理
        │   ├── CommentManageView.vue   # 评论管理
        │   ├── UserManageView.vue      # 用户管理
        │   ├── ChatManageView.vue      # 聊天记录管理
        │   ├── ResourceManageView.vue  # 资源链接管理
        │   └── LoginView.vue           # 登录
        ├── api/                  # API 模块（按资源拆分）
        ├── components/AdminLayout.vue  # 管理端布局
        └── router/index.js       # 路由配置
```

## 功能特性

### 博客前台（C端）
- 文章列表（分页、标签、分类筛选）
- 文章详情（Markdown 渲染 + 代码高亮 + 目录导航）
- 公开文章与私密文章（需密码验证）
- 评论系统（支持回复，需登录）
- 点赞/取消点赞（幂等操作）
- AI 聊天机器人（SSE 流式响应，需登录且有权限）
- 资源链接分享页（响应式卡片网格）

### 管理后台（S端）
- 数据仪表盘（Chart.js 图表）
- 文章 CRUD（Markdown 编辑器 + 实时预览）
- 标签、分类管理
- 评论管理（查看、删除）
- 用户管理
- 聊天记录管理（按用户查看、清除、裁剪）
- 资源链接管理（增删改查 + 搜索）

### 聊天机器人
- 基于 LangGraph 的 Agent 架构
- 工具调用（天气查询、网络搜索等）
- 对话摘要中间件（4000 token 触发，保留最近 20 条消息）
- MySQL + SQLite 双写持久化
- SSE 流式响应

## 数据库设计

所有表主键使用 UUID v7（去除连字符，32 位十六进制字符串）。

### 核心表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `article` | 文章 | title, slug, content_md, content_html, cover, status, view_count, like_count, comment_count, author, category, tags, published_at |
| `article_category` | 文章分类 | name |
| `article_tag` | 文章标签 | name, color |
| `article_tags` | 文章-标签关联 | article_id, tag_id |
| `article_comment` | 文章评论 | article, author, parent(自引用), content |
| `article_like` | 文章点赞 | article, user (唯一约束) |
| `chat_messages` | 聊天记录 | user, role (human/ai), content, token_count |
| `link_link` | 资源链接 | name, url, image_url, color, description |
| `auth_user` | 用户 | Django 内置 User 模型 |

### 文章状态
- `draft` — 草稿（仅 S 端可见）
- `published` — 已发布（C 端可见）
- `private` — 私密（C 端列表可见，详情需验证作者密码）

## 快速开始

### 环境要求
- Python 3.12+
- Node.js 22.12+
- MySQL 8.0+

### 后端配置

```bash
cd zblog-master

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建 config/settings.py（参考下方模板，配置数据库等信息）

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver 8000
```

### 前端配置

```bash
# C 端（博客前台）
cd zblog-vue-c
npm install
npm run dev        # 开发模式
npm run build      # 生产构建

# S 端（管理后台）
cd zblog-vue-s
npm install
npm run dev        # 开发模式
npm run build      # 生产构建
```

### 环境变量

需在 `zblog-master/config/settings.py` 中配置以下关键项：

- `SECRET_KEY` — Django 密钥
- `DATABASES` — MySQL 数据库连接信息
- `OPENAI_API_KEY` — LLM API 密钥
- `OPENAI_BASE_URL` — LLM API 地址

## API 概览

### 公开接口（C端）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/articles/c/list/` | 文章列表（分页） |
| GET | `/api/articles/c/<id>/` | 文章详情 |
| POST | `/api/articles/c/<id>/verify/` | 私密文章密码验证 |
| POST | `/api/articles/c/comments/` | 创建评论（需登录） |
| POST | `/api/articles/c/<id>/like/` | 点赞（需登录） |
| DELETE | `/api/articles/c/<id>/like/` | 取消点赞（需登录） |
| POST | `/api/auth/register/` | 用户注册 |
| POST | `/api/auth/login/` | 用户登录 |
| GET | `/api/auth/me/` | 当前用户信息 |
| POST | `/api/auth/send-code/` | 发送邮箱验证码 |
| GET | `/api/auth/captcha/` | 获取图形验证码 |
| POST | `/api/chat-robot/stream/` | 聊天流式响应（需登录） |
| GET | `/api/chat-robot/history/` | 聊天历史（需登录） |
| GET | `/api/links/c/links/` | 资源链接列表 |

### 管理接口（S端）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/articles/s/articles/` | 文章列表/创建 |
| GET/PUT/DELETE | `/api/articles/s/articles/<id>/` | 文章详情/更新/删除 |
| GET/POST | `/api/articles/s/tags/` | 标签列表/创建 |
| GET/PUT/DELETE | `/api/articles/s/tags/<id>/` | 标签详情/更新/删除 |
| GET/POST | `/api/articles/s/categories/` | 分类列表/创建 |
| GET/PUT/DELETE | `/api/articles/s/categories/<id>/` | 分类详情/更新/删除 |
| GET | `/api/articles/s/comments/` | 评论列表 |
| DELETE | `/api/articles/s/comments/<id>/` | 删除评论 |
| GET | `/api/chat-robot/users/` | 聊天用户列表 |
| GET | `/api/chat-robot/users/<id>/` | 用户聊天详情 |
| DELETE | `/api/chat-robot/users/<id>/clear/` | 清除用户聊天记录 |
| DELETE | `/api/chat-robot/users/<id>/trim/` | 裁剪用户聊天记录 |
| GET/POST | `/api/links/s/links/` | 资源链接列表/创建 |
| GET/PUT/DELETE | `/api/links/s/links/<id>/` | 资源链接详情/更新/删除 |

## License

MIT
