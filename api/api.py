import time
import json
import requests

from jsonpath_ng import jsonpath, parse
from checks import AgentCheck
from hashlib import md5

check_name = "api_check"

class APICheck(AgentCheck):
    def check(self, instance):
        if 'url' not in instance:
            self.log.info("Skipping instance, no url found.")
            return

        # Load values from the instance configuration
        url = instance['url']
        # Use a hash of the URL as an aggregation key
        aggregation_key = md5(url).hexdigest()

        default_timeout = self.init_config.get('default_timeout', 5)
        timeout = float(instance.get('timeout', default_timeout))
        default_prefix = self.init_config.get('prefix', "api")
        prefix = instance.get('prefix', default_prefix)
        metrics = instance.get('metrics', [])
        tags = instance.get('tags',[])
        self.log.info(tags)

        metric_tags = []

        # Query the API
        try:
            r = requests.get(url, timeout=timeout)
            # Check for invalid status code
            if r.status_code != 200:
                self.status_code_event(url, r, aggregation_key)
                return
           # Parse out tags
            for t in tags:
                if t['type'] == "string":
                    metric_tags.append(t['name']+':'+t['value'])
                elif t['type'] == "jsonpath":
                    jsonpath_expr = parse(t['value'])
                    arr = [str(match.value) for match in jsonpath_expr.find(r.json())]
                    for a in arr:
                        metric_tags.append(t['name']+':'+a)
            self.log.debug(metric_tags)

           # Parse out metrics. For now, this only takes the first found metric. Later support should include multiple items.
            for m in metrics:
                for key, expr in m.items():
                    jsonpath_expr = parse(expr)
                    arr = [str(match.value) for match in jsonpath_expr.find(r.json())]
                    if len(arr) > 0:
                        self.gauge(prefix+'.'+key, arr[0], tags=metric_tags)

        # Handle Timeouts
        except requests.exceptions.Timeout as e:
            # If there's a timeout
            self.timeout_event(url, timeout, aggregation_key)
            return

    def timeout_event(self, url, timeout, aggregation_key):
        self.event({
            'timestamp': int(time.time()),
            'event_type': check_name,
            'msg_title': 'API Timeout',
            'msg_text': '%s timed out after %s seconds.' % (url, timeout),
            'aggregation_key': aggregation_key
        })

    def status_code_event(self, url, r, aggregation_key):
        self.event({
            'timestamp': int(time.time()),
            'event_type': check_name,
            'msg_title': 'Not-OK (200) API response code for %s' % url,
            'msg_text': '%s returned a status of %s' % (url, r.status_code),
            'aggregation_key': aggregation_key
        })
