Feature Tracking
================

Target Selection
----------------

On VMXi, the width of the X-ray beam is only a few microns. Since each well is a few mm across, this means that it is not practical to scan the entirety of each well with the beam. This is both because of the amount of time that it would take and because the heat generated by doing so would quickly destroy the sample. Therefore, it is necessary to be selective about the section/s of each well that will be scanned by the beam. To this end, the beamline provides a web application that the users can make use of (remotely), that allows them to view images of their wells and mark points or areas of interest on each one so that it can be scanned.

![Single Bubble with Marked Crystals](img/bubble2.jpg)

Sample plates will be stored in a special purpose refrigerator/imager system in the beamline hutch and a robot will transfer them from the refrigerator to the beam sample chamber when required. When the plate is loaded into the fridge (and periodically after that), an image will be taken of each well in the plate. When the user accesses the web application, the most recent image will be shown to them for target selection.

The refrigerator system is the [Formulatrix Rock Imager](http://www.formulatrix.com/protein-crystallization/products/rock-imager-1000). It can store up to 1000 plates at a time and automatically handles the regular imaging.

![Formulatrix Rock Imager 1000](img/formulatrix.jpg)


The Problem
-----------
An issue that arises is that between the time that the user selects their targets and the time when the sample is actually scanned, it is possible for the sample in the well to move around to some degree. In the example image above, the most likely thing is that the individual crystals could move around within the bubble. This can occur due to natural motion, as well as when the sample is moved from the refrigerator to the beam. In particular there is an issue because the plates will be stored horizontally in the fridge but will be held vertically when being scanned in the beam, and so they could move under gravity.

It is necessary then to be able to identify the current position of any selected features/areas at the time when the sample is actually being scanned. There will be a digital camera on the beamline which will be able to take high resolution images of the sample wells just before they are scanned. Also the position of the plate can be controlled using very high precision motors (to scan the beam across the sample, the sample itself moves rather than the beam, as the beam position is fixed).

Therefore what is needed is a software tool that can compare an image taken in the fridge and one taken on the beamline, and track any movement of features that have been selected as targets by the user. This information is then translated into precise motion signals to control the position of the sample plate and make sure that the feature/s that the user selected are properly scanned by the beam.

It should be noted that during the sample growing process, the shape and appearance of any crystals (and the bubble as a whole) will change dramatically. This should hopefully occur mostly prior to the sample being placed in the fridge and the first image taken and so we needn't worry about it much.

Inputs and Outputs
------------------
For each sample, the inputs to the program will with Formulatrix and Beamline images of the sample well and the set of points (in pixel coordinates) that the user marked in the Formulatrix image.
 
The expected output will be the set of x,y motor coordinates that the plate needs to be moved to in order to accurately image the selected region/s.

The program is currently being developed with a GUI for development and testing, but the deployed application will be running continuously and automatically so will need to be able to communicate with other VMXi software components.


Focus Stacking
--------------
Images taken in the fridge use a Z-focusing mode where the well is imaged multiple times at different focal depths. An operation is then performed which merges the set of images into a single composite image in which every part of the image is in sharp focus. The Imager control software performs this operation automatically. This composite image is displayed to the user for them to select targets.

When the user selects a feature, the system will need to figure out which Z-slice has the feature in best focus. This feature will be important if the scan will include rotation of the sample, as we will need to know the Z-coordinate of the crystal within the sample bubble. For planar scanning, the Z-depth wont matter much as the plate will always be normal to the beam.

It is necessary to perform this same operation when images are being taken of the sample on the beamline.
The app implements a pyramid based [focusing method](http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf) found on [github](https://github.com/sjawhar/focus-stacking).
It creates one all-in-focus image from a set of Z-sliced images which is used in the further steps of the algorithm.
The app also finds (for each feature selected by the user) the index of the Z-slice which has the best focus.

Real Time Constraint
--------------------
The beamline is intended to be very high throughput. The whole scanning operation for a single well should take on the order of 1 second. For this reason, the image matching algorithm needs to run very quickly. The image matching program will run on a dedicated machine, and there is budget available to use a high performance server specifically to run it if needed.
At the moment the image matching algorithm does quite good job in terms of speed but the focusing phase is slow and takes 80% of the calculation time.

Further Details
---------------

It is likely that the images from the wells will be close-ups of the bubbles, not pictures of the whole well. Each well is divided into two or three small sub-regions (differs depending on the brand/type of plate); so the bubbles wont be randomly distributed but will be in reasonably defined positions. Presumably images will be labelled by the sub-region, e.g., ' Plate X39241, Well B6, Bubble 2'. Obviously the positions of the bubble will vary slightly between the fridge and beam images, but as long as we know the camera offset, this shouldn't be  a problem.

While we hope for nice clean, round bubbles with well defined crystals, this will not be the norm. The pictures can contain all kinds of crazy weirdness, including nice bubbles with weird amorphous rubbish, or no bubble at all. There are some samples on ISpyB and on various xtal-pims databases that will give us an idea of what to expect. We need to look into this in further detail.

The samples will be imaged repeatedly once they are in the fridge, however most of the data wont be of interest to us. It is only at the point where the user has marked the image for analysis that we will be interested in it. Apparently nobody has studied the long term movements of crystal features so the movement data should be kept long term so that this can be undertaken.


VMXi Workflow Diagram
---------------------

![VMXi Workflow Diagram](https://github.com/DiamondLightSource/CrystalMatch/blob/master/docs/img/workflow.jpg)