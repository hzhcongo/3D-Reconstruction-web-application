# Script for preparing images and calibration data 
#   for Yasutaka Furukawa's PMVS system

BUNDLER_BIN_PATH= # Edit this line before running
if [ "$BUNDLER_BIN_PATH" == "" ] ; then echo Please edit prep_pmvs.sh to specify the path to the  bundler binaries.; exit; fi
# Apply radial undistortion to the images
$BUNDLER_BIN_PATH/RadialUndistort list.txt bundle/bundle.out pmvs

# Create directory structure
mkdir -p pmvs/txt/
mkdir -p pmvs/visualize/
mkdir -p pmvs/models/

# Copy and rename files
mv pmvs/10.rd.jpg pmvs/visualize/00000000.jpg
mv pmvs/00000000.txt pmvs/txt/
mv pmvs/11.rd.jpg pmvs/visualize/00000001.jpg
mv pmvs/00000001.txt pmvs/txt/
mv pmvs/12.rd.jpg pmvs/visualize/00000002.jpg
mv pmvs/00000002.txt pmvs/txt/
mv pmvs/13.rd.jpg pmvs/visualize/00000003.jpg
mv pmvs/00000003.txt pmvs/txt/
mv pmvs/14.rd.jpg pmvs/visualize/00000004.jpg
mv pmvs/00000004.txt pmvs/txt/
mv pmvs/15.rd.jpg pmvs/visualize/00000005.jpg
mv pmvs/00000005.txt pmvs/txt/
mv pmvs/16.rd.jpg pmvs/visualize/00000006.jpg
mv pmvs/00000006.txt pmvs/txt/
mv pmvs/17.rd.jpg pmvs/visualize/00000007.jpg
mv pmvs/00000007.txt pmvs/txt/
mv pmvs/18.rd.jpg pmvs/visualize/00000008.jpg
mv pmvs/00000008.txt pmvs/txt/
mv pmvs/19.rd.jpg pmvs/visualize/00000009.jpg
mv pmvs/00000009.txt pmvs/txt/
mv pmvs/20.rd.jpg pmvs/visualize/00000010.jpg
mv pmvs/00000010.txt pmvs/txt/
mv pmvs/21.rd.jpg pmvs/visualize/00000011.jpg
mv pmvs/00000011.txt pmvs/txt/
mv pmvs/22.rd.jpg pmvs/visualize/00000012.jpg
mv pmvs/00000012.txt pmvs/txt/
mv pmvs/23.rd.jpg pmvs/visualize/00000013.jpg
mv pmvs/00000013.txt pmvs/txt/
mv pmvs/24.rd.jpg pmvs/visualize/00000014.jpg
mv pmvs/00000014.txt pmvs/txt/
mv pmvs/25.rd.jpg pmvs/visualize/00000015.jpg
mv pmvs/00000015.txt pmvs/txt/
mv pmvs/26.rd.jpg pmvs/visualize/00000016.jpg
mv pmvs/00000016.txt pmvs/txt/
mv pmvs/27.rd.jpg pmvs/visualize/00000017.jpg
mv pmvs/00000017.txt pmvs/txt/
mv pmvs/28.rd.jpg pmvs/visualize/00000018.jpg
mv pmvs/00000018.txt pmvs/txt/
mv pmvs/29.rd.jpg pmvs/visualize/00000019.jpg
mv pmvs/00000019.txt pmvs/txt/
mv pmvs/30.rd.jpg pmvs/visualize/00000020.jpg
mv pmvs/00000020.txt pmvs/txt/
mv pmvs/31.rd.jpg pmvs/visualize/00000021.jpg
mv pmvs/00000021.txt pmvs/txt/
mv pmvs/32.rd.jpg pmvs/visualize/00000022.jpg
mv pmvs/00000022.txt pmvs/txt/
mv pmvs/33.rd.jpg pmvs/visualize/00000023.jpg
mv pmvs/00000023.txt pmvs/txt/
mv pmvs/34.rd.jpg pmvs/visualize/00000024.jpg
mv pmvs/00000024.txt pmvs/txt/
mv pmvs/35.rd.jpg pmvs/visualize/00000025.jpg
mv pmvs/00000025.txt pmvs/txt/
mv pmvs/36.rd.jpg pmvs/visualize/00000026.jpg
mv pmvs/00000026.txt pmvs/txt/
mv pmvs/37.rd.jpg pmvs/visualize/00000027.jpg
mv pmvs/00000027.txt pmvs/txt/
mv pmvs/38.rd.jpg pmvs/visualize/00000028.jpg
mv pmvs/00000028.txt pmvs/txt/

echo "Running Bundle2Vis to generate vis.dat
"
$BUNDLER_BIN_PATH/Bundle2Vis pmvs/bundle.rd.out pmvs/vis.dat



echo @@ Sample command for running pmvs:
echo "   pmvs2 pmvs/ pmvs_options.txt"
echo "    - or - "
echo "   use Dr. Yasutaka Furukawa's view clustering algorithm to generate a set of options files."
echo "       The clustering software is available at http://grail.cs.washington.edu/software/cmvs"
