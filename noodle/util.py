import threading

def within_margin(x, y, margin=0.99):
	s = min(x, y)
	l = max(x, y)
	return s / l >= margin

class DataPoint(list):
	def __init__(self, time, val):
		time, val = float(time), float(val)
		super(DataPoint, self).__init__([time, val])
		self.time = time
		self.val = val
	
	def __str__(self):
		return '{t = %1.4f, val = %1.4f}' % (self.time, self.val)

	__repr__ = __str__

class TimeDataSet(object):

	def __init__(self, window, frame, freq, percentile=95):
		assert 2 * window <= frame
		assert 1 <= percentile <= 99

		self.percentile = percentile / 100.0

		self.freq = freq

		self.window = window
		self.window_buf = []
		self.frame = frame
		self.frame_buf = []
		self.values = []

		self.lock = threading.RLock()

		self.last_time = 0
	
	def __len__(self):
		with self.lock:
			return len(self.frame_buf)

	def __getitem__(self, x):
		with self.lock:
			assert len(self) > 0
			return self.frame_buf[x]

	def __iter__(self):
		with self.lock:
			return iter(self.frame_buf)

	def append(self, data):
		with self.lock:
			# FIXME: if the value is in the past, skip it
			if data.time <= self.last_time:
				return
			self.last_time = data.time

			self.window_buf.append(data)

			# trim the window
			while self.window_buf and data.time - self.window_buf[0].time > self.window:
				self.window_buf.pop(0)
			
			offset = int(round(self.percentile * len(self.window_buf)))
			if offset <= 1 / (1 - self.percentile):
				return

			frame_data = DataPoint(data.time, sorted(self.window_buf, key=lambda x: x.val)[offset].val)
	
			# add the data to the frame, if it's been at least one second
			if not self.frame_buf or data.time - self.frame_buf[-1].time >= self.freq:
				self.frame_buf.append(frame_data)
			
			# trim the frame
			while self.frame_buf and data.time - self.frame_buf[0].time > self.frame:
				self.frame_buf.pop(0)
			
			assert self.frame_buf == sorted(self.frame_buf, key=lambda x: x.time)
			
