"""
基于多模态内容理解的全自动化数据分析可视化 Agent 系统

该系统是一个高度智能化的数据分析平台，能够处理文本、图像、音频、视频等多种数据格式，
通过 AI Agent 技术实现自动化的数据分析和可视化。
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="multimodal-analysis-agent",
    version="1.0.0",
    author="Multimodal Analysis Team",
    author_email="team@example.com",
    description="基于多模态内容理解的全自动化数据分析可视化 Agent 系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multimodal-analysis-agent",
    packages=find_packages(exclude=["tests", "tests.*", "frontend", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "black>=24.1.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "multimodal-agent=backend.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
