"""This is code taken from https://github.com/sjawhar/focus-stacking
which implements the methods described in http://www.ece.drexel.edu/courses/ECE-C662/notes/LaplacianPyramid/laplacian2011.pdf"""
from multiprocessing import Queue, Process

import numpy as np

import logging

from dls_focusstack.focus.pyramid import Pyramid
from dls_imagematch import logconfig

from pyramid_level import PyramidLevel

def entropy_diviation(pyramid_layer,kernel_size,q):
    """On the top level of the pyramid (the one with the lowest resolution) two fusion operators:
    entropy and deviation are used"""
    gray_image = pyramid_layer
    gray_image.entropy(kernel_size)
    gray_image.deviation(kernel_size)

    log = logging.getLogger(".".join([__name__]))
    log.addFilter(logconfig.ThreadContextFilter())
    log.debug("Calculated entropy/div for top level of layer: " + str(gray_image.get_layer_number()))

    q.put(gray_image)

def fused_laplacian(laplacians, region_kernel, level, q):
    """On other levels of the pyramid one fusion operator: region energy is used"""
    layers = laplacians.shape[0]
    region_energies = np.zeros(laplacians.shape[:3], dtype=np.float64)

    for layer in range(layers):
        gray_lap = PyramidLevel(laplacians[layer], layer, level)
        region_energies[layer] = gray_lap.region_energy(region_kernel)

    best_re = np.argmax(region_energies, axis=0)
    fused = np.zeros(laplacians.shape[1:], dtype=laplacians.dtype)

    for layer in range(layers):
        fused += np.where(best_re[:, :] == layer, laplacians[layer], 0)

    log = logging.getLogger(".".join([__name__]))
    log.addFilter(logconfig.ThreadContextFilter())
    log.debug("Level: " + str(level) + " fused!")

    fused_level = PyramidLevel(fused,0,level)
    q.put(fused_level)

class PyramidCollection:
    """Pyramid collection has is an array with 4 dimensions: level, layer, image wight and image height
    number of levels is defined by pyramid depth
    number of layers is the number of input images each one focused on a different z-level"""
    def __init__(self):
        self.collection = []

    def add_pyramid(self, pyramid):
        self.collection.append(pyramid)

    def get_pyramid(self, layer_number):
        return self.collection[layer_number]

    def get_region_kernel(self):
        a = 0.4
        kernel = np.array([0.25 - a / 2.0, 0.25, a, 0.25, 0.25 - a / 2.0])
        return np.outer(kernel, kernel)

    def fuse(self, kernel_size):
        """Function which fuses each level of the pyramid using appropriate fusion operators
        the output is a 3 dimensional array (level, image wight, image high)
        - the input array is flattened along layers"""
        log = logging.getLogger(".".join([__name__, self.__class__.__name__]))
        log.addFilter(logconfig.ThreadContextFilter())

        base_level_fused = self.get_fused_base(kernel_size)
        depth = self.collection[0].get_depth()
        fused = Pyramid(depth,0)
        fused.add_lower_resolution_level(base_level_fused)
        layers = len(self.collection)

        q = Queue()
        processes = []
        region_kernel = self.get_region_kernel()

        for level in range(depth - 2, -1, -1):
            sh = self.collection[0].get_level(level).get_array().shape
            laplacians = np.zeros((layers, sh[0], sh [1]), dtype=np.float64)
            for layer in range(0, layers):
                new_level = self.collection[layer].get_level(level).get_array()
                laplacians[layer] = new_level

            process = Process(target=fused_laplacian, args=(laplacians, region_kernel, level, q))
            process.start()
            processes.append(process)

        for level in range(depth - 2, -1, -1):
            pyramid_level = q.get()
            fused.add_highier_resolution_level(pyramid_level)

        for p in processes:
            p.join() #this one won't work if there is still something in the Queue

        fused.sort_levels()
        return fused

    def get_fused_base(self, kernel_size):
        """Fuses the base of the pyramid - the one with the lowest resolution."""

        layers = len(self.collection)
        sh = self.collection[0].get_top_level().get_array().shape
        pyramid = self.collection[0]
        top_level_number = pyramid.get_depth() - 1
        entropies = np.zeros((layers, sh[0], sh [1]), dtype=np.float64)
        deviations = np.copy(entropies)
        q = Queue()
        processes = []
        for layer in range(layers):
            pyramid = self.collection[layer]
            top_pyramid_level = pyramid.get_top_level()
            layer = PyramidLevel(top_pyramid_level.get_array(), layer, top_level_number)

            process = Process(target=entropy_diviation, args=(layer, kernel_size, q))
            process.start()
            processes.append(process)

        for layer in range(layers):
            #should always do all threads as all the processes are the same and should take roughly the same time
            l = q.get() #picks the first one which is ready
            entropies[l.get_layer_number()] = l.get_entropies()
            deviations[l.get_layer_number()] = l.get_deviations()

        for p in processes:
            p.join() #this one won't work if there is still something in the Queue

        best_e = np.argmax(entropies, axis=0) #keeps the layer numbers
        best_d = np.argmax(deviations, axis=0)
        fused = np.zeros(best_d.shape, dtype=np.float64)

        for layer in range(layers):
            array_tmp = self.collection[layer].get_top_level().get_array()
            fused += np.where(best_e[:, :] == layer, array_tmp, 0)
            fused += np.where(best_d[:, :] == layer, array_tmp, 0)

        new_array = (fused / 2)
        return PyramidLevel(new_array,0,top_level_number) # layer 0 ???

