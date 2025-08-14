# Twitter AI 监控系统

这是一个集成了AI功能和Web界面的Twitter推文监控系统，可以实时监控指定账号的新推文，并使用AI对推文进行翻译、解读和标题生成。

## 功能特点

### 核心功能
- 🔍 **实时监控**: 定时检查指定Twitter账号的新推文
- 🤖 **AI处理**: 对每条推文进行翻译、深度解读和标题生成
- 💾 **数据存储**: 自动保存处理结果到JSON文件（按天存储）
- ⚡ **多账号支持**: 可同时监控多个Twitter账号
- 🛡️ **错误处理**: 包含完善的错误处理和API限流保护
- 🚫 **过滤功能**: 可选择是否排除回复类推文

### Web界面功能
- 🌐 **可视化界面**: 基于Flask的现代化Web界面
- 📋 **卡片展示**: 以卡片形式展示推文标题、翻译内容、作者和时间
- 🔍 **筛选功能**: 支持按作者和发布时间筛选推文
- 📖 **详情页面**: 点击卡片查看完整的AI翻译、解读和原文链接
- ⚙️ **设置中心**: 可视化配置API密钥和监控参数
- 📊 **监控控制**: 启动/停止监控，实时查看运行状态
- 🕒 **时区转换**: 自动将UTC时间转换为北京时间显示

## 快速开始



#### 通用Python脚本
1. **安装依赖包**：
   ```bash
   pip install -r requirements.txt
   ```
2. **启动Web界面**：
```bash
python start.py
```



3. **访问系统**：
   打开浏览器访问 `http://localhost:5000`

## 使用指南

### 首次配置

1. 访问 `http://localhost:5000/settings` 设置页面
2. 填入以下配置：
   - **Twitter API Key**: 从 [TwitterAPI.io](https://twitterapi.io) 获取
   - **大模型URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
   - **大模型API Key**: 从 [阿里云通义千问](https://dashscope.aliyuncs.com) 获取
   - **监控账号**: 如 `OpenAI, elonmusk, github`
   - **检查间隔**: 建议300秒（5分钟）
   - **回溯时间**: 首次运行建议1-2小时
   - **是否排除回复**: 选择是否监控回复类推文

3. 点击"保存配置"
4. 点击"启动监控"

### 主要功能

#### 首页
- 查看所有监控到的推文卡片
- 使用筛选器按作者或日期筛选
- 点击卡片进入详情页

#### 推文详情页
- 查看AI生成的标题
- 阅读AI翻译的中文内容
- 了解AI深度解读分析
- 查看原文和链接到Twitter

#### 设置页面
- 配置API密钥和参数
- 控制监控的启动和停止
- 查看监控运行状态

## 文件结构

```
AI-NES/
├── app.py                    # Flask主应用
├── twitter_ai_monitor.py     # 核心监控逻辑
├── start.py                  # Python启动脚本
├── run.bat                   # Windows启动脚本
├── run.sh                    # Linux/Mac启动脚本
├── requirements.txt          # 依赖包列表
├── config.json               # 配置文件（自动生成）
├── clean_duplicates.py       # 数据去重工具
├── llm.py                    # 大模型调用接口
├── tweets.py                 # 基础推文获取模块
├── templates/                # HTML模板
│   ├── base.html
│   ├── index.html
│   ├── tweet_detail.html
│   ├── settings.html
│   └── status_widget.html
├── static/                   # 静态资源
│   ├── css/style.css
│   └── js/app.js
└── data/                     # 数据存储目录
    └── tweets_YYYY-MM-DD.json
```

## 数据存储

- 推文数据按天存储在 `data/` 目录下
- 文件格式：`tweets_YYYY-MM-DD.json`
- 每条推文包含：
  - 作者、发布时间、原文
  - AI标题、翻译、解读
  - 推文链接和处理时间
- 自动备份和去重功能，保证数据完整性

## API要求

- **TwitterAPI.io**: 用于获取Twitter推文数据
- **阿里云通义千问**: 用于AI翻译、解读和标题生成

## 注意事项

- 建议检查间隔设置为300秒或以上，避免API限制
- 确保API密钥有效且有足够的调用额度
- Web界面支持Chrome、Firefox、Safari等现代浏览器
- 系统会自动创建必要的目录和配置文件
- 数据文件支持自动去重，避免重复存储相同推文

## 故障排除

### 常见问题

1. **无法启动Web服务**
   - 检查端口5000是否被占用
   - 确认Flask已正确安装

2. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 检查API调用额度

3. **无法获取推文**
   - 确认TwitterAPI.io密钥有效
   - 检查监控的账号名称是否正确

4. **AI处理失败**
   - 检查大模型API配置
   - 确认有足够的调用额度

### 数据维护

如需清理重复数据，可运行：
```bash
python clean_duplicates.py
```

### 技术支持

如遇到问题，请检查：
- Python版本（建议3.7+）
- 依赖包是否正确安装
- 配置文件是否正确
- 网络连接和防火墙设置

## 更新日志

- **v2.1**: 增加数据去重功能、排除回复选项、北京时间显示
- **v2.0**: 新增Web界面、数据存储、可视化配置
- **v1.0**: 基础命令行监控功能 