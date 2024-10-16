# Wellcome to the THU TimeDomain Astronomy Group
Well come to the Tsinghua University TimeDomain Astronomy Group, Here we will introduce some about the Astrnomical Data Reduction in Optical!
欢迎各位同学补充和修正内容！让我们组的观测资源和代码资源整理的更加有条理！

# 数据处理和科学软件指南

## 光谱数据处理
具体学习教程和文件详见[./Spectroscopy/](./Spectroscopy/)
## 测光数据处理
具体学习教程和文件详见[./Photometry/](./Photometry/)
## 科学数据分析
整理了一些我们课题组常见的科学分析软件，学习教程和文件等详见[./Softwares/](./Softwares/)

# 软件及操作系统

## 操作系统以及网络配置
作为初学者，如果你使用的是Windows操作系统，强烈建议建议使用Windows+[WSL](https://learn.microsoft.com/en-us/windows/wsl/install)组合，替代若干年前的，常见的Windows+Ubuntu双系统组合。Windows+WSL组合可以几乎完美的同时使用Windows和Linux系统的各个软件。而且免去了开双系统的麻烦，两个系统的文件也可以相互交互访问并修改。


### Windows进阶
我目前已经逐渐放弃了Windows+WSL组合。因为随着计算量变大，本地计算已经无法满足科研需求。所以我开始使用Visual Studio Code SSH远程连接服务器的方式进行日常coding。并且通过蒲公英[蒲公英](https://pgy.oray.com/)建立私域VPN，避免了本地电脑计算机运较慢等问题。

## IRAF
[IRAF](https://iraf.net/)是我们天文学光学领域，数据处理和科学分析，最标准的，最科学，最全面的科学软件，是天文光学软件的旗舰和标杆。软件里面不仅仅包含了各种数据处理和科学分析的的功能，还拥有很全面使用指南。

## DS9
[DS9](https://sites.google.com/cfa.harvard.edu/saoimageds9)作为最强大的天文图像查看软件，可以和天文学软件很多兼容。里面有很多分析工具，可以对图像进行初的数值步分析。

## git
学会强大的代码管理，强烈建议养成良好的习惯。把代码保存在远程服务器作为备份，防止丢失。

## Python
除了常见的numpy，matplotlib，scipy等python软件包，常见的astropy，astroquery，emcee也是必学的软件包。

### emcee
[emcee](https://emcee.readthedocs.io/en/stable/)是mcmc最常见的采样估计参数的方法之一。我集成了emcee的，写成了一个类似scipy curve_fit的包，让拟合更方便。详见[]()

### SVO+pyphot
[SVO](http://svo2.cab.inta-csic.es/) Filter Profile Service是一个包含了各种望远镜及其仪器滤光片的信息网站,我们可以通过这个数据，下载滤光片信息。另外，SVO可以通过python中astroquery直接获取信息，比直接从网站获取更方便快捷。[pyphot](https://mfouesneau.github.io/pyphot/)是一个强大的卷积滤光片透过率和光谱软件，两个工具配合好，可以玩转多波段测光数据。