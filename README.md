# senseToolkit
Python functions for computer vision

# setup

git clone git@gitlab.bj.sensetime.com:fengweitao/senseToolkit.git

# local build(with sudo)
```sh
cd senseToolkit
sudo python2 setup.py build install
```
# server build(without sudo)
```sh
cd senseToolkit
alias py=/your_local_virtualenv/bin/python2
py setup.py build install
```
# notes

if cannot find the package, try to add the egg file to your pythonpath

i.e., export PYTHONPATH=$PYTHONPATH:/installed_place/senseToolkit-[version]-[arch].egg

# apps
```sh
python2 -m senseTk.apps.visualize [video] [--trackset [tracksetfilepath]]

python2 -m VI 
usage: python2 -m VI [-h] [-t {auto,img,video}] [-i] [--ifmt IFMT] [--istart ISTART]
	[--ofmt OFMT] [--ostart OSTART]
	source destination
```
# requirements
neccessary:
- opencv>=2.4.10
- numpy>=1.12.1

IMGallery optional:
- qimage2ndarray>=1.6
- PyQt4

