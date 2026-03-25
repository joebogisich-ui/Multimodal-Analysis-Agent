---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4b4abf8539199bb8c1fb4b35ee2fc8db
    PropagateID: 4b4abf8539199bb8c1fb4b35ee2fc8db
    ReservedCode1: 3046022100d05cbee7f62a67d87166493ede9a1c711e95dd1e3aa9b563c7c719b7fa2e4b6b022100fceae352825049bbaa1b933888b63166b3f89db6ed81fb55638c001bda297490
    ReservedCode2: 304402200dd4a7711c56c7b42b44445e127094f2c3a94bb13e5dd15fb1b353c8aecf5eaa022042cec6ce0cc3ae4c099a1a7ddf88edbb6334f234234ffe65eecc548126a5777e
---

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multimodal Analysis Agent - 多模态数据分析可视化Agent系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: #24292e;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 60px 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(124, 58, 237, 0.1) 0%, transparent 70%);
            animation: pulse 8s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        .logo {
            width: 120px;
            height: 120px;
            margin: 0 auto 30px;
            position: relative;
            z-index: 1;
        }

        .logo svg {
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 4px 20px rgba(124, 58, 237, 0.4));
        }

        .title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
            background: linear-gradient(135deg, #00d9ff 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        .lang-switch {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 2;
        }

        .lang-btn {
            padding: 8px 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: transparent;
            color: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
        }

        .lang-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.5);
        }

        .lang-btn.active {
            background: linear-gradient(135deg, #00d9ff 0%, #7c3aed 100%);
            border-color: transparent;
        }

        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 40px;
        }

        .section-title {
            font-size: 1.5rem;
            color: #1a1a2e;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid;
            border-image: linear-gradient(135deg, #00d9ff 0%, #7c3aed 100%) 1;
        }

        .zh, .en {
            display: none;
        }

        .zh.active, .en.active {
            display: block;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .feature-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(124, 58, 237, 0.15);
            border-color: #7c3aed;
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 12px;
        }

        .feature-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 8px;
        }

        .feature-desc {
            font-size: 0.95rem;
            color: #64748b;
            line-height: 1.6;
        }

        .architecture {
            background: #f8fafc;
            border-radius: 12px;
            padding: 30px;
            margin-top: 20px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            border: 1px solid #e2e8f0;
        }

        .code-block {
            background: #1a1a2e;
            color: #e2e8f0;
            border-radius: 8px;
            padding: 20px;
            margin: 15px 0;
            overflow-x: auto;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
        }

        .code-block code {
            color: #e2e8f0;
        }

        .code-comment {
            color: #6a737d;
        }

        .code-keyword {
            color: #f97583;
        }

        .code-string {
            color: #9ecbff;
        }

        .code-function {
            color: #b392f0;
        }

        .badges {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin: 20px 0;
        }

        .badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .badge-python {
            background: linear-gradient(135deg, #3776ab 0%, #ffd43b 100%);
            color: white;
        }

        .badge-react {
            background: linear-gradient(135deg, #61dafb 0%, #20232a 100%);
            color: white;
        }

        .badge-fastapi {
            background: linear-gradient(135deg, #009688 0%, #00bfa5 100%);
            color: white;
        }

        .badge-mit {
            background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
            color: white;
        }

        .quick-start {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 12px;
            padding: 24px;
            margin: 20px 0;
            border-left: 4px solid #f59e0b;
        }

        .quick-start-title {
            font-weight: 600;
            color: #92400e;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .api-item {
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #e2e8f0;
        }

        .api-method {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .api-method.get {
            background: #d1fae5;
            color: #065f46;
        }

        .api-method.post {
            background: #dbeafe;
            color: #1e40af;
        }

        .api-path {
            font-family: monospace;
            font-size: 0.9rem;
            color: #374151;
        }

        .footer {
            background: #1a1a2e;
            color: white;
            padding: 30px 40px;
            text-align: center;
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
        }

        .footer-link {
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .footer-link:hover {
            color: #00d9ff;
        }

        .copyright {
            font-size: 0.9rem;
            opacity: 0.7;
        }

        @media (max-width: 768px) {
            .header {
                padding: 40px 20px;
            }

            .title {
                font-size: 1.8rem;
            }

            .content {
                padding: 20px;
            }

            .feature-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="lang-switch">
                <button class="lang-btn active" data-lang="zh">中文</button>
                <button class="lang-btn" data-lang="en">English</button>
            </div>

            <div class="logo">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">
                    <defs>
                        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#16213e;stop-opacity:1" />
                        </linearGradient>
                        <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#00d9ff;stop-opacity:1" />
                            <stop offset="50%" style="stop-color:#7c3aed;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#f472b6;stop-opacity:1" />
                        </linearGradient>
                        <linearGradient id="textGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#00d9ff;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
                        </linearGradient>
                        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                            <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                            <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#7c3aed" flood-opacity="0.3"/>
                        </filter>
                    </defs>
                    <rect width="400" height="400" rx="20" ry="20" fill="url(#bgGradient)"/>
                    <circle cx="200" cy="180" r="130" fill="none" stroke="url(#iconGradient)" stroke-width="2" opacity="0.2"/>
                    <circle cx="200" cy="180" r="110" fill="none" stroke="url(#iconGradient)" stroke-width="1" opacity="0.15"/>
                    <g transform="translate(200, 180)" filter="url(#glow)">
                        <g transform="translate(-50, -50)">
                            <rect x="0" y="0" width="36" height="36" rx="8" fill="none" stroke="#00d9ff" stroke-width="2"/>
                            <line x1="8" y1="12" x2="28" y2="12" stroke="#00d9ff" stroke-width="2" stroke-linecap="round"/>
                            <line x1="8" y1="18" x2="24" y2="18" stroke="#00d9ff" stroke-width="2" stroke-linecap="round"/>
                            <line x1="8" y1="24" x2="20" y2="24" stroke="#00d9ff" stroke-width="2" stroke-linecap="round"/>
                        </g>
                        <g transform="translate(14, -50)">
                            <rect x="0" y="0" width="36" height="36" rx="8" fill="none" stroke="#f472b6" stroke-width="2"/>
                            <circle cx="18" cy="16" r="6" fill="none" stroke="#f472b6" stroke-width="2"/>
                            <path d="M 8 28 L 14 20 L 20 24 L 28 14 L 28 28 Z" fill="none" stroke="#f472b6" stroke-width="2" stroke-linejoin="round"/>
                        </g>
                        <g transform="translate(-50, 14)">
                            <rect x="0" y="0" width="36" height="36" rx="8" fill="none" stroke="#fbbf24" stroke-width="2"/>
                            <path d="M 12 26 L 12 14 L 16 14 L 16 26 M 20 26 L 20 10 L 24 10 L 24 26" fill="none" stroke="#fbbf24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </g>
                        <g transform="translate(14, 14)">
                            <rect x="0" y="0" width="36" height="36" rx="8" fill="none" stroke="#4ade80" stroke-width="2"/>
                            <polygon points="14,10 26,18 14,26" fill="none" stroke="#4ade80" stroke-width="2" stroke-linejoin="round"/>
                        </g>
                    </g>
                    <g transform="translate(200, 180)" filter="url(#shadow)">
                        <circle cx="0" cy="0" r="28" fill="url(#iconGradient)" opacity="0.9"/>
                        <circle cx="-4" cy="-4" r="12" fill="none" stroke="white" stroke-width="2.5"/>
                        <line x1="5" y1="5" x2="12" y2="12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                        <circle cx="-4" cy="-4" r="3" fill="white" opacity="0.8"/>
                    </g>
                    <g stroke="url(#iconGradient)" stroke-width="1.5" fill="none" opacity="0.6">
                        <line x1="160" y1="140" x2="180" y2="160"/>
                        <line x1="240" y1="140" x2="220" y2="160"/>
                        <line x1="160" y1="220" x2="180" y2="200"/>
                        <line x1="240" y1="220" x2="220" y2="200"/>
                    </g>
                    <text x="200" y="320" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="18" font-weight="600" fill="url(#textGradient)">Multimodal Analysis Agent</text>
                    <text x="200" y="345" text-anchor="middle" font-family="'Microsoft YaHei', 'PingFang SC', sans-serif" font-size="13" fill="#94a3b8">多模态数据分析可视化系统</text>
                    <text x="200" y="375" text-anchor="middle" font-family="'Segoe UI', Arial, sans-serif" font-size="10" fill="#64748b">v1.0.0</text>
                </svg>
            </div>

            <h1 class="title">Multimodal Analysis Agent</h1>
            <p class="subtitle">基于多模态内容理解的全自动化数据分析可视化 Agent 系统</p>
        </header>

        <main class="content">
            <!-- 徽章 -->
            <div class="badges">
                <span class="badge badge-python">Python 3.10+</span>
                <span class="badge badge-react">React + TypeScript</span>
                <span class="badge badge-fastapi">FastAPI</span>
                <span class="badge badge-mit">MIT License</span>
            </div>

            <!-- 项目概述 -->
            <section class="section">
                <h2 class="section-title" data-i18n="overview">项目概述</h2>

                <div class="zh active">
                    <p>本项目是一个高度智能化的数据分析可视化 Agent 系统，专注于多模态内容理解与自动化数据分析。该系统能够接收文本、图像、音频、视频等多种数据格式，通过先进的人工智能技术自动识别数据类型、提取关键信息、执行深度分析，并生成直观的可视化结果。</p>
                </div>

                <div class="en">
                    <p>This project is a highly intelligent data analysis and visualization Agent system, focusing on multimodal content understanding and automated data analysis. The system can receive various data formats including text, images, audio, and video, automatically identify data types, extract key information, perform deep analysis, and generate intuitive visualization results through advanced AI technology.</p>
                </div>
            </section>

            <!-- 核心特性 -->
            <section class="section">
                <h2 class="section-title" data-i18n="features">核心特性</h2>

                <div class="zh active">
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🔄</div>
                            <div class="feature-title">多模态数据融合处理</div>
                            <div class="feature-desc">系统能够同时处理和理解多种数据格式，实现跨模态的信息关联与融合分析</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🎯</div>
                            <div class="feature-title">智能任务编排</div>
                            <div class="feature-desc">Agent 引擎能够自动分解复杂分析任务，协调多个处理模块高效协同工作</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📊</div>
                            <div class="feature-title">自适应可视化生成</div>
                            <div class="feature-desc">系统根据数据特征和分析目标自动选择最优的可视化方案</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">💬</div>
                            <div class="feature-title">自然语言交互支持</div>
                            <div class="feature-desc">用户可以通过自然语言描述分析需求，系统自动解析意图并执行</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🔧</div>
                            <div class="feature-title">可扩展架构设计</div>
                            <div class="feature-desc">模块化的系统架构支持灵活扩展，便于集成新的数据处理能力</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🔁</div>
                            <div class="feature-title">反馈闭环机制</div>
                            <div class="feature-desc">系统具备结果验证、错误检测和自我修正能力，持续优化分析质量</div>
                        </div>
                    </div>
                </div>

                <div class="en">
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🔄</div>
                            <div class="feature-title">Multimodal Data Fusion</div>
                            <div class="feature-desc">Process and understand multiple data formats simultaneously, enabling cross-modal information correlation and fusion analysis</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🎯</div>
                            <div class="feature-title">Intelligent Task Orchestration</div>
                            <div class="feature-desc">Agent engine automatically decomposes complex analysis tasks and coordinates multiple processing modules</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📊</div>
                            <div class="feature-title">Adaptive Visualization</div>
                            <div class="feature-desc">Automatically select optimal visualization schemes based on data characteristics and analysis goals</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">💬</div>
                            <div class="feature-title">Natural Language Interaction</div>
                            <div class="feature-desc">Users can describe analysis requirements in natural language, and the system automatically interprets and executes</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🔧</div>
                            <div class="feature-title">Extensible Architecture</div>
                            <div class="feature-desc">Modular architecture supports flexible expansion and easy integration of new data processing capabilities</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🔁</div>
                            <div class="feature-title">Feedback Loop Mechanism</div>
                            <div class="feature-desc">System has result validation, error detection, and self-correction capabilities for continuous quality optimization</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 快速开始 -->
            <section class="section">
                <h2 class="section-title" data-i18n="quickstart">快速开始</h2>

                <div class="zh active">
                    <div class="quick-start">
                        <div class="quick-start-title">⚡ 快速启动</div>
                        <div class="code-block">
                            <code>
<span class="code-comment"># 克隆项目</span>
<span class="code-keyword">git</span> clone https://github.com/yourusername/multimodal-analysis-agent.git
<span class="code-keyword">cd</span> multimodal-analysis-agent

<span class="code-comment"># 安装后端依赖</span>
<span class="code-keyword">python</span> -m venv venv
<span class="code-function">source</span> venv/bin/activate  <span class="code-comment"># Linux/macOS</span>
<span class="code-keyword">pip</span> install -r requirements.txt

<span class="code-comment"># 安装前端依赖</span>
<span class="code-keyword">cd</span> frontend
<span class="code-function">npm</span> install

<span class="code-comment"># 启动服务</span>
<span class="code-keyword">cd</span> backend && <span class="code-function">uvicorn</span> main:app --reload --port 8000
                            </code>
                        </div>
                    </div>

                    <h3 style="margin: 20px 0 15px; color: #1a1a2e;">环境配置</h3>
                    <p>在项目根目录创建 <code>.env</code> 文件：</p>
                    <div class="code-block">
                        <code>
<span class="code-string">OPENAI_API_KEY</span>=your_api_key_here
<span class="code-string">SECRET_KEY</span>=your_secret_key_here
<span class="code-string">REDIS_HOST</span>=localhost
<span class="code-string">REDIS_PORT</span>=6379
                        </code>
                    </div>
                </div>

                <div class="en">
                    <div class="quick-start">
                        <div class="quick-start-title">⚡ Quick Start</div>
                        <div class="code-block">
                            <code>
<span class="code-comment"># Clone the project</span>
<span class="code-keyword">git</span> clone https://github.com/yourusername/multimodal-analysis-agent.git
<span class="code-keyword">cd</span> multimodal-analysis-agent

<span class="code-comment"># Install backend dependencies</span>
<span class="code-keyword">python</span> -m venv venv
<span class="code-function">source</span> venv/bin/activate  <span class="code-comment"># Linux/macOS</span>
<span class="code-keyword">pip</span> install -r requirements.txt

<span class="code-comment"># Install frontend dependencies</span>
<span class="code-keyword">cd</span> frontend
<span class="code-function">npm</span> install

<span class="code-comment"># Start services</span>
<span class="code-keyword">cd</span> backend && <span class="code-function">uvicorn</span> main:app --reload --port 8000
                            </code>
                        </div>
                    </div>

                    <h3 style="margin: 20px 0 15px; color: #1a1a2e;">Environment Configuration</h3>
                    <p>Create a <code>.env</code> file in the project root:</p>
                    <div class="code-block">
                        <code>
<span class="code-string">OPENAI_API_KEY</span>=your_api_key_here
<span class="code-string">SECRET_KEY</span>=your_secret_key_here
<span class="code-string">REDIS_HOST</span>=localhost
<span class="code-string">REDIS_PORT</span>=6379
                        </code>
                    </div>
                </div>
            </section>

            <!-- 系统架构 -->
            <section class="section">
                <h2 class="section-title" data-i18n="architecture">系统架构</h2>

                <div class="zh active">
                    <div class="architecture">
multimodal-analysis-agent/
├── backend/                    # 后端服务目录
│   ├── agents/               # Agent 核心模块
│   │   ├── orchestrator.py   # 任务编排器
│   │   ├── analyzer.py       # 数据分析器
│   │   ├── visualizer.py     # 可视化生成器
│   │   ├── planner.py        # 任务规划器
│   │   └── feedback_loop.py  # 反馈闭环模块 ⭐
│   ├── processors/           # 数据处理器
│   │   ├── text_processor.py # 文本处理
│   │   ├── image_processor.py# 图像处理
│   │   ├── audio_processor.py# 音频处理
│   │   └── video_processor.py# 视频处理
│   ├── api/routes.py        # API 接口
│   └── core/                # 核心功能
├── frontend/                # 前端应用
├── docs/                    # 项目文档
└── config/                  # 配置文件
                    </div>
                </div>

                <div class="en">
                    <div class="architecture">
multimodal-analysis-agent/
├── backend/                    # Backend Service
│   ├── agents/               # Agent Core Modules
│   │   ├── orchestrator.py   # Task Orchestrator
│   │   ├── analyzer.py       # Data Analyzer
│   │   ├── visualizer.py     # Chart Visualizer
│   │   ├── planner.py        # Task Planner
│   │   └── feedback_loop.py  # Feedback Loop ⭐
│   ├── processors/           # Data Processors
│   │   ├── text_processor.py # Text Processing
│   │   ├── image_processor.py# Image Processing
│   │   ├── audio_processor.py# Audio Processing
│   │   └── video_processor.py# Video Processing
│   ├── api/routes.py        # API Routes
│   └── core/                # Core Functions
├── frontend/                # Frontend Application
├── docs/                    # Documentation
└── config/                  # Configuration
                    </div>
                </div>
            </section>

            <!-- 核心模块 -->
            <section class="section">
                <h2 class="section-title" data-i18n="modules">核心模块</h2>

                <div class="zh active">
                    <h3 style="color: #7c3aed; margin: 15px 0;">🤖 Agent 协调器</h3>
                    <p>系统的核心控制单元，负责接收用户请求、解析任务意图、分解复杂任务、协调各处理模块以及整合最终结果。</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">📝 多模态处理器</h3>
                    <p>支持文本、图像、音频、视频四种数据格式的预处理和特征提取。</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">📈 数据分析引擎</h3>
                    <p>提供统计分析、趋势分析、聚类分析、相关性分析、回归分析等多种分析方法。</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">📊 可视化生成器</h3>
                    <p>支持折线图、柱状图、散点图、热力图、雷达图等 10+ 图表类型。</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">🔄 反馈闭环模块</h3>
                    <p>结果验证器 + 错误检测器 + 自我修正器，实现自我检查和持续改进。</p>
                </div>

                <div class="en">
                    <h3 style="color: #7c3aed; margin: 15px 0;">🤖 Agent Orchestrator</h3>
                    <p>The core control unit responsible for receiving user requests, parsing task intent, decomposing complex tasks, coordinating processing modules, and integrating final results.</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">📝 Multimodal Processors</h3>
                    <p>Support preprocessing and feature extraction for text, image, audio, and video data formats.</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">📈 Data Analysis Engine</h3>
                    <p>Provide statistical analysis, trend analysis, clustering, correlation analysis, regression analysis, and more.</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">📊 Visualization Generator</h3>
                    <p>Support 10+ chart types including line, bar, scatter, heatmap, radar, and more.</p>

                    <h3 style="color: #7c3aed; margin: 15px 0;">🔄 Feedback Loop Module</h3>
                    <p>Result Validator + Error Detector + Self-Corrector for self-inspection and continuous improvement.</p>
                </div>
            </section>

            <!-- API 接口 -->
            <section class="section">
                <h2 class="section-title" data-i18n="api">API 接口</h2>

                <div class="zh active">
                    <div class="api-grid">
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/tasks</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">创建分析任务</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method get">GET</span>
                            <div class="api-path">/api/v1/tasks/{id}</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">查询任务状态</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/analyze</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">执行数据分析</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/visualize</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">生成可视化</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/feedback/validate</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">验证结果</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/feedback/correct</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">自我修正</p>
                        </div>
                    </div>
                </div>

                <div class="en">
                    <div class="api-grid">
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/tasks</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Create Analysis Task</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method get">GET</span>
                            <div class="api-path">/api/v1/tasks/{id}</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Query Task Status</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/analyze</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Execute Data Analysis</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/visualize</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Generate Visualization</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/feedback/validate</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Validate Results</p>
                        </div>
                        <div class="api-item">
                            <span class="api-method post">POST</span>
                            <div class="api-path">/api/v1/feedback/correct</div>
                            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">Self-Correction</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 技术栈 -->
            <section class="section">
                <h2 class="section-title" data-i18n="techstack">技术栈</h2>

                <div class="zh active">
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🐍</div>
                            <div class="feature-title">Python</div>
                            <div class="feature-desc">FastAPI, LangChain, Pandas, NumPy, Scikit-learn</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">⚛️</div>
                            <div class="feature-title">React</div>
                            <div class="feature-desc">React 18, TypeScript, TailwindCSS, Plotly</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🧠</div>
                            <div class="feature-title">AI/ML</div>
                            <div class="feature-desc">OpenAI API, LangChain, Transformers, PyTorch</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📦</div>
                            <div class="feature-title">Data</div>
                            <div class="feature-desc">Pandas, NumPy, SciPy, Librosa, OpenCV</div>
                        </div>
                    </div>
                </div>

                <div class="en">
                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🐍</div>
                            <div class="feature-title">Python</div>
                            <div class="feature-desc">FastAPI, LangChain, Pandas, NumPy, Scikit-learn</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">⚛️</div>
                            <div class="feature-title">React</div>
                            <div class="feature-desc">React 18, TypeScript, TailwindCSS, Plotly</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🧠</div>
                            <div class="feature-title">AI/ML</div>
                            <div class="feature-desc">OpenAI API, LangChain, Transformers, PyTorch</div>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📦</div>
                            <div class="feature-title">Data</div>
                            <div class="feature-desc">Pandas, NumPy, SciPy, Librosa, OpenCV</div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 贡献 -->
            <section class="section">
                <h2 class="section-title" data-i18n="contributing">贡献指南</h2>

                <div class="zh active">
                    <p>欢迎贡献代码！请参阅 <a href="CONTRIBUTING.md" style="color: #7c3aed;">CONTRIBUTING.md</a> 了解如何参与项目开发。</p>
                    <p style="margin-top: 15px;">项目采用 MIT 许可证开源。</p>
                </div>

                <div class="en">
                    <p>Contributions are welcome! Please see <a href="CONTRIBUTING.md" style="color: #7c3aed;">CONTRIBUTING.md</a> for how to participate in project development.</p>
                    <p style="margin-top: 15px;">This project is open source under the MIT License.</p>
                </div>
            </section>
        </main>

        <footer class="footer">
            <div class="footer-links">
                <a href="https://github.com/yourusername/multimodal-analysis-agent" class="footer-link">GitHub</a>
                <a href="https://github.com/yourusername/multimodal-analysis-agent/issues" class="footer-link">Issues</a>
                <a href="https://github.com/yourusername/multimodal-analysis-agent/discussions" class="footer-link">Discussions</a>
            </div>
            <p class="copyright">© 2024 Multimodal Analysis Agent. MIT License.</p>
        </footer>
    </div>

    <script>
        // 语言切换功能
        const langBtns = document.querySelectorAll('.lang-btn');
        const zhContents = document.querySelectorAll('.zh');
        const enContents = document.querySelectorAll('.en');

        langBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const lang = btn.dataset.lang;

                // 更新按钮状态
                langBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // 切换内容显示
                if (lang === 'zh') {
                    zhContents.forEach(el => el.classList.add('active'));
                    enContents.forEach(el => el.classList.remove('active'));
                    document.documentElement.lang = 'zh-CN';
                } else {
                    enContents.forEach(el => el.classList.add('active'));
                    zhContents.forEach(el => el.classList.remove('active'));
                    document.documentElement.lang = 'en';
                }
            });
        });

        // 键盘快捷键支持
        document.addEventListener('keydown', (e) => {
            if (e.key === 'l' && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                const currentLang = document.querySelector('.lang-btn.active').dataset.lang;
                const nextLang = currentLang === 'zh' ? 'en' : 'zh';
                document.querySelector(`[data-lang="${nextLang}"]`).click();
            }
        });
    </script>
</body>
</html>
