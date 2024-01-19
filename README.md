# Make your GIS life easy!
　ナカニシヤ出版から2022年に発行された[『実践利用にステップアップを目指す QGIS応用編―ベクタデータの利用からラスタデータの応用まで』](https://www.amazon.co.jp/dp/4779516374)の第V章(47ページから61ページまで)でfgddemImporterプラグインを用いた基盤地図情報のDEM(数値標高モデル)の読み込み方法が説明されていますが、その説明の通り、このプラグインはQGISのメジャーバージョン2で動作するものであって、QGIS 3では動作しません。プラグインの作者は既に開発を終了しています。

　QGIS 3ではMIERUNEさんが作成した[QuickDEM4JP](https://plugins.qgis.org/plugins/QuickDEM4JP/)プラグインを利用して基盤地図情報のDEMを変換して読み込むことができます。このプラグインはQGISの公式プラグインリポジトリに登録されており、プラグインメニューの「プラグインの管理とインストール...」からインストールできます。
次にチュートリアル記事があります。
- 国土地理院の標高データ（DEM）をQGIS上でサクッとGeoTIFFを作って可視化するプラグインを公開しました！（Terrain RGBもあるよ） #Python - Qiita https://qiita.com/nokonoko_1203/items/b99aa733cb215305f8aa

　fgddemImporterを用いて基盤地図情報のDEMを読み込むためにQGIS 2.XXをインストールするのは時間の無駄です。やめましょう。

# What is this?
**fgddemImporter** is a QGIS plugin to load DEM files of fundamental geospatial data provided by GSI into QGIS. JPGIS (GML) format files will be translated into GeoTIFF.

Japanese fundamental geospatial data are available at GSI site (user registration is required): http://www.gsi.go.jp/kiban/

# License
  GPLv3

Copyright (c) 2014 Minoru Akagi
