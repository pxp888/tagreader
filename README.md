# Any angle tag reader
### This was a project intended to be a pallet tracking system for warehouses or distribution centers.  
The idea was that cameras mounted above doors and other areas of interest would read a human-readable code on a sticker to record the time and location of any pallet moving underneath it.  

Ideally this would replace a bar code system that was already in place, with the added advantage that it wouldn't require human effort to scan a bar code.  This also had an advantage that it could extend to customers, as it was human readable.  
Essentially, this is just a license plate reader with one complication, sticker tags on pallets may appear in any orientation while cars are generally right side up.  
This required developing a custom network.  
## Steps involved
#### Training Data
To make the job easier a subset of the alphabet was used with characters that are not ambiguous when rotated arbitrarily.  Only capital letters are used, in addition to numerals.  
Rather than having to sample training data this was done automatically by using openCV to distort, skew, scale and rotate these characters as needed.  This may not be as effective as reality, but it worked pretty well.  This is done with the newlettermaker.py script.  

_**Note**- This "generated data" approach worked well enough here, where a simple threshold image to present to the network.  This would not work with a modern system finding characters in raw images._

#### Testing
The network can be tested with the photo.py script which runs through images, or with the video.py script which works with openCV webcam capture video.  
## Results

This system did perform reasonably well, but there is a glaring technical issue.  The pre-processing was done using basic threshold and object separation techniques.  This works, but if even one pixel of a character is touching a neighbor the system will think they are only one letter.  
Important note here, this was done before the development (or at least before I was aware of) CNN neural networks.  

**A modern CNN will have drastically better performance than what is available here, and generally makes this project irrelevant.**  

The concept and use case are still interesting, though.  It really needs to be updated with modern methods for object detection that would bypass the character segmentation issue, at the expense of computational cost.  

