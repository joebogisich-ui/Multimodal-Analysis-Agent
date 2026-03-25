---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402201f38e53b93cf0da84dadfd98e45575ad314d2a19be72354221c5df73e943dbce02207fab877a277de47afae13edf9b75786f86dcd1c33ff6fce04d1116fb46f6bbb5
    ReservedCode2: 3046022100d537e3ae0758b0db3dc5ecc1ceb1ba02bff571bf20ebb4228f4c782a77e578d6022100be5b150231910fb3261202714a009a783e0dd30a4ede522e7de2a46cc6b9ea6b
---

# 贡献指南

感谢您对多模态数据分析可视化 Agent 系统的关注！我们非常欢迎各种形式的贡献，包括但不限于代码提交、文档改进、问题报告等。

## 开发环境设置

### 前置要求

- Python 3.10+
- Node.js 18.0+
- npm 或 yarn

### 安装步骤

1. 克隆项目仓库：
```bash
git clone https://github.com/yourusername/multimodal-analysis-agent.git
cd multimodal-analysis-agent
```

2. 设置后端环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

3. 设置前端环境：
```bash
cd frontend
npm install
```

## 开发工作流程

### 分支管理

我们采用 Git Flow 工作流：

- `main` 分支：稳定版本，只接受来自 `develop` 或 `hotfix` 分支的合并
- `develop` 分支：开发主分支，所有新功能都基于此分支开发
- `feature/*` 分支：功能分支，从 `develop` 分支创建
- `hotfix/*` 分支：紧急修复分支，从 `main` 分支创建

创建功能分支：
```bash
git checkout develop
git checkout -b feature/your-feature-name
```

### 代码规范

#### Python 代码规范

- 遵循 PEP 8 风格指南
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 所有公共函数和类必须有文档字符串

#### JavaScript/TypeScript 代码规范

- 遵循 ESLint 配置规则
- 使用 Prettier 进行代码格式化
- 组件使用 PascalCase 命名
- 工具函数使用 camelCase 命名

### 提交规范

提交信息应遵循 Conventional Commits 规范：

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

类型标识：
- `feat`：新功能
- `fix`：错误修复
- `docs`：文档更新
- `style`：代码格式（不影响代码运行的变动）
- `refactor`：重构（既不是新功能也不是错误修复）
- `test`：测试相关
- `chore`：构建过程或辅助工具的变动

示例：
```
feat(analyzer): 添加聚类分析功能

- 新增 K-Means 聚类算法支持
- 新增层次聚类算法支持
- 添加聚类质量评估指标

Closes #123
```

### 测试要求

所有新功能必须包含相应的测试用例：

```bash
# 运行后端测试
pytest tests/ -v

# 运行前端测试
cd frontend
npm test
```

## Pull Request 流程

1. Fork 项目并创建功能分支
2. 在分支上进行开发，确保所有测试通过
3. 更新相关文档
4. 提交 Pull Request 到 `develop` 分支
5. 等待代码审查
6. 审查通过后，合并不者将合并您的 Pull Request

## 问题反馈

如果您发现任何问题或有改进建议，请通过以下方式反馈：

- 在 GitHub Issues 中创建新问题
- 提交 Pull Request 进行修复
- 联系项目维护者

## 许可证

通过贡献代码，您同意将您的贡献以 MIT 许可证开源。
