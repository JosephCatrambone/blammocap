
import unittest

import numpy

from camera_models import CameraModel, CameraExtrinsics, CameraIntrinsics

class CameraModelTests(unittest.TestCase):

	def test_lookat(self):
		eye = [1, 3, 2]
		lookat = [4, -2, 8]
		up = [1, 1, 0]
		ext = CameraExtrinsics.from_lookat(eye, lookat, up)
		print(ext.to_matrix())
		# Original from book:
		#numpy.array([
		#	[-0.50709, 0.50709, 0.67612, -2.36643],
		#	[0.76772, 0.60609, 0.12122, -2.82843],
		#	[-0.35857, 0.59761, -0.71714, 0.0],
		#	[0.0, 0.0, 0.0, 1.0],
		#])
		target = numpy.array([
			[-0.50709, 0.50709, 0.67612, -1],
			[0.76772, 0.60609, 0.12122, -3],
			[-0.35857, 0.59761, -0.71714, -2],
			[0.0, 0.0, 0.0, 1.0]
		])
		error = numpy.sum(numpy.abs(ext.to_matrix() - target))
		print(f"Error: {error}")
		assert numpy.allclose(ext.to_matrix(), target, 1e-4)


def render_lookat_demo():
	import numpy
	from PIL import Image
	import math
	import cv2
	w = 640
	h = 480
	points3d = numpy.array([
		[0, 0, 0],
		[-10, -10, 0],
		[10, -10, 0],
		[10, 10, 0],
		[-10, 10, 0]
	])
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	intr = CameraIntrinsics(image_width=w, image_height=h, focal_x=100, focal_y=100)
	out = cv2.VideoWriter("test_anim.mp4", fourcc, 30, (w, h), True)
	for i in range(0, 240):
		extr = CameraExtrinsics.from_lookat(eye=[0, 100*math.sin(i/30), 100], lookat=[0, 0, 0], up=[0, 1, 0])
		c = CameraModel(intrinsics=intr, extrinsics=extr)
		pts = c.transform_points(points3d)
		img = Image.new('RGB', (w, h))
		for j in range(0, pts.shape[0]):
			if 0 <= pts[j,0] < w and 0 <= pts[j,1] < h:
				img.putpixel((int(pts[j,0]), int(pts[j,1])), (255, 0, 255))
			out.write(numpy.asarray(img))
	out.release
