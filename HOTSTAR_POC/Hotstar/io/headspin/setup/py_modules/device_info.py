# -*- coding: utf-8 -*-
#!/usr/bin/python
from __future__ import absolute_import
from __future__ import print_function
from hs_api import hsApi
from time import sleep
from os.path import exists
import os
import subprocess
import codecs
import sys
import sh
import json
from appium.webdriver.common.mobileby import MobileBy as MBy
#Needed as the app name is non-ASIC value
if sys.version_info[0] >= 3:
	from importlib import reload
reload(sys)  # Reload does the trick!
if sys.version_info[0] < 3:
	sys.setdefaultencoding('UTF8')
if sys.version_info[0] < 3:
    UTF8Writer = codecs.getwriter('utf8')
    sys.stdout = UTF8Writer(sys.stdout)

class deviceInfo:
    debug = False

    def __init__(self, UDID, access_token):
        self.hs_api_call = hsApi(UDID, access_token)
        self.UDID = UDID
        self.ACCESS_TOKEN = access_token

    def get_hostname(self):
        return self.hs_api_call.device_details['hostname']

    def get_os_version(self):
        return self.hs_api_call.device_details['os_version']

    def get_owner(self):
        return self.hs_api_call.device_details['device']['owner']

    def get_device_model(self, udid):
        try:
            return self.hs_api_call.device_details['device_skus'][0]
        except:
            adb_comm = sh.Command('adb')
            return adb_comm('-s', udid, 'shell', 'getprop', 'ro.product.model').strip()

    def get_network_name(self):
        network_name = self.hs_api_call.device_details['operator']
        return network_name

    def get_app_size_info(self, driver, app_name):
        # Only works in Samsung and Pixel devices

        self.hs_api_call.run_adb_command(
            "monkey -p com.android.settings -c android.intent.category.LAUNCHER 1")

        if driver.orientation == "LANDSCAPE":
            driver.orientation = "PORTRAIT"

        sleep(2)
        screen_size = driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        start_x = width/2
        start_y = height/1.5
        end_x = width/2
        end_y = height/4

        driver.implicitly_wait(2)
        for i in range(0, 50):
            try:
                apps_button = driver.find_element_by_android_uiautomator(
                    'new UiSelector().textContains("Apps")')
                break
            except:
                driver.swipe(start_x, start_y, end_x, end_y)
                sleep(2)
        apps_button.click()

        try:
            search = driver.find_element_by_android_uiautomator(
                'new UiSelector().descriptionContains("Search")')
            search.click()
            tf = driver.find_element_by_class_name('android.widget.EditText')
            tf.set_value(app_name)
            sleep(3)
            app_name_selection = driver.find_element_by_id('android:id/title')
            app_name_selection.click()

        except Exception as e:
            print(e)
            for i in range(0, 50):
                try:
                    if self.debug:
                        page_source = driver.page_source
                        print(('get app button page_source trial: ' + str(i)))
                        print(page_source)
                    app_name_sel = driver.find_element_by_android_uiautomator(
                        'new UiSelector().textContains("%s")' % app_name)
                    app_name_sel.click()
                    break
                except:
                    driver.swipe(start_x, start_y, end_x, end_y)
                    sleep(2)

        driver.implicitly_wait(30)

        storage = driver.find_element_by_android_uiautomator(
            'new UiSelector().textContains("Storage")')
        storage.click()
        summary_size_list = driver.find_elements_by_id("android:id/summary")
        app_size_info = {}
        app_size_info['app_size'] = summary_size_list[0].text
        app_size_info['user_data'] = summary_size_list[1].text
        app_size_info['cache'] = summary_size_list[2].text
        app_size_info['total'] = summary_size_list[3].text
        return app_size_info


    def get_app_info_page(self, driver, app_name):
        ## Only works in Samsung and Pixel devices

        self.hs_api_call.run_adb_command("monkey -p com.android.settings -c android.intent.category.LAUNCHER 1")

        if driver.orientation == "LANDSCAPE":
            driver.orientation = "PORTRAIT"
            
        sleep (2)
        screen_size = driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        start_x = width/2
        start_y = height/1.5
        end_x = width/2
        end_y = height/4

        driver.implicitly_wait(2)
        for i in range(0, 50):
            try:
                apps_button = driver.find_element(MBy.XPATH,'//android.widget.TextView[@resource-id="android:id/title" and @text="Apps"]')
                break
            except:
                driver.swipe(start_x, start_y, end_x, end_y)
                sleep(2)
        apps_button.click()

        try:
            search = driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'descriptionContains("Search")')
            search.click()
            tf = driver.find_element(MBy.ID, 'com.android.settings:id/search_src_text')
            tf.send_keys(app_name)
            sleep(3)
            app_name_selection = driver.find_element(MBy.ID, 'android:id/title')
            app_name_selection.click()

        except Exception as e:
            print(e)
            for i in range(0, 50):
                try:
                    if self.debug:
                        page_source = driver.page_source
                        print('get app button page_source trial: ' + str(i))
                        print(page_source)
                    app_name_sel = driver.find_element_by_android_uiautomator('new UiSelector().resourceId("android:id/title").textContains("%s")'% app_name)
                    app_name_sel.click()
                    break
                except:
                    driver.swipe(start_x, start_y, end_x, end_y)
                    sleep(2)

        driver.implicitly_wait(30)
    

    def clear_app_cache(self, driver, app_name):
        self.get_app_info_page(driver, app_name)
        screen_size = driver.get_window_size()
        width = screen_size['width']
        height = screen_size['height']
        start_x = width/2
        start_y = height/1.5
        end_x = width/2
        end_y = height/4
        for i in range(0, 50):
            try :
                storage = driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'textContains("Storage")')
                break
            except:
                driver.swipe(start_x, start_y, end_x, end_y)
                sleep(2)
        storage.click()
        driver.implicitly_wait(2)
        try:
            clear_cache = driver.find_element(MBy.ID, 'com.android.settings:id/button2_negative')
        except:
            clear_cache = driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'textContains("Clear cache")')
        clear_cache.click()
        #driver.press_keycode(4)
        if app_name=="mirrativ":
            driver.press_keycode(4)
            print ("mirrativ")
            screen_size = driver.get_window_size()
            width = screen_size['width']
            height = screen_size['height']
            start_x = width/2
            start_y = height/1.5
            end_x = width/2
            end_y = height/4

            driver.implicitly_wait(2)
            for i in range(0, 50):
                try:
                    appear_button = driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'textContains("Appear")')
                    appear_button.click()
                    break
                except:
                    driver.swipe(start_x, start_y, end_x, end_y)
                    sleep(2)
            allow_button = driver.find_element(MBy.ANDROID_UIAUTOMATOR, 'textContains("Allow permission")')
            allow_button.click()
            driver.implicitly_wait(20)
            sleep(3)

    def get_package_list(self):
        package_list = self.hs_api_call.run_adb_command("pm list package")
        return package_list

    def get_app_version(self, app_package):
        app_version = None
        if self.hs_api_call.device_os == "android":
            if app_package =="com.linkedin.android":
                version_details = self.hs_api_call.run_adb_command("dumpsys package {}| grep versionName".format(app_package))
                try:
                    version_details = str(version_details, 'UTF-8')
                except TypeError as e:
                    version_details = str(version_details)

                try:
                    app_version = version_details.split('=')[1].split('\'')[0].strip()
                except:
                    app_version = version_details.split('=')[1].strip()
            else:
                version_details = self.hs_api_call.run_adb_command("dumpsys package {}| grep versionName".format(app_package))
                version_details = str(version_details)
                app_version = version_details.split('=')[1].strip()
                if "\n" in app_version:
                    app_version = app_version.split("\n")[0]
        elif self.hs_api_call.device_os == "ios":
            apps = self.hs_api_call.get_app_list_ios()
            for app in apps['data']:
                if app['CFBundleIdentifier'] == app_package:
                    # app_version = app['CFBundleVersion']
                    app_version = app['CFBundleShortVersionString']
                    break
        return app_version.replace("'", "")

    # See if connection is on WIFI or MOBILE
    def get_connection_type(self,os,network_type):
        if os.lower()=="android":
            connection = self.hs_api_call.device_details['network_type']
        elif os.lower()=='ios':
            connection = network_type.upper()
        print(("Connected to %s" % connection))
        return connection