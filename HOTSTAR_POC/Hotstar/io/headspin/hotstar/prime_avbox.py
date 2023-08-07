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
    app_name = "Amazon prime"
    package = "com.amazon.avod.thirdpartyclient"
    activity = "com.amazon.avod.client.activity.HomeScreenActivity" 
    #test_name = "test session"
    test_name = "Amazon Prime Android"
    session_type = "page load time"
    implicitly_wait_time = 20
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


    def test_prime(self):
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
        self.kpi_labels[kpi_names.LAUNCH_TIME]['start'] = int(round(time.time() * 1000)) 
        self.driver.launch_app()
        try:
            close = self.short_wait(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Close")') 
            close.click()
        except:pass
        try:
            self.driver.find_element(MBy.XPATH, '//*[@resource-id="com.amazon.avod.thirdpartyclient:id/card_cover_art_state"]')
            self.kpi_labels[kpi_names.LAUNCH_TIME]['end'] = int(round(time.time() * 1000))
        except:
            profile = self.driver.find_element(MBy.ACCESSIBILITY_ID, "hsindia")
            self.kpi_labels[kpi_names.LAUNCH_TIME]['end'] = int(round(time.time() * 1000))
            profile.click()
        sleep(4)
        logger.info("App launched")
        self.pass_count += 2
        # self.kpi_labels[kpi_names.LAUNCH_TIME]['start_sensitivity'] = 0.65
        # self.kpi_labels[kpi_names.LAUNCH_TIME]['end_sensitivity'] = 0.86
        # self.kpi_labels[kpi_names.LAUNCH_TIME]['segment_start'] = 0
        # self.kpi_labels[kpi_names.LAUNCH_TIME]['segment_end'] = -1
        # self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['segment_start'] = 0
        # self.kpi_labels[kpi_names.LOGO_LOAD_TIME]['segment_end'] = 2

    def download_tab(self):
        self.status = "Fail_download"
        download = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Downloads")')
        self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5300
        download.click()
        self.driver.find_element(MBy.ID, "com.amazon.avod.thirdpartyclient:id/card_cover_art")
        self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['end'] = int(round(time.time() * 1000)) - 200
        logger.info("Downloaded videos found")
        try:
            downloads = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("The Family Man")')
            downloads.click()
            dot = self.driver.find_element(MBy.XPATH, '//*[@resource-id="com.amazon.avod.thirdpartyclient:id/title_card_action_button"]')
            dot.click()
            delete = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Delete download")')
            delete.click()
            sleep(2)
        except:pass   
        self.pass_count += 1
        sleep(2)

        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['segment_start'] = 0
        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['segment_start'] = -1

        self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['start_sensitivity'] = 0.99
        #self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['end_sensitivity'] = 0.999
        
    def search(self):
        self.status = "Fail_search" 
        search_btn=self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Find")' )
        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5400
        search_btn.click()
        search_bar = self.driver.find_element(MBy.ACCESSIBILITY_ID, 'Search Video Store. Search by actor, title..')
        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['end'] = int(round(time.time() * 1000)) #+ 5000
        sleep(2)
        search_bar.click()
        self.kpi_labels[kpi_names.SEARCH_TIME]['start'] = int(round(time.time() * 1000)) + 6000
        search_bar.send_keys("The Family Man")
        self.driver.press_keycode(66)
        self.driver.find_element(MBy.ID, 'com.amazon.avod.thirdpartyclient:id/card_cover_art')
        self.kpi_labels[kpi_names.SEARCH_TIME]['end'] = int(round(time.time() * 1000))
        logger.info("Search element found")
        time.sleep(2)
        self.pass_count += 2
        
        self.kpi_labels[kpi_names.SEARCH_TAB_LOAD_TIME]['start_sensitivity'] = 0.999
        self.kpi_labels[kpi_names.SEARCH_TIME]['start_sensitivity'] = 0.999

    def video(self):
        self.status = "Fail_video_load" 
        movie_image  = self.driver.find_element(MBy.ID, 'com.amazon.avod.thirdpartyclient:id/card_cover_art')
        self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 5000
        movie_image.click()
        self.driver.find_element(MBy.ID, 'com.amazon.avod.thirdpartyclient:id/header_image')
        self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME]['end'] = int(round(time.time() * 1000)) - 200
        sleep(2)
        start_over = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Start over")')
        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['start'] = int(round(time.time() * 1000)) + 4500
        start_over.click()
        #sleep(5)
        self.driver.find_element(MBy.ID, 'android:id/content')
        #self.driver.find_element(MBy.ID, 'com.amazon.avod.thirdpartyclient:id/ContentView')
        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['end'] = int(round(time.time() * 1000)) + 2000
        logger.info("video started playing")
        self.pass_count += 2
        sleep(30)
        #logger.info("Logout")
        self.driver.back()
        sleep(10)

        self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME]['start_sensitivity'] = 0.99

        self.kpi_labels[kpi_names.VIDEO_LOAD_TIME]['end_sensitivity'] = 0.99

    def downloads(self):
        self.status = "Fail_download"
        self.screen_size_swipe()
        sleep(2)
        start = self.driver.find_elements(MBy.XPATH, '//*[@resource-id="com.amazon.avod.thirdpartyclient:id/episode_download_button"]')
        start[0].click()
        sleep(1)
        download = self.driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Start download")')
        # self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME]['video_box'] = [0, 50, 500, 100]
        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['start'] = int(round(time.time() * 1000)) + 4900
        download.click()
        sleep(30)
        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['video_box'] = [[380,660,618,807]] #[[180,300, 340, 450]]
        self.kpi_labels[kpi_names.DOWNLOAD_TIME]['end'] = int(round(time.time() * 1000)) - 2000
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
        self.start_y = self.height * 0.68
        self.end_x = self.width/2
        self.end_y = self.height * 0.3
        self.driver.swipe(self.start_x, self.start_y, self.end_x, self.end_y, 300)

    def get_screen_size(self):
        screen_size = self.driver.get_window_size()
        self.width = screen_size['width']
        self.height = screen_size['height']
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BupaAndroidTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
