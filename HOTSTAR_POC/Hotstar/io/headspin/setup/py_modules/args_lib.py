from __future__ import absolute_import
from __future__ import print_function
import os
import time
from device_info import deviceInfo
from hs_api import hsApi


def get_args(script_location):
    print('get_args')
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--udid', '--udid', dest='udid',
                        type=str, nargs='?',
                        default=None,
                        required=True,
                        help="udid")
    parser.add_argument('--appium_input', '--appium_input', dest='appium_input',
                        type=str, nargs='?',
                        default=None,
                        required=True,
                        help="appium_input")
    parser.add_argument('--uiautomator1', '--uiautomator1',
                        dest='uiautomator1',
                        action='store_true',
                        default=None,
                        required=False,
                        help="uiautomator1")
    parser.add_argument('--network_type', '--network_type', dest='network_type',
                        type=str, nargs='?',
                        default="WIFI",
                        required=True,
                        help="network_type")
    parser.add_argument('--os', '--os', dest='os',
                        type=str, nargs='?',
                        default=None,
                        required=True,
                        help="os")
    

    args = parser.parse_args()
    if not args.udid or not args.appium_input:
        parser.print_help()
        example_args = [' ']
        example_args.append('--udid=<udid>')
        example_args.append(
            '--appium_input=https://<host:port>/v0/<api_token>/wd/hub')
        example_args.append('--os=<android/ios>')
        example_args.append('--network_type=<WIFI/MOBILE>')
        print(('Example Args: python ' +
              os.path.basename(script_location) + ' '.join(example_args)))
        raise Exception('Invalid Args')
    else:
        return args, parser


def init_args(args, self):
    self.is_game_test = False
    self.verify_kpi_with_log = False
    self.valid_start = False
    self.udid = args.udid
    self.appium_input = args.appium_input
    # if the uiautomator1 needs to be used
    self.uiautomator1 = args.uiautomator1
    self.url = self.appium_input
    self.network_type = args.network_type
    self.os = args.os
    self.access_token = self.url.split('/')[4]
    if 'localhost' in self.url or '0.0.0.0' in self.url or not self.private_key_file:
        self.running_on_pbox = True
    self.valid_start = True

    # For cases where driver is not used to launch app
    self.relaunch_start = None
    


def init_caps(self, video_only=False, auto_launch=True):
    # desired caps for the app
    self.desired_caps = {}
    self.desired_caps['platformName'] = self.os
    self.desired_caps['udid'] = self.udid
    self.desired_caps['deviceName'] = self.udid

    # Android specific caps
    #self.os = "Android"
    if self.os.lower() == "android":
        self.desired_caps['appPackage'] = self.package
        self.desired_caps['appActivity'] = self.activity
        self.desired_caps['disableWindowAnimation'] = True
        self.desired_caps['unlockType'] = "pin"
        self.desired_caps['unlockKey'] = "1234"
        self.desired_caps['newCommandTimeout'] = 50000
        if self.uiautomator1:
            self.desired_caps['automationName'] = "UiAutomator1"
        else:
            self.desired_caps['automationName'] = "UiAutomator2"
        self.desired_caps['autoGrantPermissions'] = True
        # self.desired_caps['uiautomator2ServerInstallTimeout'] = 50000
        # self.desired_caps['skipServerInstallation'] = True
        if not auto_launch:
            self.desired_caps['autoLaunch'] = False

    # iOS spedific caps
    elif self.os.lower() == "ios":
        self.desired_caps['automationName'] = "XCUITest"
        self.desired_caps['bundleId'] = self.bundle_id
        self.desired_caps['autoAcceptAlerts'] = True
        self.desired_caps['newCommandTimeout'] = 50000

    if self.no_reset:
        self.desired_caps['noReset'] = self.no_reset
    else:
        self.desired_caps['noReset'] = False

    # Headspin caps
    self.desired_caps['headspin:controlLock'] = True
    if self.use_capture:
        if video_only:
            self.desired_caps['headspin:capture.video'] = True
            self.desired_caps['headspin:capture.network'] = False
        else:
            self.desired_caps['headspin:capture.video'] = True
            self.desired_caps['headspin:capture.network'] = True
    return self



def device_state_var(self):

    self.device_info = deviceInfo(self.udid, self.access_token)
    self.hostname = self.device_info.get_hostname()
    self.connection_status = self.device_info.get_connection_type(self.os,self.network_type)

    self.hs_api_call = hsApi(self.udid, self.access_token)
    self.network_name = ""
    self.network_name = self.device_info.get_network_name()

    if not self.connection_status:
        self.connection_status = "None"

    if self.os.lower() == "android":
        if self.network_type not in self.connection_status:
            if 'WIFI' in self.network_type:
                self.hs_api_call.run_adb_command("svc wifi enable")
                print("Changing to WIFI")
                self.connection_status = "WIFI"
            else:
                self.hs_api_call.run_adb_command("svc wifi disable")
                print("Changing to MOBILE")
                self.connection_status = "MOBILE"
            time.sleep(3)

    if self.os.lower() == "android":
        try:
            self.apk_version = self.device_info.get_app_version(self.package)
            print(("App Version: ", self.apk_version))
        except Exception as error:
            print(error)
            self.apk_version = None
            print('Get apk_version Failed')

    elif self.os.lower() == "ios":
        try:
            self.apk_version = self.device_info.get_app_version(self.bundle_id)
            print(("App Version: ", self.apk_version))
        except Exception as error:
            print(error)
            self.apk_version = None
            print('Get apk_version Failed')