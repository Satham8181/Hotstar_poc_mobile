import os
import unittest
import sys
import json
import logging
import time
import urllib3
import warnings
import traceback
from time import sleep
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from appium.webdriver.common.mobileby import MobileBy as MBy
from selenium.webdriver.support import expected_conditions as EC

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


class BupaAndroidTest(unittest.TestCase):

    debug = False
    use_capture = False
    video_only = True
    no_reset = True
    app_size_info = False
    autoLaunch = False
    app_name = "Netflix"
    package = "com.netflix.mediaclient"
    activity = "com.netflix.mediaclient.ui.launch.UIWebViewActivity" 
    #activity = "com.netflix.mediaclient.ui.profiles.ProfileSelectionActivity"
    #test_name = "Netflix Android"
    #test_name = "test_session"
    test_name = "Netflix Android"
    session_type = "page load time"
    implicitly_wait_time = 10
    delta_time = 1

    def init_vars(self):
        # Session Configs
        self.KPI_COUNT = 8
        self.pass_count = 0
        self.working_dir = None
        self.private_key_file = None
        self.os = 'Android'
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
            # self.driver2.quit()
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
        self.device_model ="CD"
        print("Dut session ID - TearDown",self.dut_session_id)
        session_visual_lib.run_record_session_info(self)
        if self.status != "Pass":
            self.fail_count = self.KPI_COUNT - self.pass_count
            # '''try :
            #     page_source = self.driver.page_source
            #     print('failed page_source')
            #     print(page_source)
            # except :
            #     print((traceback.print_exc()))'''
        session_visual_lib.run_add_session_data(self)
        logger.info("https://ui-dev.headspin.io/sessions/" + self.session_id + "/waterfall")
        self.session_id=self.dut_session_id
        self.device_model ="DUT"
        # session_visual_lib.run_record_session_info(self)
        session_visual_lib.run_add_session_data(self)


    def test_hotstar(self):
        self.short_wait = WebDriverWait(self.driver, 6)
        self.wait = WebDriverWait(self.driver, 20)
        self.long_wait =  WebDriverWait(self.driver, 30)
        self.driver.implicitly_wait(self.implicitly_wait_time)
        self.driver.terminate_app(self.package)
        #self.get_screen_size()
        self.app_launch()
        self.download_tab()
        self.search()	
        self.video()	
        self.downloads()
        self.status = "Pass"   

    
    def app_launch(self):
        self.status="Fail_launch"
        sleep(10)
        self.dut_session_id=self.hs_api_call.start_session_capture()
        sleep(10)
        self.session_id=self.hs_api_call.start_session_capture(device_address=self.cd_address)
        self.kpi_labels[kpi_names.LAUNCH_TIME]['start'] = int(round(time.time() * 1000)) + 1000
        self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5500
        self.driver.launch_app() 
        profile = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("vinoth")')
        #self.driver.find_element(MBy.ACCESSIBILITY_ID, 'Play Now')
        self.kpi_labels[kpi_names.LAUNCH_TIME]['end'] = int(round(time.time() * 1000))
        self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['video_box'] = [[30, 290, 350, 495]]
        self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['end'] =  int(round(time.time() * 1000)) - 900
        profile.click()
        sleep(5)
        logger.info("App launched")
        self.pass_count += 2

        self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['start_sensitivity'] = 0.999
        self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['end_sensitivity'] = 0.999
        self.kpi_labels[kpi_names.LAUNCH_TIME]['segment_start'] = 0
        self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['segment_start'] = 0
    def download_tab(self):
        self.status = "Fail_download"
        sleep(2)
        download = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Downloads")')
        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['video_box'] = [0, 50, 500, 100]
        self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5000
        download.click()
        self.driver.find_element(MBy.ID, "com.netflix.mediaclient:id/2131427585")
        #self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['video_box'] = [[0, 0, 504, 200]]
        self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['end'] = int(round(time.time() * 1000)) + 100
        logger.info("Downloaded videos found")

        try:
            downloads = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Mismatched")')
            downloads.click()
            sleep(1)
            dot = self.driver.find_element(MBy.ACCESSIBILITY_ID, 'Select Items to Remove')
            dot.click()
            delete = self.driver.find_element(MBy.ID, 'com.netflix.mediaclient:id/2131427623')
            delete.click()
            sleep(1)
            confirm = self.driver.find_element(MBy.ACCESSIBILITY_ID, 'Remove Downloads')
            confirm.click()
            sleep(2)
            logger.info("Delete sucessfull")
        except:
            pass

        self.pass_count += 1
        sleep(2)

        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['segment_start'] = 0
        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['segment_start'] = -1

        #self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['start_sensitivity'] = 0.999
        #self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['end_sensitivity'] = 0.98
        
    def search(self):
        self.status = "Fail_search" 
        search_btn=self.driver.find_element(MBy.ACCESSIBILITY_ID, "Search" )
        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5000
        search_btn.click()
        search_bar = self.driver.find_element(MBy.ID, "android:id/search_src_text")
        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['end'] = int(round(time.time() * 1000)) + 2000
        sleep(2)
        self.kpi_labels[kpi_names.SEARCH_TIME]['start'] = int(round(time.time() * 1000)) + 7000
       # search_bar.click()
        search_bar.send_keys("Mismatched")
        self.driver.find_element(MBy.ACCESSIBILITY_ID, "Mismatched")
        self.kpi_labels[kpi_names.SEARCH_TIME]['end'] = int(round(time.time() * 1000)) + 1500
        logger.info("Search element found")
        time.sleep(2)
        self.pass_count += 2

        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['start_sensitivity'] = 0.999
        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['end_sensitivity'] = 0.90

        self.kpi_labels[kpi_names.SEARCH_TIME]['start_sensitivity'] = 0.93
        self.kpi_labels[kpi_names.SEARCH_TIME]['end_sensitivity'] = 0.97


    def video(self):
        self.status = "Fail_video_load" 
       # watch = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Watch Now")')
        movie_image  = self.driver.find_element(MBy.ACCESSIBILITY_ID, "Mismatched")
        self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 4500
        movie_image.click()
        #sleep(2)
        self.driver.find_element(MBy.ACCESSIBILITY_ID, "Show controls")
        self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME]['end'] = int(round(time.time() * 1000)) #+ 500
        self.pass_count += 1
        sleep(2)
        try:
            watch = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Resume")')
        except:
            watch = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Play")')
        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5000
        watch.click()
        self.driver.find_element(MBy.ACCESSIBILITY_ID, "Show player controls")
        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['end'] = int(round(time.time() * 1000)) + 2500
        logger.info("video started playing")
        sleep(30)
        self.pass_count += 1

        self.driver.back()
        sleep(5)

        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['start_sensitivity'] = 0.98
        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['end_sensitivity'] = 0.80
        self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME]['end_sensitivity'] = 0.78

    def downloads(self):
        self.status = "Fail_download"
        self.screen_size_swipe()
        sleep(2)
        start = self.driver.find_elements(MBy.XPATH, '//*[@content-desc="Download"]')
        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['start'] = int(round(time.time() * 1000)) + 4900
        start[0].click()
        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['video_box'] = [0, 50, 500, 100]
        sleep(25)
        #self.kpi_labels[kpi_names.DOWNLOAD_TIME]['video_box'] = [[270,500, 360, 700]]
        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['end'] = int(round(time.time() * 1000)) - 3000
        logger.info("download sucessfull")
        self.pass_count += 1
        sleep(10)

        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['start_sensitivity'] = 0.999
        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['end_sensitivity'] = 0.999


    def screen_size_swipe(self):
        screen_size = self.driver.get_window_size()
        self.width = screen_size['width']
        self.height = screen_size['height']
        self.start_x = self.width/2
        self.start_y = self.height * 0.63
        self.end_x = self.width/2
        self.end_y = self.height * 0.2
        self.driver.swipe(self.start_x, self.start_y, self.end_x, self.end_y, 300)

    def get_screen_size(self):
        screen_size = self.driver.get_window_size()
        self.width = screen_size['width']
        self.height = screen_size['height']
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BupaAndroidTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
