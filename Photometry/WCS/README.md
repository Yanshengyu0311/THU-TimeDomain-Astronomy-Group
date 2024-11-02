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
