from setuptools import setup, find_packages

setup(
    name="PreReduction",
    version="0.1",
    packages=find_packages(),
    python_requires=">=2.7, <3",
    include_package_data=True,
    install_requires=[
    "numpy",
    "pandas",
    "astropy"
    # "optparse",
    "pyyaml",
    "reproject",
    "pyraf",
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
