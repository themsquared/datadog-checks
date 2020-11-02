import requests

try:
    # first, try to import the base class from new versions of the Agent...
	from datadog_checks.base import AgentCheck, ConfigurationError
except ImportError:
    # ...if the above failed, the check is running in Agent version < 6.6.0
    from checks import AgentCheck

# Some basics
__version__ = "1.0.0"
__metric_base__ = "voltdb"

# VoltDB reported "types"... idk, but this seems arbitrary...
STRING = 9
BIGINT = 6
INT = 5
BOOL = 3

# The actual VoltDB check
class VoltDBCheck(AgentCheck):

	# Build a pretty URL
	def getURL(self, url, port, username, password, procedure, parameters):
		vdbURL = "http://%s:%d/api/1.0/?Procedure=%s&Parameters=%s&admin=false&User=%s&Password=%s" % (url, port, procedure, parameters, username, password)
		return vdbURL

	# Build metrics from data
	def buildMetrics(raw, prefix):
		results = raw['results'][0]
		schema = results['schema']
		data = results['data']

		tags = []
		metrics = []
		processed = []

		for i in range(len(schema)):
			if schema[i]['type'] == STRING:
				tags.append({"index": i, "name": str(schema[i]['name']).lower()})
			else:
				if schema[i]['name'] != 'TIMESTAMP':
					metrics.append({"index": i, "name": str(__metric_base__+'.'+prefix+'.'+schema[i]['name'].lower())})

		print(tags)
		print(metrics)

		# Timestamp should ****ALWAYS**** BE at 0
		# Build metrics with tags
		for point in data:	
			console.log(point);			
			for m in metrics: 
				# Basics...
				newMetric = {
					"name": m['name'],
					"value": point[m['index']],
					"tags": [],
					"timestamp": point[0]
					}
				for t in tags:
					newMetric['tags'].append(t['name']+':'+point[t['index']])
				processed.append(newMetric)
		return processed

	# Submit actual metrics
	def submitMetrics(self, metrics):
		for m in metrics: 
			self.gauge(m['name'], m['value'], tags=m['tags'])

	# Do CPU Checking
	def submitCPU(self, url, port, username, password):
		# get url and build data
		results = requests.get(getURL(url, port, username, password, '@Statistics', '["CPU"]'))
		metrics = this.buildMetrics(results, "cpu")
		this.submitMetrics(metrics)
		return 

	# Do Memory Checking
	def submitMemory(self, url, port, username, password):
		# get url and build data
		results = requests.get(getURL(url, port, username, password, '@Statistics', '["MEMORY"]'))
		metrics = this.buildMetrics(results, "memory")
		this.submitMetrics(metrics)
		return

	# Do Index Checking
	def submitIndex(self, url, port, username, password):
		# get url and build data
		results = requests.get(getURL(url, port, username, password, '@Statistics', '["INDEX"]'))
		metrics = this.buildMetrics(results, "indexes")
		this.submitMetrics(metrics)
		return

	# Do Procedure Checking
	def submitProcedure(self, url, port, username, password):
		# get url and build data
		results = requests.get(getURL(url, port, username, password, '@Statistics', '["PROCEDURE"]'))
		metrics = this.buildMetrics(results, "procedures")
		this.submitMetrics(metrics)
		return

	# Do Procedure Detail Checking
	def submitProcedureDetail(self, url, port, username, password):
		# get url and build data
		results = requests.get(getURL(url, port, username, password, '@Statistics', '["PROCEDUREDETAIL"]'))
		metrics = this.buildMetrics(results, "procedure_detail")
		this.submitMetrics(metrics)
		return

	# Do Procedure Detail Checking
	def submitTables(self, url, port, username, password):
		# get url and build data
		results = requests.get(getURL(url, port, username, password, '@Statistics', '["TABLE"]'))
		metrics = this.buildMetrics(results, "tables")
		this.submitMetrics(metrics)
		return

	# Do the Datadog check!
    def check(self, instance):
    	# Grab the config variables
    	url = instance.get('url')
    	port = instance.get('port')
    	username = instance.get('username')
    	password = instance.get('password')

    	# Check configuration for integration
    	if not url or not port or not username or not password:
    		raise ConfigurationError('There is a configuration error, please fix conf.yaml in voltdb.d!')

    	# Run the cpu check...
    	try: 
    		this.submitCPU(url, port, username, password)
        except Exception as e:
        	raise ConfigurationError('There is a CPU collection error for voltdb.d!')

        # Run the memory check...
    	try: 
    		this.submitMemory(url, port, username, password)
        except Exception as e:
        	raise ConfigurationError('There is a Memory collection error for voltdb.d!')

        # Run the Index check...
    	try: 
    		this.submitIndex(url, port, username, password)
        except Exception as e:
        	raise ConfigurationError('There is an Index collection error for voltdb.d!')

        # Run the Procedure check...
    	try: 
    		this.submitProcedure(url, port, username, password)
        except Exception as e:
        	raise ConfigurationError('There is a Procedure collection error for voltdb.d!')

         # Run the Procedure Detail check...
    	try: 
    		this.submitProcedureDetail(url, port, username, password)
        except Exception as e:
        	raise ConfigurationError('There is a Procedure Detail collection error for voltdb.d!')

        # Run the Table check...
    	try: 
    		this.submitTables(url, port, username, password)
        except Exception as e:
        	raise ConfigurationError('There is a Tables collection error for voltdb.d!')


