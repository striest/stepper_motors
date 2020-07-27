import time
from gpiozero import OutputDevice
from math import pi

class Stepper:
	"""
	Class for position control of stepper motors with Raspberry pi
	Maybe velocity control later. Note that these are open-loop (should probably do a closed-loop one if I buy potentiometers)
	"""
	
	def __init__(self, pin1, pin2, pin3, pin4, step_mode = 'half', n_steps = 512, delay = 1e-2):
		"""
		Stepper motors use four GPIO pins.

		n_steps: The amount of steps required for a full rotation of the stepper motor
		delay: Need a delay to step in the step sequence (0.001 was the highest value tested)
		"""
		assert step_mode in ['full', 'half'], 'Expected step_mode to be one of [\'full\', \'half\']. Got {}'.format(step_mode)
		self.pins = [OutputDevice(pin1), OutputDevice(pin2), OutputDevice(pin3), OutputDevice(pin4)]
		self.n_steps = n_steps
		self.delay = delay
		self.step_size = 2 * pi / self.n_steps
		self.step_idx = 0
		
		if step_mode == 'half':
			self.step_sequence = [
				[1, 0, 0, 1],
				[1, 0, 0, 0],
				[1, 1, 0, 0],
				[0, 1, 0, 0],
				[0, 1, 1, 0],
				[0, 0, 1, 0],
				[0, 0, 1, 1],
				[0, 0, 0, 1]
			]
			self.step_sequence_len = 8
		elif step_mode == 'full':
			self.step_sequence = [
				[1, 1, 0, 0],
				[0, 1, 1, 0],
				[0, 0, 1, 1],
				[1, 0, 0, 1]
			]
			self.step_sequence_len = 4
		
		self.angle = 0.0
		self.check()
		self.inv = False

	def set_step_sequence(self, seq):
		"""
		seq: The step sequence to move clockwise
		"""
		self.step_sequence = seq
		self.step_sequence_len = len(seq)

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
			n = int(target // self.step_size)
			diff = n * self.step_size # Don't accrue error
			for _ in range(n):
				self.step_c()

		else:
			n = int(-target // self.step_size)
			diff = -n * self.step_size
			for _ in range(n):
				self.step_cc()

		if self.inv:
			diff  = -diff

	def zero(self):
		"""
		Resets the position of the stepper to 0
		"""
		self.angle = 0.0

	def assign(self, assignment):
		for i, a in enumerate(assignment):
			if a:
				self.pins[i].on()
			else:
				self.pins[i].off()

	def step_c(self):
		step = self.step_sequence[self.step_idx]
		self.assign(step)
		self.step_idx = (self.step_idx + 1) % self.step_sequence_len
		self.angle += self.step_size
		time.sleep(self.delay)

	def step_cc(self):
		step = self.step_sequence[self.step_idx]
		self.assign(step)
		self.step_idx = (self.step_idx - 1) % self.step_sequence_len
		self.angle -= self.step_size
		time.sleep(self.delay)

	def close(self):
		for pin in self.pins:
			pin.close()

	def check(self):
		self.step_c()
		self.step_cc()
