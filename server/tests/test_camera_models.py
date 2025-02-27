
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
		assert numpy.allclose(
			ext.to_matrix(),
			numpy.array([
				[-0.50709, 0.50709, 0.67612, -2.36643],
				[0.76772, 0.60609, 0.12122, -2.82843],
				[-0.35857, 0.59761, -0.71714, 0.0],
				[0.0, 0.0, 0.0, 1.0],
			])
		)