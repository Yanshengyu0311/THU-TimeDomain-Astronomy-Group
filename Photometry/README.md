# 基础软件
首先介绍几个常见的光学测光基础软件
## iraf

## Sextractor
Sextractor是一个批量测光软件。

## DS9


## WCS软件
### Astromotry.net
[Astromotry.net](https://astrometry.net/)是一个强大的
### Scamp


## 图像相减软件
### hotpants
### zogy
[ZOGY](http://ui.adsabs.harvard.edu/abs/2021ascl.soft05010V/abstract)

## 其他软件
### Swarp
### missfit


# 软件进阶
# IRAF测光
郑伟康老师的曾经写过IRAF的pipeline'zphot'。可能会涉及到郑伟康老师的版权问题，所以请在清华云盘内部链接下载'zphot'及其代码：


### Autophot

### zrutyphot

莫军师兄硕士论文
黄芳师姐曾经对80厘米望远镜的数据介绍，[论文地址](https://iopscience.iop.org/article/10.1088/1674-4527/12/11/012/meta)。


# S-correction
## SVO+pyphot
[SVO](http://svo2.cab.inta-csic.es/) Filter Profile Service是一个包含了各种望远镜及其仪器滤光片的信息网站,我们可以通过这个数据，下载滤光片信息。另外，SVO可以通过python中astroquery直接获取信息，比直接从网站获取更方便快捷。[pyphot](https://mfouesneau.github.io/pyphot/)是一个强大的卷积滤光片透过率和光谱软件，两个工具配合好，可以玩转多波段测光数据。

## S-correction实例