#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Tue Apr 26 17:25:41 2011 +0200
#
# Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

"""Tests the affine transformations
"""

import math
import numpy
import nose.tools
from nose.plugins.skip import SkipTest

import bob.io.base
import bob.io.base.test_utils
import bob.io.image

import bob.ip.base

regenerate_reference = False

###############################################
########## scaling ############################
###############################################

scale_src = numpy.array([
    [  0,   2,   4,   6],
    [  2,   4,   8,  12],
    [  4,   8,  16,  24],
    [  8,  16,  32,  48]],
    dtype=numpy.uint8)

# Reference values
scaled_ref_2by2 = numpy.array([[0, 6], [8, 48]], dtype=numpy.float64)
scaled_ref_8by8 = numpy.array([
    [  0.        ,  0.85714286,  1.71428571,  2.57142857,  3.42857143,  4.28571429,  5.14285714,  6.        ],
    [  0.85714286,  1.71428571,  2.57142857,  3.67346939,  4.89795918,  6.12244898,  7.34693878,  8.57142857],
    [  1.71428571,  2.57142857,  3.42857143,  4.7755102 ,  6.36734694,  7.95918367,  9.55102041, 11.14285714],
    [  2.57142857,  3.67346939,  4.7755102 ,  6.6122449 ,  8.81632653, 11.02040816, 13.2244898 , 15.42857143],
    [  3.42857143,  4.89795918,  6.36734694,  8.81632653, 11.75510204, 14.69387755, 17.63265306, 20.57142857],
    [  4.57142857,  6.53061224,  8.48979592, 11.75510204, 15.67346939, 19.59183673, 23.51020408, 27.42857143],
    [  6.28571429,  8.97959184, 11.67346939, 16.16326531, 21.55102041, 26.93877551, 32.32653061, 37.71428571],
    [  8.        , 11.42857143, 14.85714286, 20.57142857, 27.42857143, 34.28571429, 41.14285714, 48.        ]],
    dtype=numpy.float64)


def test_scale_regular():
  # Use scaling where both output and input are arguments
  scaled_2by2 = numpy.ndarray((2,2))
  bob.ip.base.scale(scale_src, scaled_2by2)
  assert numpy.allclose(scaled_2by2, scaled_ref_2by2, atol=1e-7)

  scaled_8by8 = numpy.ndarray((8,8))
  bob.ip.base.scale(scale_src, scaled_8by8)
  assert numpy.allclose(scaled_8by8, scaled_ref_8by8, atol=1e-7)

  scaled_2by8 = numpy.ndarray((2,8))
  bob.ip.base.scale(scale_src, scaled_2by8)
  assert numpy.allclose(scaled_2by8, scaled_ref_8by8[(0,-1),:])


def test_scale_mask():
  # TODO: implement
  raise SkipTest("This functionality is (yet) untested")


def test_scale_factor():
  # Use scaling where the output size is provided as a scaling factor
  scaled_2by2 = bob.ip.base.scale(scale_src, 0.5)
  assert numpy.allclose(scaled_2by2, scaled_ref_2by2, atol=1e-7)

  scaled_8by8 = bob.ip.base.scale(scale_src, 2.)
  assert numpy.allclose(scaled_8by8, scaled_ref_8by8, atol=1e-7)

  color_src = numpy.array((scale_src, scale_src, scale_src))
  scaled_3by8by8 = bob.ip.base.scale(color_src, 2.)
  for i in range(3):
    assert numpy.allclose(scaled_3by8by8[i], scaled_ref_8by8, atol=1e-7)


def test_get_scaled_output_shape():
  shape_2by2 = bob.ip.base.get_scaled_output_shape(scale_src, 0.5)
  assert shape_2by2 == (2,2)

  shape_8by8 = bob.ip.base.get_scaled_output_shape(scale_src, 2.)
  assert shape_8by8 == (8,8)


def test_scale_non_round():
  i = numpy.ones((285,193))
  scaled = bob.ip.base.scale(i, 3.18467)
  assert numpy.allclose(scaled, 1.)



###############################################
########## rotating ###########################
###############################################

def test_rotate():
  # load input image
  image = bob.io.base.load(bob.io.base.test_utils.datafile("image.pgm", "bob.ip.base", "data/affine"))

  # rotate the face with 10 degree
  image_r10 = bob.ip.base.rotate(image, 10.)
  normalized_r10 = numpy.round(image_r10).astype(numpy.uint8)

  # compare with reference
  reference_file_r10 = bob.io.base.test_utils.datafile("image_r10.pgm", "bob.ip.base", "data/affine")
  if regenerate_reference:
    bob.io.base.save(normalized_r10, reference_file_r10)
  reference_r10 = bob.io.base.load(reference_file_r10)
  assert numpy.allclose(normalized_r10, reference_r10)

  # rotate the face with 70 degree
  image_r70 = numpy.ndarray(bob.ip.base.get_rotated_output_shape(image, 70))
  bob.ip.base.rotate(image, image_r70, 70)
  normalized_r70 = numpy.round(image_r70).astype(numpy.uint8)

  # compare with reference
  reference_file_r70 = bob.io.base.test_utils.datafile("image_r70.pgm", "bob.ip.base", "data/affine")
  if regenerate_reference:
    bob.io.base.save(normalized_r70, reference_file_r70)
  reference_r70 = bob.io.base.load(reference_file_r70)
  assert numpy.allclose(normalized_r70, reference_r70)


def test_rotate_mask():
  # TODO: implement
  raise SkipTest("This functionality is (yet) untested")


###############################################
########## GeomNorm ###########################
###############################################

def test_geom_norm_simple():
  # tests the geom-norm functionality (copied from old C++ tests)

  test_image = bob.io.base.load(bob.io.base.test_utils.datafile("image_r10.pgm", "bob.ip.base", "data/affine"))
  processed = numpy.ndarray((40, 40))

  # Define a Geometric normalizer
  # * rotation angle: 10 degrees
  # * scaling factor: 0.65
  # * Cropping area: 40x40
  geom_norm = bob.ip.base.GeomNorm(-10., 0.65, (40, 40), (0, 0))

  # Process giving the upper left corner as the rotation center (and the offset of the cropping area)
  geom_norm(test_image, processed, (54, 27));

  # compute normalized image
  normalized = numpy.round(processed).astype(numpy.uint8)

  # This is the actual test image that was copied from the old implementation of Bob
  reference_file = bob.io.base.test_utils.datafile("image_r10_geom_norm.pgm", "bob.ip.base", "data/affine")
  if regenerate_reference:
    bob.io.base.save(normalized, reference_file)

  reference_image = bob.io.base.load(reference_file)

  assert numpy.allclose(normalized, reference_image)


def test_geom_norm_with_mask():
  # tests the geom-norm functionality with masks (copied from old C++ tests)

  test_image = bob.io.base.load(bob.io.base.test_utils.datafile("image_r70.pgm", "bob.ip.base", "data/affine"))
  processed = numpy.ndarray((160, 160))

  test_mask = test_image != 0;
  processed_mask = numpy.ndarray(processed.shape, numpy.bool);

  # Define a Geometric normalizer
  # * rotation angle: 70 degrees
  # * scaling factor: 1.2
  # * Cropping area: 160x160
  # cropping offset: 80x80
  geom_norm = bob.ip.base.GeomNorm(-70., 1.2, (160, 160), (80, 80))

  # Process giving the masks and the center of the eye positions
  geom_norm(test_image, test_mask, processed, processed_mask, (64, 69))

  # compute normalized image
  normalized = numpy.round(processed).astype(numpy.uint8)
  mask = processed_mask.astype(numpy.uint8)*255

  # This is the actual test image that was copied from the old implementation of Bob
  reference_file = bob.io.base.test_utils.datafile("image_r70_geom_norm.pgm", "bob.ip.base", "data/affine")
  if regenerate_reference:
    bob.io.base.save(normalized, reference_file)
  reference_image = bob.io.base.load(reference_file)
  assert numpy.allclose(normalized, reference_image)

  # This is the actual test mask that was copied from the old implementation of Bob
  mask_file = bob.io.base.test_utils.datafile("image_r70_mask.pgm", "bob.ip.base", "data/affine")
  if regenerate_reference:
    bob.io.base.save(mask, mask_file)
  reference_mask = bob.io.base.load(mask_file)
  assert numpy.allclose(mask, reference_mask)


def test_geom_norm_position():
  # generate geometric normalizer that rotates by 45 degrees, scales by 2 and moves to new center (40,80)
  # (the image resolution aka cropping area 160x160 is not required for this test...)
  geom_norm = bob.ip.base.GeomNorm(45., 2., (160, 160), (40, 80))

  # define positions to be rotated
  position = (15,25)

  # we take an offset of 20,20 to rotate the point
  # the centered point is hence (-5,5)
  rotated = geom_norm(position,(20,20))

  # check the new position
  # new y-value should be 0 plus offset
  # new x value is the length of the centered vector (i.e. 5*sqrt(2)) times the scaling factor 2 plus offset
  assert numpy.allclose(rotated, (40, 80. + 5. * math.sqrt(2.) * 2))


###############################################
########## FaceEyesNorm #######################
###############################################

def test_face_eyes_norm():
  # load test image
  test_image = bob.io.base.load(bob.io.base.test_utils.datafile("image_r10.pgm", "bob.ip.base", "data/affine"))
  processed = numpy.ndarray((40, 40))

  fen = bob.ip.base.FaceEyesNorm((40, 40), 20, (5/19.*40, 20))

  # Process giving the coordinates of the eyes
  fen(test_image, processed, (67,47), (62,71))
  normalized = numpy.round(processed).astype(numpy.uint8)

  reference_file = bob.io.base.test_utils.datafile("image_r10_face_eyes_norm.pgm", "bob.ip.base", "data/affine")
  if regenerate_reference:
    bob.io.base.save(normalized, reference_file)

  reference_image = bob.io.base.load(reference_file)

  assert numpy.allclose(normalized, reference_image)


