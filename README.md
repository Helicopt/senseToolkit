# senseToolkit
Useful python functions for computer vision

## Setup
```sh
git clone git@gitlab.bj.sensetime.com:fengweitao/senseToolkit.git
```

## Requirements

Neccessary:
- opencv>=2.4.10
- numpy>=1.12.1

IMGallery optional:
- qimage2ndarray>=1.6
- PyQt4

## Local build(with sudo)
```sh
cd senseToolkit
sudo python2 setup.py build install
```

## Server build(without sudo)
```sh
cd senseToolkit
alias py=/your_local_virtualenv/bin/python2
py setup.py build install
```

## Notes
If cannot find the package, try to add the egg file to your pythonpath

i.e., export PYTHONPATH=$PYTHONPATH:/installed_place/senseToolkit-[version]-[arch].egg

***Now it is only in python2***

## Apps
```sh
python2 -m senseTk.apps.visualize
usage: python2 -m senseTk.apps.visualize [-h] [--ifmt IFMT] [--istart ISTART]
                     [--trackset TRACKSET]
                     src
python2 -m senseTk.apps.VI
usage: python2 -m senseTk.apps.VI [-h] [-t {auto,img,video}] [-i] [--ifmt IFMT] 
			  [--istart ISTART] [--ofmt OFMT] [--ostart OSTART]
              source destination
```

## Docs

### Class TrackSet & Det: a convenient tracklets manager.

```python
>>> from senseTk.common import *
>>> gt = TrackSet('/home/MOT/train/MOT16-04/gt/gt.txt') #open a file in MOT format
>>> for i in gt[1]:
...     print i # print all items in frame 1
... 
1,1,1363.00,569.00,103.00,241.00,0.860,1,1,-1
1,2,371.00,410.00,80.00,239.00,1.000,1,1,-1
1,3,103.00,549.00,83.00,251.00,1.000,1,1,-1
1,4,1734.00,457.00,76.00,213.00,0.984,1,1,-1
1,5,1098.00,980.00,78.00,208.00,0.483,1,1,-1
1,6,632.00,761.00,100.00,251.00,0.319,1,1,-1
1,7,623.00,901.00,144.00,123.00,1.000,11,0,-1

>>> for i in gt(1).frameRange():           
...     print gt(1)[i][0] # print the target who's id is 1, in all frames
... 
1,1,1363.00,569.00,103.00,241.00,0.860,1,1,-1
2,1,1362.00,568.00,103.00,241.00,0.862,1,1,-1
3,1,1362.00,568.00,103.00,241.00,0.862,1,1,-1
4,1,1362.00,568.00,103.00,241.00,0.862,1,1,-1
5,1,1362.00,568.00,103.00,241.00,0.862,1,1,-1

>>> d = Det(1,1,50,50,uid=1,fr=2,confidence=2) # all structures in TrackSet in Det
>>> print d
2,1,1.00,1.00,50.00,50.00,2.000,None,-1,-1
>>> d.x1, d.y1, d.w, d.h, d.cx, d.cy, d.x2, d.y2 # all kinds of coordinates
(1, 1, 50, 50, 26, 26, 51, 51)


```

Class Det:

- area()

  returns the area of the Det

- intersection(anotherDet)

  returns the intersection of the two Det

- union(anotherDet)

  returns the union of the two Det

- iou(anotherDet)

  returns the iou of the two Det

- lt(ox = 0, oy = 0, trim = True)

  returns the left-top point with offset(ox, oy), auto trim to int (useful in cv2.rectangle or other paint functions)

- rb(ox = 0, oy = 0, trim = True)

  returns the right-bottom point with offset(ox, oy), auto trim to int (useful in cv2.rectangle or other paint functions)

- _trim(sz = None, toInt = True)

  inplace function to trim to integer

- trim(sz = None, toInt = True)

  function to trim to integer (copy)

- _astype(dtype)

  inplace function to change to dtype

- astype(dtype)

  function to change to dtype (copy)

- toList()

  to [x1, y1, w, h]

- toTuple()

  to (x1, y1, w, h)

Class TrackSet:
```python
def __init__(self, fn = None, dealer = None, filter = None, formatter = None):
```
- if dealer is set, each row will be sent to dealer and the dealer is expected to return a Det
- if filter is set, only the rows satisfy filter(row) will be added
- if formatter is set, all rows will be formatted with the formatter, otherwise all rows will be read in MOT format or labeled format (auto-select)
> A formatter includes items in [fr, id, la, cf, st] and coordinates in [x1, y1, w, h, cx, cy, x2, y2]
>
> normally, there are three styles to read coordinates, [x1, y1, w, h] or [cx, cy, w, h] or [x1, y1, x2, y2]
>
> fr is the frame id, id is the target id, la is the label, cf is confidence, st is status
>
> then we use ".type" to format the data type, "i" for integer, "f" for float, "s" for string, default choice is float
>
> e.g., "fr.i,id.i,x1,y1,w,h,-1,st.i,-1,-1" is one format, meaning fr and id is integers and x1, y1, w, h is float and st is integer, other places filled with -1(or other something) will be all ignored.

- allPed()

  returns a list contains all target id

- allFr()

  returns a list contrains all frame numbers

- append_data(det)

  append a new det into trackset

- frameRange()

  return a list of [minimum_fr, ..., maximum_fr]

- dump(fd, formatter = 'MOT16', filter = None)

  dump to filedescripter fd using formatter and filter function

- toJson(frfirst = False, filter = None)

  returns a dict contains all information

- We can using slice to split frames like this: (useful for tracklets split and merge problems)

```python
>>> gt = TrackSet('/home/MOT/train/MOT16-04/gt/gt.txt')
>>> b = gt[50:100] # copy frames ranging from 50 to 100
>>> gt[50:100]=None # delete original frames

```

### Class VideoClipReader & VideoClipWriter: a convenient video wrapper merging nomal video and images set

VideoClipReader:

```python
v = VideoClipReader('./MOT16-04.avi') # normal video
v = VideoClipReader('./MOT16-04/imgs') # a directory contains all images of a video
v.read() # return status, image
v.get(cv2.cv.CV_CAP_PROP_FPS) # same method as opencv
v.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 50) # same method as opencv
v.length()
v.fps()
v.ImgSize()
v.release()
# more convenient methods
```

VideoClipWriter:

```python
def __init__(self, path, video_type, fps = 25.0, size = None, fmt = ImgVideoCapture.DEFAULT_FMT, start = 1):
# video_type: VideoClipWriter.NORAML_VIDEO or VideoClipWriter.IMG_VIDEO
# if normal type: size and fps are needed
# if img type: fmt and start is needed
# fmt: DEFAULT_FMT = '%06d.jpg', it's a string to format pictures' names, start is offset
vidwriter.write(img)
vidwriter.release()
```

