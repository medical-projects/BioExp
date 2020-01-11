import keras
import random
import numpy as np
from glob import glob
from keras.models import Model
from keras.utils import np_utils
from keras.models import load_model
import matplotlib.pyplot as plt

import sys
sys.path.append('..')
from helpers.losses import *
from helpers.utils import load_vol_brats

class intervention():

	def __init__(self, model):
		self.model = model

	def mean_swap(self, test_path, plot = False):

		channel = 3

		vol_path = glob(test_path)
		test_image, gt = load_vol_brats(vol_path[0], slicen = 78, pad = 0)

		prediction = np.argmax(self.model.predict(test_image[None, ...]), axis = -1)[0]
		n_classes = (len(np.unique(prediction)))
		corr = np.zeros((n_classes, n_classes))
		slices = list(range(20, 125, 10))

		for vol in vol_path:
			for slicen in slices:

				test_image, gt = load_vol_brats(vol, slicen = slicen, pad = 0)

				prediction = np.argmax(self.model.predict(test_image[None, ...]), axis = -1)[0]
				print("Original Dice Whole:", dice_whole_coef(prediction, gt))

				class_dict = {0:'bg', 1:'core', 2:'edema', 3:'enhancing'}

				plt.figure(figsize = (20,20))
				corr_temp = np.zeros((n_classes, n_classes))
				for i in range(n_classes):
					for j in range(n_classes):
						new_mean = np.mean(test_image[gt == i], axis = 0)
						old_mean = np.mean(test_image[gt == j], axis = 0)
						test_image_intervention = np.copy(test_image)
						test_image_intervention[gt == j] += (new_mean - old_mean)
						prediction_intervention = np.argmax(self.model.predict(test_image_intervention[None, ...]), axis = -1)[0]
						if plot == True:
							plt.subplot(n_classes, n_classes, 1+4*i+j)
							plt.xticks([])
							plt.yticks([])
							plt.title("{} --> {}".format(class_dict[j], class_dict[i]))
							plt.imshow(prediction_intervention, cmap = plt.cm.RdBu, vmin = 0, vmax = 3)
							plt.colorbar()
						
						corr[i,j] += dice_label_coef(prediction, gt, (j,)) - dice_label_coef(prediction_intervention, gt, (j,))
						corr_temp[i,j] += dice_label_coef(prediction, gt, (j,)) - dice_label_coef(prediction_intervention, gt, (j,))
				# print(corr_temp)

		np.set_printoptions(precision = 2, suppress = True)
		print(corr/(len(vol_path)*len(slices)))
		if plot == True:
			plt.show()

		# print(test_image[gt == 3].shape)

		# new_mean = np.mean(test_image[gt == 3], axis = 0)
		# print(new_mean)

		# plt.subplot(2, 2, 1)
		# plt.imshow(test_image[:, :, channel], cmap = plt.cm.RdBu, vmin = -2, vmax = 3)
		# plt.colorbar()
		# plt.subplot(2, 2, 3)
		# plt.imshow(prediction, cmap = plt.cm.RdBu, vmin = 0, vmax = 3)
		# plt.colorbar()
		# # plt.show()

		# old_mean = np.mean(test_image[gt == 2], axis = 0)
		# print(old_mean)
		# test_image[gt == 2] += (new_mean - old_mean)
		# print(np.mean(test_image[gt == 2], axis = 0))

		# prediction_intervention = np.argmax(self.model.predict(test_image[None, :, :, channel, None]), axis = -1)[0]

		# plt.subplot(2, 2, 2)
		# plt.imshow(test_image[:, :, channel], cmap = plt.cm.RdBu, vmin = -2, vmax = 3)
		# plt.colorbar()
		# plt.subplot(2, 2, 4)
		# plt.imshow(prediction_intervention, cmap = plt.cm.RdBu, vmin = 0, vmax = 3)
		# plt.colorbar()
		# plt.show()


		# print(dice_whole_coef(prediction, gt))


if __name__ == "__main__":

	model = load_model('/home/parth/Interpretable_ML/saved_models/U_resnet/ResUnet.h5', 
                custom_objects={'gen_dice_loss':gen_dice_loss,
                                'dice_whole_metric':dice_whole_metric,
                                'dice_core_metric':dice_core_metric,
                                'dice_en_metric':dice_en_metric})

	model.load_weights('/home/parth/Interpretable_ML/saved_models/U_resnet/ResUnet.40_0.559.hdf5')


	I = intervention(model)

	I.mean_swap('/home/parth/Interpretable_ML/BioExp/sample_vol/brats/**')

