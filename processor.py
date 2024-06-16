import os 
from ultralytics  import YOLO

class ModelProcessor():
	def __init__(self, model_path):
		self.model = YOLO(model_path)

	def __call__(self, img_paths):

		out_paths = []
		results = self.model(img_paths)
		for name, result in zip(img_paths, results):
			out_path = name+"result.jpg"
			result.save(filename=out_path) 
			out_paths += [out_path]
		return out_paths
