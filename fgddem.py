#!/usr/bin/env python
# fgddem.py
# Copyright (c) 2012, Akagi Minoru.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

script_version = '0.1'

import sys,os
import glob
import zipfile
import shutil
import codecs
from xml.dom import minidom
import numpy

try:
    from osgeo import gdal
except ImportError:
    import gdal

try:
    progress = gdal.TermProgress_nocb
except:
    progress = gdal.TermProgress

verbose = 0
quiet = 0
debug_mode = 0

# Convert Kiban JPGIS(GML) XML mesh file to GeoTIFF file.
def convert_jpgis_gml(src_file,dest_file,driver,create_options = [],replace_nodata_by_zero = 0):

    if replace_nodata_by_zero:
        nodata_value = 0.
    else:
        nodata_value = -9999.

    f = codecs.open(src_file,'r','shift_jis')
    doc = f.readlines()
    f.close()

    numLines = len(doc)
    l1 = None
    l2 = None

    for i in range(numLines):
        if doc[i].find("<gml:tupleList>") != -1:
            l1 = i + 1      # top of inner tupleList
            break

    for i in range(numLines-1,-1,-1):
        if doc[i].find("</gml:tupleList>") != -1:
            l2 = i - 1      # bottom of inner tupleList
            break

    if l1 is None or l2 is None:
        return 0

    numLines_tupleList = l2 - l1 + 1
    doc_hf = ''.join(doc[:l1] + doc[l2+1:])

    if debug_mode:
        print 'l1: %d l2: %d' % (l1,l2)
        print numLines_tupleList
        print doc_hf

    # Minidom doesn't support Shift_JIS encoding (2012-03-08)
    xml = minidom.parseString(doc_hf.encode('UTF-8').replace('Shift_JIS','UTF-8'))

    lowerCorner = xml.getElementsByTagName('gml:lowerCorner')[0].childNodes[0].data.split(' ')
    upperCorner = xml.getElementsByTagName('gml:upperCorner')[0].childNodes[0].data.split(' ')
    lry = float2(lowerCorner[0])
    ulx = float2(lowerCorner[1])
    uly = float2(upperCorner[0])
    lrx = float2(upperCorner[1])

    high = xml.getElementsByTagName('gml:high')[0].childNodes[0].data.split(' ')
    xsize = int(high[0]) + 1
    ysize = int(high[1]) + 1

    startPoint = xml.getElementsByTagName('gml:startPoint')[0].childNodes[0].data.split(' ')
    startX = int(startPoint[0])
    startY = int(startPoint[1])

    psize_x = (lrx - ulx) / xsize
    psize_y = (lry - uly) / ysize

    geotransform = [ulx, psize_x, 0, uly, 0, psize_y]

    band_type = gdal.GDT_Float32
    bands = 1

    dst_ds = driver.Create(dest_file, xsize, ysize, bands, band_type, create_options)
    if dst_ds is None:
        print 'Creation failed.'
        sys.exit(1)

    dst_ds.SetGeoTransform(geotransform)

    # The following Well Known Text has been cited from http://spatialreference.org/ref/epsg/4612/ogcwkt/
    dst_ds.SetProjection('GEOGCS["JGD2000",DATUM["Japanese_Geodetic_Datum_2000",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6612"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4612"]]')

    rband = dst_ds.GetRasterBand(1)
    narray = numpy.empty((ysize, xsize), numpy.float32)
    narray.fill(nodata_value)
    i = 0; sx = startX
    for y in range(startY, ysize):
        for x in range(sx, xsize):
            if i < numLines_tupleList:
                vals = doc[i+l1].split(',')
                if len(vals) == 2 and vals[1].find('-99') == -1:
                    narray[y][x] = float(vals[1])
                i += 1
            else:
                break
        if i == numLines_tupleList: break
        sx = 0
    rband.WriteArray(narray,0,0)

    if replace_nodata_by_zero == 0:
        rband.SetNoDataValue(nodata_value)

    dst_ds = None

    if verbose:
        print 'file: %s' % src_file
        print 'name: %s' % xml.getElementsByTagName('gml:name')[0].childNodes[0].data
        print 'fid : %s' % xml.getElementsByTagName('fid')[0].childNodes[0].data
        print 'type: %s' % xml.getElementsByTagName('type')[0].childNodes[0].data
        print 'mesh: %s' % xml.getElementsByTagName('mesh')[0].childNodes[0].data
        print 'bounds : %f, %f - %f, %f' % (lry,ulx,uly,lrx)
        print 'cell size : %f, %f' % (psize_x,psize_y)
        print 'size : %d, %d' % (xsize,ysize)
        print 'start point : %d, %d' % (startX,startY)
        print ''

def unzip(src_file, dest=None):
    if os.path.isfile(src_file):
        if dest is None:
            dest = os.path.splitext(src_file)[0]
        zf = zipfile.ZipFile(src_file, mode='r')
        zf.extractall(dest)
        zf.close()

        if verbose:
            print 'unzipped : %s' % dest

def Usage():
    print '=== Usage ==='
    print 'python fgddem.py [-replace_nodata_by_zero][-out_dir output_directory][-q] [-v] src_files*'
    print ''
    print 'src_files: The source file name(s). JPGIS(GML) DEM zip/xml files.'
    print 'You can use -version option to display the version of this script.'

    return 0

def main(argv=None):
    global verbose, quiet, debug_mode
    format = 'GTiff'
    filenames = []
    out_dir = ''
    replace_nodata_by_zero = 0

    gdal_merge_options = ''
    gdalwarp_options = ''
    gdal_merge_ext = ''
    if os.name != 'nt':     # nt: windows
        gdal_merge_ext = '.py'

    gdal_version = int(gdal.VersionInfo())
    gdal.AllRegister()

    if argv is None:
        argv = sys.argv
    argv = gdal.GeneralCmdLineProcessor(argv)
    if argv is None:
        return 0

    # Parse command line arguments.
    i = 1
    while i < len(argv):
        arg = argv[i]

        if arg == '-replace_nodata_by_zero':
            replace_nodata_by_zero = 1

        elif arg == '-out_dir':
            i += 1
            out_dir = argv[i]

        elif arg == '-v':
            verbose = 1

        elif arg == '-q':
            quiet = 1

        elif arg == '-debug':
            debug_mode = 1

        elif arg == '-help' or arg == '--help':
            return Usage()

        elif arg == '-version':
            print 'fgddem.py Version %s' % script_version
            return 0

        elif arg[:1] == '-':
            print 'Unrecognised command option: %s' % arg
            return Usage()

        else:
            # Expand any possible wildcards
            f = glob.glob(arg)
            if len(f) == 0:
                print 'File not found: "%s"' % arg

            filenames += f

        i = i + 1

    if verbose or debug_mode:
        sys.stdout = codecs.getwriter('shift_jis')(sys.stdout)      # Error occurs in Python >= 3.0

    if debug_mode:
        print 'args: %s' % ' '.join(argv)
        print 'files: %s' % ','.join(filenames)

    if len(filenames) == 0:
        print 'No input files selected.'
        return Usage()

    if quiet:
        gdal_merge_options += ' -q'

    if verbose == 0:
        gdalwarp_options += ' -q'

    if out_dir != '' and os.path.exists(out_dir) == False:
        os.mkdir(out_dir)
        if verbose:
            print '"%s" directory has been created.' % out_dir

    if replace_nodata_by_zero == 0:
        gdal_merge_options += ' -a_nodata -9999'
        gdalwarp_options += ' -dstnodata -9999'

    driver = gdal.GetDriverByName(format)
    if driver is None:
        print 'Format driver %s not found.' % format
        return 0

    fi_processed = 0
    for src_file in filenames:
        if quiet == 0 and len(filenames) > 1:
            print 'Processing files ( %d / %d )' % (fi_processed+1, len(filenames))

        if out_dir == '':
            src_root, ext = os.path.splitext(src_file)
            dst_root = src_root
        else:
            bn = os.path.basename(src_file)
            filetitle, ext = os.path.splitext(bn)
            dst_root = os.path.join(out_dir,filetitle)

        dst_file = dst_root + '.tif'

        ext = ext.lower()
        if ext == '.zip':
            if quiet == 0:
                print 'extracting %s' % src_file
            unzip(src_file,dst_root)

            if quiet == 0:
                print 'translating %s' % dst_root

            if quiet == 0 and verbose == 0:
                progress(0.0)

            fi_processed_in = 0
            file_list = os.listdir(dst_root)

            filelist_file = os.path.join(dst_root,'filelist.txt')
            f = open(filelist_file,'w')

            for file_in in file_list:
                file_in = os.path.join(dst_root,file_in)
                if file_in.find('meta') == -1:
                    convert_jpgis_gml(file_in,file_in+'.tif',driver,[],replace_nodata_by_zero)
                    f.write(file_in+'.tif\n')

                fi_processed_in += 1
                if quiet == 0 and verbose == 0:
                    progress(fi_processed_in / float(len(file_list)))

            f.close()

            if gdal_version >= 1900:
                merge_command = 'gdal_merge' + gdal_merge_ext + gdal_merge_options + ' -o ' + dst_file + ' --optfile ' + filelist_file
                # TODO: testing in Linux
                # Wildcards cannot be used for arguments now. See http://trac.osgeo.org/gdal/ticket/4542 (2012/04/08)
            else:
                merge_command = 'gdalwarp' + gdalwarp_options + ' ' + os.path.join(dst_root,'*.tif') + ' ' + dst_file

            if quiet == 0:
                print 'merging files'
            if verbose:
                print 'executing %s' % merge_command
            os.system(merge_command)

            if quiet == 0:
                print 'removing temporary files'
                print ''
            shutil.rmtree(dst_root)

        elif ext == '.xml' and src_file.find('meta') == -1:
            convert_jpgis_gml(src_file,dst_file,driver,[],replace_nodata_by_zero)

        fi_processed += 1

    if quiet == 0:
        print 'completed'

    return 0

def float2(str):
    lc = ''
    for i in range(len(str)):
        c = str[i]
        if c == lc:
            renzoku += 1
            if renzoku == 6:
                return float(str[:i+1] + c * 10)
        else:
            lc = c
            renzoku = 1

    return float(str)

if __name__ == '__main__':
    sys.exit(main())
