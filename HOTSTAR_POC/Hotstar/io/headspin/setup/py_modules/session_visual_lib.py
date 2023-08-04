# -*- coding: utf-8 -*-
import json
import kpi_names
from hs_api import hsApi
import time
from hs_logger import logger


def run_record_session_info(self, non_time_kpis= None):
	'''
	Save KPI and Description to session
	'''
	self.non_time_kpis= non_time_kpis
	
	logger.info('run_record_session_info')
	run_add_annotation_data(self)
	# run_add_session_data(self)
	logger.info("https://ui-dev.headspin.io/sessions/" +
				str(self.session_id)+"/waterfall")


def run_add_session_data(self):
	'''
	Save KPI Label info to description 
	'''
	logger.info("run add session data")

	session_data = get_general_session_data(self)
	# adding data_kpi to session data
	if self.data_kpi:
		session_data = get_data_kpi(self, session_data)
		logger.debug("error")
	

	if not self.debug:
		result = self.hs_api_call.add_session_data(session_data)
		logger.info('result')
		logger.info(result)
	description_string = ""
	for data in session_data['data']:
		description_string += data['key'] + " : " + str(data['value']) + "\n"

	print("Adding Tag")
	if self.dut_session_id :
		print("Dut session ID",self.dut_session_id)
		self.hs_api_call.add_session_tags(self.session_id,bundle_id=self.package,app_name=self.app_name,app_version=self.apk_version,status=self.status,os=self.os,session_type=self.session_type,dut_session_id=self.dut_session_id,device_model= self.device_model)#file_size=self.file_size)
		print("Dut session ID",self.dut_session_id)
	else:
		print("session ID",self.session_id)
		self.hs_api_call.add_session_tags(self.session_id,bundle_id=self.package,app_name=self.app_name,app_version=self.apk_version,status=self.status,os=self.os,session_type=self.session_type)#file_size=self.file_size)
	
	#self.hs_api_call.add_session_tags(self.session_id,bundle_id=self.package,app_name=self.app_name,app_version=self.apk_version,status=self.status,os=self.os,session_type=self.session_type)#File_size=self.text)

	self.hs_api_call.update_session_name_and_description(
		self.session_id, self.test_name, description_string)


def get_general_session_data(self):
	'''
	General Session Data, include phone os, phone version ....
	'''
	session_status = None
	if self.status != "Pass":
		session_status = "Failed"
	else:
		session_status = "Passed"
	try:
		if self.state=="excluded":
			session_status='Excluded' 
	except:
		pass
	

	session_data = {}
	session_data['session_id'] = self.session_id
	session_data['test_name'] = self.test_name
	session_data['status'] = session_status
	session_data['data'] = []
	# app info
	session_data['data'].append(
		{"key": kpi_names.BUNDLE_ID, "value": self.package})
	session_data['data'].append({"key": 'status', "value": self.status})
				
	session_data = add_kpi_data_from_labels(self, session_data)

	
	try:
		if self.genre_id:
			session_data['data'].append(
				{"key": kpi_names.GENRE_ID, "value": self.genre_id})
	except:
		pass
	try:
		session_data['data'].append(
			{"key": kpi_names.FAIL_REASON, "value": self.status})
	except:
		pass

	try:
		session_data['data'].append(
			{"key": kpi_names.PASS_COUNT, "value": self.pass_count})
	except:
		pass
	try:
		session_data['data'].append(
			{"key": kpi_names.FAIL_COUNT, "value": self.fail_count})
	except:
		pass
	try:
		session_data['data'].append(
			{"key": kpi_names.CONNECTION_STATUS, "value": self.connection_status})
	except:
		pass
	try:
		session_data['data'].append(
			{"key": kpi_names.OS, "value": self.os})
	except:
		pass

	try:
		session_data['data'].append(
			{"key": kpi_names.APP, "value": self.app_name})
	except:
		pass

	try:
		session_data['data'].append(
			{"key": kpi_names.APP, "value": self.app_name})
	except:
		pass

	try:
		session_data['data'].append(
			{"key": "speed_value", "value": str(self.speed_value)})
	except:
		pass
	
	try:
		if self.app_size_info:
			session_data['data'].append(
				{"key": kpi_names.APP_SIZE_ON_DISK, "value": self.app_size_info['app_size']})
			session_data['data'].append(
				{"key": kpi_names.USER_DATA_ON_DISK, "value": self.app_size_info['user_data']})
			session_data['data'].append(
				{"key": kpi_names.CACHE_ON_DISK, "value": self.app_size_info['cache']})
			session_data['data'].append(
				{"key": kpi_names.TOTAL_ON_DISK, "value": self.app_size_info['total']})
	except:

		pass

	# Incase of cold launch and first launch
	try:
		if self.app_size_info_pre_launch:
			session_data['data'].append(
				{"key": kpi_names.APP_SIZE_PRE_LAUNCH, "value": self.app_size_info_pre_launch['app_size']})
			session_data['data'].append(
				{"key": kpi_names.USER_DATA_PRE_LAUNCH, "value": self.app_size_info_pre_launch['user_data']})
			session_data['data'].append(
				{"key": kpi_names.CACHE_PRE_LAUNCH, "value": self.app_size_info_pre_launch['cache']})
			session_data['data'].append(
				{"key": kpi_names.TOTAL_PRE_LAUNCH, "value": self.app_size_info_pre_launch['total']})
	except:
		pass

	try:
		if self.app_size_info_post_launch:
			session_data['data'].append(
				{"key": kpi_names.APP_SIZE_POST_LAUNCH, "value": self.app_size_info_post_launch['app_size']})
			session_data['data'].append(
				{"key": kpi_names.USER_DATA_POST_LAUNCH, "value": self.app_size_info_post_launch['user_data']})
			session_data['data'].append(
				{"key": kpi_names.CACHE_POST_LAUNCH, "value": self.app_size_info_post_launch['cache']})
			session_data['data'].append(
				{"key": kpi_names.TOTAL_POST_LAUNCH, "value": self.app_size_info_post_launch['total']})
	except:
		pass

	try:
		if self.apk_version:
			session_data['data'].append(
				{"key": kpi_names.APP_VERSIONS, "value": self.apk_version})
	except:
		pass

	try:
		if self.code_version:
			session_data['data'].append(
				{"key": kpi_names.CODE_VERSION, "value": self.code_version})
	except:
		pass

	try:
		if self.clear_cache:
			session_data['data'].append({"key": "clear_cache", "value": True})
	except:
		pass

	try:
		if self.debug:
			logger.info('session_data')
			logger.info(json.dumps(session_data, indent=2))
	except:
		pass
	return session_data


def get_video_start_timestamp(self):
	logger.info('get_video_start_timestamp')
	wait_until_capture_complete = True
	t_end = time.time()+600
	if wait_until_capture_complete:
		while time.time() < t_end:
			capture_timestamp = self.hs_api_call.get_capture_timestamp(
				self.session_id)
			logger.info(capture_timestamp)
			self.video_start_timestamp = capture_timestamp['capture-started'] * 1000
			if 'capture-complete' in capture_timestamp:
				break
			time.sleep(1)
	else:
		capture_timestamp = self.hs_api_call.get_capture_timestamp(
			self.session_id)
		self.video_start_timestamp = capture_timestamp['capture-started'] * 1000




def run_add_annotation_data(self):
	'''
	Add annotation from kpi_labels
	'''
	logger.info("run add annotation to session")
	get_video_start_timestamp(self)
	add_kpi_labels(self, self.kpi_labels, self.KPI_LABEL_CATEGORY)


def add_kpi_data_from_labels(self, session_data):
	'''
	Merge kpi labels and interval time
	'''
	for label_key in self.kpi_labels.keys():
		if self.kpi_labels[label_key] and 'start' in self.kpi_labels[label_key] and 'end' in self.kpi_labels[label_key]:
			data = {}
			data['key'] = label_key
			start_time = self.kpi_labels[label_key]['start']
			end_time = self.kpi_labels[label_key]['end']
			if start_time and end_time:
				data['value'] = end_time - start_time
				session_data['data'].append(data)
	return session_data


def get_screenchange_list_divide(self, label_key, label_start_time, label_end_time,
								 start_sensitivity=None, end_sensitivity=None,page_transition_sensitivity=None,video_box=None):
	"""
		Given a visual page load of the region
		If there are start and end, there is only 1 region in the middle that might have more screen changes.
		If start and end are the same we are done
	"""
	screen_change_list = []
	sn = 0
	sn_limit = 10
	segment_time_step = 100
	try:
		segment_time_step = self.segment_time_step
	except AttributeError:
		pass
	pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), label_start_time, label_end_time,
												 start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity,page_transition_sensitivity=page_transition_sensitivity,video_box=video_box)
	logger.debug(pageload)
	if 'page_load_regions' in list(pageload.keys()) and 'message' not in pageload['page_load_regions']:
		while True:
			screen_change_list.append(
				pageload['page_load_regions'][0]['start_time'])
			screen_change_list.append(
				pageload['page_load_regions'][0]['end_time'])
			sn += 1
			if sn_limit < sn:
				break
			new_label_start_time = float(
				pageload['page_load_regions'][0]['start_time']) + segment_time_step
			new_label_end_time = float(
				pageload['page_load_regions'][0]['end_time']) - segment_time_step
			if new_label_start_time > new_label_end_time:
				break
			logger.debug('new_label_start_time:' + str(new_label_start_time))
			logger.debug('new_label_end_time:' + str(new_label_end_time))
			pageload = self.hs_api_call.get_pageloadtime(self.session_id, str(label_key) + str(sn), new_label_start_time, new_label_end_time,
														 start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity,page_transition_sensitivity=page_transition_sensitivity,video_box=video_box)
			if 'page_load_regions' not in list(pageload.keys()) or 'error_msg' in pageload['page_load_regions'][0]:
				logger.debug(pageload)
				if 'status' in pageload:
					# Prevent bad data to get into the database
					self.status = 'Page Load Error'
				break
	else:
		# Prevent bad data to get into the database
		self.status = 'Page Load Error'
		logger.debug(pageload)

	screen_change_list = sorted(list(set(screen_change_list)))
	logger.info(label_key + str(screen_change_list))
	logger.debug((label_key + ' ' + str(screen_change_list)))
	return screen_change_list


def add_kpi_labels(self, labels, label_category):
	'''
		Find all the screen change using different increments
		From the screen changes, pick the desired region
		1. Make sure we can produce the regions that we want to work with 100%
		2. Pick the regions in the code to be inserted for labels kpi

		If there is segment_start and segment_end, find all the candidate regions, and use segment_start and segment_end to pick
		segment_start 
		segment_end 
		0 => Pick the first segment from the start
		1 => Pick the second segment from the start
		-1 => Pick the last segment from the end
		-2 => Pick the second to last segment from the end
	'''
	logger.info("add_kpi_labels")
	logger.debug(labels)
	for label_key in labels.keys():
		label = labels[label_key]
		logger.debug(label)
		if label['start'] and label['end']:
			label_start_time = label['start'] - \
				self.video_start_timestamp - self.delta_time * 1000
			if(label_start_time < 0):
				label_start_time = 0.0
			label_end_time = label['end'] - self.video_start_timestamp

			if label_key == kpi_names.DOWNLOAD_TIME:
				label_end_time += self.delta_time * 1000
			logger.info("Add Desired Region " + str(label_key) +
						" "+str(label_start_time)+" "+str(label_end_time))
			self.hs_api_call.add_label(
				self.session_id, label_key, 'desired region', (label_start_time)/1000, (label_end_time)/1000)

			start_sensitivity = None
			end_sensitivity = None
			page_transition_sensitivity = None
			video_box = None
			if 'start_sensitivity' in label:
				start_sensitivity = label['start_sensitivity']
			if 'end_sensitivity' in label:
				end_sensitivity = label['end_sensitivity']
			if 'page_transition_sensitivity' in label:
				page_transition_sensitivity = label['page_transition_sensitivity']
			if 'video_box' in label:
				video_box = label['video_box']

			new_label_start_time = None
			new_label_end_time = None

			if 'segment_start' in labels[label_key] and 'segment_end' in labels[label_key]:
				# Get candidate screen change list, example [2960, 4360, 8040, 9480, 9960, 11560, 13560, 13800, 17720, 18040]
				screen_change_list = get_screenchange_list_divide(
					self, label_key, label_start_time, label_end_time, start_sensitivity, end_sensitivity,page_transition_sensitivity,video_box)
				try:
					if screen_change_list:
						new_label_start_time = float(
							screen_change_list[labels[label_key]['segment_start']])
						new_label_end_time = float(
							screen_change_list[labels[label_key]['segment_end']])
				except:
					self.status = 'Page Load Segement Error'
			else:
				if label['start'] and label['end']:
					pageload = self.hs_api_call.get_pageloadtime(
						self.session_id, label_key, label_start_time, label_end_time, start_sensitivity=start_sensitivity, end_sensitivity=end_sensitivity,page_transition_sensitivity=page_transition_sensitivity, video_box=video_box)
					if 'page_load_regions' in list(pageload.keys()) and 'error_msg' not in pageload['page_load_regions'][0]:
						new_label_start_time = float(
							pageload['page_load_regions'][0]['start_time'])
						new_label_end_time = float(
							pageload['page_load_regions'][0]['end_time'])
					elif 'Please check for results later' in str(pageload):
						#this runs if pageload returns the error "The page load analysis will run once the session video becomes available. Please check for results later".
						while True:
							try:
								
								pageload = self.hs_api_call.return_page_load_existing(self.session_id)
								if 'page_load_regions' in list(pageload.keys()):
									if label_key in str(pageload):
										for i in range(0,(len(pageload['page_load_regions']))):
											if (pageload['page_load_regions'][i]['request_name']) == label_key:
												new_label_start_time = float(
												pageload['page_load_regions'][i]['start_time'])
												new_label_end_time = float(
												pageload['page_load_regions'][i]['end_time'])
												break
											
										break
									

							except:
								pass
					else :
						self.status='Page Load Analysis Fail'

			if new_label_start_time and new_label_end_time:
				self.kpi_labels[label_key]['start'] = new_label_start_time
				self.kpi_labels[label_key]['end'] = new_label_end_time

				# validate kpi = 0
				kpi_value = self.kpi_labels[label_key]['end'] - \
					self.kpi_labels[label_key]['start']
				if int(kpi_value) == 0:
					self.kpi_labels[label_key]['start'] = self.kpi_labels[label_key]['start'] - 50
					self.kpi_labels[label_key]['end'] = self.kpi_labels[label_key]['end'] + 50

				self.hs_api_call.add_label(self.session_id, label_key, label_category, (
					new_label_start_time)/1000, (new_label_end_time)/1000)
		else:
			logger.debug('Label not found for:' +
						 str(label_key) + ' ' + label_category)


# adding data kpi's to session data

def get_data_kpi(self, session_data):
	logger.debug("Adding data kpi")
	for key, value in self.data_kpis.items():
		if value:
			session_data['data'].append({"key": key, "value": value})
	return session_data
