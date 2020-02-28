#! /usr/bin/python
'''This is the main script for the python exporter for exporting Couchbase
 RestAPI metrics to Prometheus format.'''

# pylint: disable=C0303, C0325, C1801

URL = '18.224.34.238'
USER = 'Administrator'
PASSWD = 'password'

# This is an autogenerated file. DO NOT EDIT BELOW THIS LINE!!!

from modules import *

def get_metrics(url='', user='', passwrd=''):
	cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
	metrics = cluster_values['metrics']
	index_buckets = cb_bucket._get_index_buckets(url, user, passwrd)
	if len(cluster_values['serviceNodes']['cbas']) > 0:
		analytics_metrics = cb_analytics._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['cbas'], cluster_values['clusterName'])
		metrics = metrics + analytics_metrics['metrics']

	if len(cluster_values['serviceNodes']['kv']) > 0:
		bucket_metrics = cb_bucket._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['kv'], cluster_values['clusterName'])
		metrics = metrics + bucket_metrics['metrics']

	if len(cluster_values['serviceNodes']['eventing']) > 0:
		eventing_metrics = cb_eventing._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['eventing'], cluster_values['clusterName'])
		metrics = metrics + eventing_metrics['metrics']

	if len(cluster_values['serviceNodes']['fts']) > 0:
		fts_metrics = cb_fts._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['fts'], cluster_values['clusterName'])
		metrics = metrics + fts_metrics['metrics']

	if len(cluster_values['serviceNodes']['index']) > 0:
		indexes_metrics = cb_index._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['index'], cluster_values['clusterName'])
		metrics = metrics + indexes_metrics['metrics']

	node_exporter_metrics = cb_node_exporter._get_metrics(
		user, passwrd, cluster_values['nodeList'], cluster_values['clusterName'])
	metrics = metrics + node_exporter_metrics['metrics']

	if len(cluster_values['serviceNodes']['n1ql']) > 0:
		query_metrics = cb_query._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['n1ql'], cluster_values['clusterName'])
		metrics = metrics + query_metrics['metrics']

	system_metrics = cb_system._get_metrics(
		user, passwrd, cluster_values['nodeList'], cluster_values['clusterName'])
	metrics = metrics + system_metrics['metrics']

	if len(cluster_values['serviceNodes']['kv']) > 0:
		xdcr_metrics = cb_xdcr._get_metrics(
			user, passwrd, cluster_values['serviceNodes']['kv'], cluster_values['clusterName'])
		metrics = metrics + xdcr_metrics['metrics']

	return(metrics)

if __name__ == '__main__':
	print(get_metrics(URL, USER, PASSWD))
