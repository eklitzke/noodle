import math

def hsv_to_rgb(h, s, v):
	"""Convert HSV to RGB"""

	h, s, v = float(h), float(s), float(v)
	hi = int(math.floor(h / 60)) % 6
	f = h / 60 - math.floor(h / 60)
	p = v * (1 - s)
	q = v * (1 - f * s)
	t = v * (1 - (1 - f) * s)
	if hi == 0:
		return v, t, p
	elif hi == 1:
		return q, v, p
	elif hi == 2:
		return p, v, t
	elif hi == 3:
		return p, q, v
	elif hi == 4:
		return t, p, v
	elif hi == 5:
		return v, p, q
