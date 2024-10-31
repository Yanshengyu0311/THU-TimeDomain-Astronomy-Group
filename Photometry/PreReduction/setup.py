from setuptools import setup, find_packages

setup(
    name="PreReduction",
    version="0.1",
    packages=find_packages(),
    python_requires=">=2.7, <3",
    install_requires=[
    # "numpy>=1.20.0",       # 最低版本1.20.0，允许更高版本
    # "pandas==1.3.3",       # 固定版本为1.3.3
    # "scipy>=1.5,<2.0",     # 版本介于1.5和2.0之间
    "numpy",
    "pandas",
    "astropy",
    "optparse",
    "yaml",
    "reproject",
    "pyraf"
    ],  # 如果有依赖库，可以在这里添加

    # 定义命令行脚本入口
    
    entry_points={
        "console_scripts": [
            # "PreReduction=PreReduction.main:main",
            # "PreReduction=PreReduction.main",
            "PreReduction=PreReduction.main:cli",
        ],
    },
    # 项目信息
    author="Shengyu Yan",
    author_email="yanshengyu0311@qq.com",
    description="A tool for PreReduction with parameters -a and -b",
)
