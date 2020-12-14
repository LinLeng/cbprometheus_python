import re
import sys
from application import application

if sys.version_info[0] == 3:
    from .cb_utilities import *
    from . import cb_cluster
else:
    from cb_utilities import *
    import cb_cluster

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "process_exporter"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"result_set","type":"int","name":"num_samples","value":60}]
        self.comment = '''This is the method used to access prometheus provided Node Exporter Metrics'''
        self.service_identifier = False
        self.inputs = [{"value":"user"},
                        {"value":"passwrd"},
                        {"value":"cluster_values['nodeList']"},
                        {"value":"cluster_values['clusterName']"},
                        {"value":"result_set"}]
        self.exclude = False


def run(url="", user="", passwrd="", nodes=[], num_samples = 60, result_set=60):
    '''Entry point for getting the metrics for the analytics nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if num_samples != 60:
        result_set = num_samples
    if len(nodes) == 0:
        if len(cluster_values['nodeList']) > 0:
            __metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['nodeList'],
                cluster_values['clusterName'])
            metrics = __metrics['metrics']
    else:
        __metrics = _get_metrics(
            user,
            passwrd,
            nodes,
            cluster_values['clusterName'])
        metrics = __metrics['metrics']
    return metrics

def _create_metric(tag, label="", value=""):
    if "#" in tag:
        return(tag.strip())
    else:
     return "{} {{{}}} {}".format(tag, ",".join(label), value)

def _get_metrics(user, passwrd, node_list, cluster_name="", result_set=60):
    '''Process Exporter Metrics'''
    process_metrics = {}
    process_metrics['metrics'] = []
    # Doing this to prevent updating the nodeList with the IP of the exporter
    __node_list = node_list
    if application.config['CB_EXPORTER_MODE'] != "local":
        __node_list = node_list + get_local_ip()

    auth = basic_authorization(user, passwrd)

    for node in __node_list:
        node_hostname = node.split(":")[0]
        try:
            _ne_url = "http://{}:{}/metrics".format(
                node_hostname,
                application.config['CB_PROCESS_EXPORTER_PORT'])
            a_json = text_request(_ne_url)
            _node = node
            for record in a_json:
                tag = ""
                label = ['\"cluster\":\"{}\"'.format(cluster_name),
                            '\"node\":\"{}\"'.format(node_hostname),
                            '\"type\"=\"process_exporter\"']
                _value = ""
                if len(record) == 0:
                    next
                elif "{" in record:
                    _label = (re.search('\{(.*)\}', record.strip()).group(1)).split(",")
                    label += _label
                    tag = re.search('(.*)\{', record.strip()).group(1)
                    _value = re.search('\}(.*)', record.strip()).group(1)
                    process_metrics['metrics'].append(_create_metric(tag, label, _value))
                elif "#" in record:
                    process_metrics['metrics'].append(_create_metric(record))
                else:
                    tag, _value = record.strip().split(" ")
                    process_metrics['metrics'].append(_create_metric(tag, label, _value))
        except Exception as e:
            print("process_exporter base: " + str(e))
    return process_metrics
