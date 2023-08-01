import os
import sys
import json
import logging
import urllib3
import warnings
import unittest
import traceback
import time
from time import sleep
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.mobileby import MobileBy as MBy
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.touch_action import TouchAction
urllib3.disable_warnings()
warnings.simplefilter("ignore")

# Custom Libs
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
py_modules_dir = os.path.join(root_dir, 'setup/py_modules' )
sys.path.append(script_dir)
sys.path.append(root_dir)
sys.path.append(py_modules_dir)

import hotstar_lib
from hs_api import hsApi
import kpi_names as kpi_names
import args_lib as args_lib
from hs_logger import logger, setup_logger
import session_visual_lib as session_visual_lib


class TimesIosTest(unittest.TestCase):

	debug = False
	use_capture = True
	video_only = True
	no_reset = True
	app_size_info = False
	autoLaunch = False
	app_name = "YouTube"
	bundle_id = "com.google.ios.youtube"
	package=bundle_id   
	test_name = "Youtube iOS"
	#test_name = "test_session"
	session_type = "page load time"
	implicitly_wait_time = 30
	delta_time = 2
	
	def init_vars(self):
		# Session Configs
		self.KPI_COUNT = 4
		self.pass_count = 0
		self.working_dir = None
		self.private_key_file = None
		self.os = 'iOS'
		self.valid_start = False
		self.speed_value = None
		self.running_on_pbox = False

	def init_workflow(self, video_only=False):
		args, parser = args_lib.get_args(__file__)
		args_lib.init_args(args, self)
		args_lib.init_caps(self, video_only=video_only, auto_launch = self.autoLaunch)    
		#Get the network connections
		hotstar_lib.init_timing(self)

	def setUp(self):
		setup_logger(logger, logging.DEBUG)
		self.init_vars()
		self.init_workflow(video_only=self.video_only)

		logger.info("Starting test")
		# launching app
		# CAREFUL there is api call being made in hsApi init
		self.hs_api_call = hsApi(self.udid, self.access_token)
		# Log Desired Capability for debugging
		self.desired_caps['adbExecTimeout'] = 50000
		# self.desired_caps['headspin:testName'] =self.test_name
		self.driver = webdriver.Remote(self.url, self.desired_caps)
		# Get Device
		r = self.driver.session
		self.udid = r['udid']
		args_lib.device_state_var(self)
		# Log Desired Capability for debugging
		debug_caps = self.desired_caps
		logger.debug('debug_caps:\n'+json.dumps(debug_caps))
		self.session_id = self.driver.session_id


	def tearDown(self):
		try :
			self.driver.quit()
		except :
			print((traceback.print_exc()))

		if not self.valid_start:
			return

		if self.pass_count == self.KPI_COUNT:
			self.status="Pass"
			logger.info(self.status)
		else:
			logger.info("Fail status : " + self.status)
		logger.info("https://ui-dev.headspin.io/sessions/" + self.session_id + "/waterfall")
		#sleep(3)
			
		session_visual_lib.run_record_session_info(self)

		if self.status != "Pass":
			self.fail_count = self.KPI_COUNT - self.pass_count
			'''try :
				page_source = self.driver.page_source
				print('failed page_source')
				print(page_source)
			except :
				print((traceback.print_exc()))'''
		session_visual_lib.run_add_session_data(self)
		logger.info("https://ui-dev.headspin.io/sessions/" + self.session_id + "/waterfall")


	def test_youtube(self):
		self.short_wait = WebDriverWait(self.driver, 5)
		self.wait = WebDriverWait(self.driver, 60)
		self.driver.implicitly_wait(self.implicitly_wait_time)
		self.driver.terminate_app(self.bundle_id)
		sleep(3)
		self.app_launch()
		self.download()
		self.search()
		self.video()
		self.status = "Pass"	


	def download(self):
		self.status="Fail_download_page"
		library = self.driver.find_element(MBy.ACCESSIBILITY_ID, "id.ui.pivotbar.FElibrary.button")
		library.click()
		download = self.driver.find_element(MBy.IOS_PREDICATE, 'label = "Downloads"')
		self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5200
		download.click()
		self.driver.find_element(MBy.NAME, "eml.cvr")
		self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['end'] = int(round(time.time() * 1000)) - 300
		logger.info("Download page found")
		self.pass_count += 1
		sleep(2)
		back = self.driver.find_element(MBy.ACCESSIBILITY_ID, "id.ui.browse.back.button")
		back.click()
		sleep(2)


		self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['start_sensitivity'] = 0.99
		self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['end_sensitivity'] = 0.98

	def search(self):
		self.status="Fail_serach"
		search = self.driver.find_element(MBy.ACCESSIBILITY_ID, "id.ui.navigation.search.button")
		search.click()
		search.send_keys("Titanic movie songs")
		enter = self.driver.find_element(MBy.ACCESSIBILITY_ID, "Search")
		self.kpi_labels[kpi_names.SEARCH_TIME]['start'] = int(round(time.time() * 1000)) + 5000
		enter.click()
		self.driver.find_element(MBy.NAME, "eml.vwc")
		#search_result = self.driver.find_elements(MBy.IOS_PREDICATE, 'label CONTAINS "Search suggestion"')
		self.kpi_labels[kpi_names.SEARCH_TIME]['end'] = int(round(time.time() * 1000)) + 200
		self.pass_count += 1
		logger.info("Search result found")
		sleep(3)

		self.kpi_labels[kpi_names.SEARCH_TIME]['end_sensitivity'] = 0.98
		
		#search_result[0].click()
		# if self.driver.find_elements(MBy.IOS_PREDICATE, 'label CONTAINS "Ad"'):
		# 	play_image =self.driver.find_elements(MBy.XPATH,'//*[@class = "android.widget.ImageView"]//preceding-sibling::android.view.ViewGroup')
		
		#video = self.driver.find_element(MBy.IOS_PREDICATE, 'type == "XCUIElementTypeCollectionView"')
		#video = self.driver.find_element(MBy.NAME, "eml.vwc")

	def video(self):
		self.status="Fail_video_load"
		video = self.driver.find_element(MBy.NAME, "eml.vwc")
		self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5000
		video.click()
		self.driver.find_element(MBy.ACCESSIBILITY_ID, "id.player")
		self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['end'] = int(round(time.time() * 1000)) - 700
		self.pass_count += 1
		logger.info("Video started playing")
		ad = (MBy.IOS_PREDICATE, 'label CONTAINS "Ad"')
		self.short_wait.until(EC.visibility_of_element_located(ad))
		#sleep(2)
		
		self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['end_sensitivity'] = 0.999
		
		try:
			skip_ad = self.driver.find_element(MBy.IOS_PREDICATE, 'label CONTAINS "Skip ad"')
			skip_ad.click()
		except:
			pass
		sleep(30)

	def app_launch(self):
		self.status="Fail_Launch"
		self.driver.implicitly_wait(self.implicitly_wait_time)
		self.session_id = self.hs_api_call.start_session_capture()
		sleep(5)
		self.kpi_labels[kpi_names.LAUNCH_TIME]['start'] = int(round(time.time() * 1000)) + 4500
		self.driver.activate_app(self.bundle_id)
		self.driver.find_element(MBy.NAME, "eml.vwc")
		self.kpi_labels[kpi_names.LAUNCH_TIME]['end'] = int(round(time.time() * 1000)) + 200
		logger.info("App launched")
		self.pass_count += 1
		sleep(3)

	def screen_size_swipe(self):
		screen_size = self.driver.get_window_size()
		self.width = screen_size['width']
		self.height = screen_size['height']
		self.start_x = self.width/2
		self.start_y = self.height * 0.55
		self.end_x = self.width/2
		self.end_y = self.height * 0.3
		self.driver.swipe(self.start_x, self.start_y, self.end_x, self.end_y, 300)


	def get_screen_size(self):
		screen_size = self.driver.get_window_size()
		self.width = screen_size['width']
		self.height = screen_size['height']


if __name__ == '__main__':
	suite = unittest.TestLoader().loadTestsFromTestCase(TimesIosTest)
	unittest.TextTestRunner(verbosity=2).run(suite)
