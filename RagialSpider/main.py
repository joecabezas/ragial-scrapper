import logging
import json

from src.ragial_job_generator import RagialJobGenerator
from src.input_parser import InputParser

class Main():

	INPUT_ITEMS_FILE = 'configuration/items.yaml'

	def __init__(self):
		logging.getLogger().setLevel(logging.DEBUG)
		self.input_parser = InputParser(self.INPUT_ITEMS_FILE)
		self.ragial_job_generator = RagialJobGenerator(self.input_parser.inputs)

	def get_jobs(self):
		return self.ragial_job_generator.get_jobs()

if __name__ == '__main__':
	main = Main()
	print json.dumps(main.get_jobs(), indent=4)