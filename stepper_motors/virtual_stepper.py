import time
import matplotlib.pyplot as plt
from math import pi, sin, cos

class VirtualStepper:
	"""
	A visualization of a stepper motor for use in remote learning workshops where not everyone has access to stepper motors.
	"""
	count = 0
	
	def __init__(self, name = None, n_steps = 256, delay = 1e-3):
		"""
		Since virtual steppers are virtual, we don't need pins or step sequences. We're still using delay and n_steps to resemble physical steppers.
		"""
		self.fig, self.ax = plt.subplots(figsize=(3, 3))
		self.n_steps = n_steps
		self.delay = delay
		self.step_size = 2 * pi / self.n_steps

		if name is None:
			self.name = 'Stepper {}'.format(VirtualStepper.count + 1)

		self.angle = 0.0
		self.check()
		self.inv = False
		VirtualStepper.count += 1

		plt.ion()
		plt.show()
		self.draw()

	def draw(self):
		self.ax.cla()
		self.ax.set_title('{}: Angle = {:.2f}$\pi$'.format(self.name, self.angle % (2*pi) / pi))
		self.ax.set_xlim(-1, 1)
		self.ax.set_ylim(-1, 1)

		self.ax.arrow(0, 0, cos(self.angle), sin(self.angle), length_includes_head = True, head_length = 0.3, head_width = 0.1)

		self.fig.canvas.draw()
		plt.pause(1e-3)

	def reverse(self):
		self.inv = True

	def unreverse(self):
		self.inv = False

	def rotate_to(self, angle, degrees = False):
		"""
		Rotates to the angle specified (chooses the direction of minimum rotation)
		"""
		target = angle * pi / 180 if degrees else angle

		curr = self.angle
		diff = (target - curr) % (2*pi)
		if abs(diff - (2*pi)) < diff:
			diff = diff - (2*pi)
		self.rotate_by(diff)

	def rotate_by(self, angle, degrees = False):
		"""
		Rotate the stepper by this angle (radians unless specified)
		Positive angles rotate clockwise, negative angles rotate counterclockwise
		"""
		target = angle * pi / 180 if degrees else angle
		if self.inv:
			target = -target

		if target > 0:
			n = int(target // self.step_size) + 1
			for _ in range(n):
				self.step_c()

		else:
			n = int(-target // self.step_size) + 1
			for _ in range(n):
				self.step_cc()

		if self.inv:
			diff  = -diff

	def zero(self):
		"""
		Resets the position of the stepper to 0
		"""
		self.angle = 0.0
		self.draw()
		time.sleep(self.delay)

	def step_c(self):
		self.angle += self.step_size
		self.angle = self.angle % (2*pi)
		self.draw()
		time.sleep(self.delay)

	def step_cc(self):
		self.angle -= self.step_size
		self.angle = self.angle % (2*pi)
		self.draw()
		time.sleep(self.delay)

	def check(self):
		self.step_c()
		self.step_cc()
