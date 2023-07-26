import kpi_names
#import label_categories

def init_timing(self):

	# initialising variables
	self.status = "Fail_launch"
	self.pass_count = 0
	self.fail_count = 0
	self.ADD_KPI_ANNOTATION = True
	self.app_size_info= None
	self.delta_time = 5
	self.connection_status= ""
	self.data_kpi = True
	self.feature = None
	self.debug = False
	
	# Categories
	self.KPI_LABEL_CATEGORY = "HOTSTAR KPI"
	self.genre_id = "Hotstar Genre"	
	
	# KPIs
	self.app_launch_time = None
	self.first_command_end = None

	self.data_kpis = {}

	# KPI Labels
	self.kpi_labels = {}
	self.kpi_labels[kpi_names.LAUNCH_TIME] = {'start': None, 'end': None}
	self.kpi_labels[kpi_names.DOWNLOAD_PAGE_LOAD_TIME] = {'start': None, 'end': None}
	self.kpi_labels[kpi_names.SEARCH_TIME] = {'start': None, 'end': None}
	self.kpi_labels[kpi_names.VIDEO_LOAD_TIME] = {'start': None, 'end': None}
	self.kpi_labels[kpi_names.DETAILS_PAGE_LOAD_TIME] = {'start': None, 'end': None}
	
	
	# Action Labels
	self.ADD_KPI_ANNOTATION = True
	self.session_start = None
	self.appium_timestamps = {}

	self.action_labels = {}

	return self






	