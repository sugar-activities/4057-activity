from sugar.activity import activity
from main import *

class ChessActivity(activity.Activity):

	def __init__(self, handle):
		print "Initializing activity..."
		activity.Activity.__init__(self, handle)
		print "Running main..."
		main(1200, 900)
		sys.exit(0)