import logging
import yaml

from src.models.input_item import InputItem
class InputParser():

    def __init__(self, items_input_file):
        self.inputs = {}
        with open(items_input_file) as file:
            items_input = yaml.load(file)

            # logging.debug("items_input: %s", items_input)

            for item in items_input:
                input_object = InputItem()
                input_object.name = item.get('name')
                input_object.url = item.get('url')
                input_object.maximum_price = item.get('maximum price')
                input_object.auto_price = item.get('auto price')

                self.inputs[input_object.url] = input_object

    def get_inputs(self):
        return self.inputs
