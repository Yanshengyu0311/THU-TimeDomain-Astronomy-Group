# 简介
TNT是我们组的最常用的测光设备，由于现在EP会有很多后随的源需要观测，EP的X-ray源的光学对应体一般也比较暗，所以有时候可能需要叠加图像才可以更好的找到信号。这个项目就是教大家快速的获得TNT图像，并且图像进行叠加，并寻找光学对映体。
# 获取fit文件
由于TNT图像，是每晚观测完之后，观测助手上传至山上一个服务器，再由服务器到我们的服务器，一般时间较长。所以我们就需要让助手，在观测之后，马上传给我们数据。建议建立一个清华云盘链接。大家就可以直接让助手传到清华云盘上，然后我们从清华云盘下载。
# 预处理
预处理详见[PreReduction](../../Photometry/PreReduction/)
# WCS
对于WCS，组里常见的用的是scamp，包括TNT80cm 服务器上和zrutyphot上，这个东西比较轻量化。
我常用的就是[Astrometry.net](https://astrometry.net/)中solve-field，这个工具是开源的，可以自己下载。
一般使用技巧，加上中心坐标和半径，会加速计算。
```bash
solve-field -O --no-plot --temp-axy --match=none --rdls=none --solved=none --index-xyls=none --corr=none  -T --radius=10 --ra=67.990 --dec=43.030 *fits
```
GRB241018A_r_0*需要做wcs的文件名。运行完后，可用的文件一般是去掉fits文件后缀的文件，在加上一个.new,比如GRB241018A_r_001.new。   
--ra和--dec是中心坐标，--radius是搜索半径。中心坐标的格式比价灵活。具体看[教程](https://astrometry.net/)。-O（大写O）是覆盖原来的文件，防止一些不必要的报错。
--no-plot到--corr=none的参数，是删除一些程序运行过程中产生的临时文件。-T是关闭场曲/畸变修正，视场不是很大的情况下，没有必要做高阶的修正，最低阶即可。
其他用法详见[WCS](../../Photometry/WCS/README.md)。
# 合并图像。
由于TNT80cm的图像指向并不是很好，所以直接相加会导致图像的偏移，所以需要对其wcs后，才能对图像合并，这个脚本中即可对图像进行wcs对齐合并。
这时候需要切换一下环境，使用python 3，包含[**reproject**](https://reproject.readthedocs.io/en/stable/index.html)包的环境。然后
```bash
python coadd_image.py -T TNT80cm -i XL80 GRB241018A_r_00*new
```
其中[coadd_image.py](../../Photometry/PreReduction/PreReduction/coadd_image.py)
-T 是望远镜名称 -i 是仪器名称。GRB241018A_r_00*new是所有合并所需要的文件。运行完毕之后，会在CombinedImages/文件下有一个合并后的图片。
**注意事项
合并之前查看一下合并的图像，是否有质量特别差的图像，特别差的需要删除。