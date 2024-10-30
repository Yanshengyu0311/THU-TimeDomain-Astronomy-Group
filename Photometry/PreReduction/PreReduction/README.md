* 简介
这是一个图像预处理的脚本。通过调用pyraf，实现快速的图像预处理。不同望远镜的信息都集成在telescope_Pre.yaml里面。可以通过telescope_Pre.yaml中头文件的信息，对文件进行识别，分类。
* python基本的依赖
- **numpy** 
- **pandas**
- **astropy**
- **optparse**
- **yaml**
- **reproject**
- **pyraf**

* 安装此软件
下载包后，先初始化有**pyraf/iraf**的环境，在终端中输入：
```bash
source activate iraf27
cd PreReduceFITS/
pip install .
```
* 使用方法
首先初始化环境：
```bash
source activate iraf27
```
查看帮助信息：
```bash
PreReduction -h # 查看帮助信息
```
预处理文件(示例):
```bash
PreReduction -b "bias_0*" -T TNT80cm -i XL80 -f "flat_*" SN2024vpc_r_001.fit
```
其中，-b 是bias，-T 是望远镜名称，-i 是仪器名称，-f 是平常名称 SN2024vpc_*_是需要预处理的科学图像的文件名称，可以使用通配符。    
**注意-b和-f后面的参数，必须用引号""括号括起来**

* WCS
对于WCS，组里常见的用的是scamp，包括TNT80cm 服务器上和zrutyphot上，这个东西比较轻量化。
我常用的就是(Astrometry.net)[https://astrometry.net/]中solve-field，这个工具是开源的，可以自己下载。
一般使用技巧，加上中心坐标和半径，会加速计算。
```bash
solve-field GRB241018A_r_0* --ra=67.990 --dec=43.030 --radius=10 -O
```
GRB241018A_r_0*需要做wcs的文件名。运行完后，可用的文件一般是去掉fits文件后缀的文件，在加上一个.new,比如GRB241018A_r_001.new。   
--ra和--dec是中心坐标，--radius是搜索半径。中心坐标的格式比价灵活。具体看(教程)[https://astrometry.net/]。-O（大写O）是覆盖原来的文件，防止一些不必要的报错。

* 合并图像。
由于TNT80cm的图像指向并不是很好，所以直接相加会导致图像的偏移，所以需要对其wcs后，才能对图像合并，这个脚本中即可对图像进行wcs对齐合并。
这时候需要切换一下环境，使用python 3，包含(**reproject**)[https://reproject.readthedocs.io/en/stable/index.html]包的环境。然后
```bash
python coadd_image.py -T TNT80cm -i XL80 GRB241018A_r_00*new
```
-T 是望远镜名称 -i 是仪器名称。GRB241018A_r_00*new是所有合并所需要的文件。运行完毕之后，会在CombinedImages/文件下有一个合并后的图片。
**注意事项
合并之前查看一下合并的图像，是否有质量特别差的图像，特别差的需要删除。