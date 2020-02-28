from cb_utilities import *
import cb_cluster

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "bucket"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"buckets","type":"default","name":"bucket_list","value":[]}]
        self.comment = '''This is the method used to access bucket metrics'''
        self.service_identifier = "kv"

def run(url="", user="", passwrd="", buckets=[], nodes=[]):
    '''Entry point for getting the metrics for the kv nodes and buckets'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if len(nodes) == 0:
        if len(cluster_values['serviceNodes']['kv']) > 0:
            bucket_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['kv'],
                cluster_values['clusterName'],
                buckets)
            metrics = bucket_metrics['metrics']
    else:
        bucket_metrics = _get_metrics(
            user, passwrd, nodes, cluster_values['clusterName'], buckets)
        metrics = bucket_metrics['metrics']
    return metrics

def _get_index_buckets(url, user, passwrd):
    '''Gets a unique list of all of the buckets in the cluster that have indexes'''
    buckets = []

    auth = basic_authorization(user, passwrd)

    try:
        _url = "http://{}:8091/indexStatus".format(url.split(":")[0])
        result = rest_request(auth, _url)


        for index in result['indexes']:
            if index['bucket'] not in buckets:
                buckets.append(index['bucket'])

        buckets.sort()

    except Exception as e:
        print("indexStatus: " + str(e))
    return buckets

def _get_metrics(user, passwrd, node_list, cluster_name="", bucket_names=[]):
    '''Gets the metrics for each bucket'''
    bucket_info = {}
    bucket_info['buckets'] = []
    bucket_info['metrics'] = []

    auth = basic_authorization(user, passwrd)

    try:
        for uri in node_list:
            try:
                _url = "http://{}:8091/pools/default/buckets".format(uri.split(":")[0])
                f_json = rest_request(auth, _url)
                break
            except Exception as e:
                print("Error getting buckets from node: {}: {}".format(uri, str(e.args)))
        for node in node_list:
            try:
                if len(bucket_names) == 0:
                    for bucket in f_json:
                        bucket_info['buckets'].append(bucket['name'])
                        bucket_url = "http://{}:8091/pools/default/buckets/" \
                                     "{}/nodes/{}:8091/stats".format(
                            node.split(":")[0], bucket['name'], node.split(":")[0])
                        b_json = rest_request(auth, bucket_url)
                        _node = node
                        for _record in b_json['op']['samples']:
                            record = value_to_string(_record)
                            if record != "timestamp":
                                if len(record.split("/")) == 3:
                                    ddoc_type = record.split("/")[0]
                                    ddoc_uuid = record.split("/")[1]
                                    ddoc_stat = record.split("/")[2]
                                    for idx, dpt in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{cluster=\"{}\", bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"view\" "
                                            "viewType=\"{}\", "
                                            "view=\"{}\"}} {} {}".format(
                                                ddoc_stat,
                                                cluster_name,
                                                bucket['name'],
                                                _node,
                                                ddoc_type,
                                                ddoc_uuid,
                                                dpt,
                                                b_json['op']['samples']['timestamp'][idx]))

                                else:
                                    for idx, dpt in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{cluster=\"{}\", bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"bucket\"}} {} {}".format(
                                                record,
                                                cluster_name,
                                                bucket['name'],
                                                _node,
                                                dpt,
                                                b_json['op']['samples']['timestamp'][idx]))
                else:
                    for bucket in bucket_names:
                        bucket_info['buckets'].append(bucket)
                        bucket_url = "http://{}:8091/pools/default/buckets/" \
                                     "{}/nodes/{}:8091/stats".format(node.split(":")[0],
                                                                     bucket,
                                                                     node.split(":")[0])
                        b_json = rest_request(auth, bucket_url)
                        _node = node
                        for _record in b_json['op']['samples']:
                            record = value_to_string(_record)
                            if record != "timestamp":
                                if len(record.split("/")) == 3:
                                    ddoc_type = record.split("/")[0]
                                    ddoc_uuid = record.split("/")[1]
                                    ddoc_stat = record.split("/")[2]
                                    for idx, dpt in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{cluster=\"{}\", bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"view\" "
                                            "viewType=\"{}\", "
                                            "view=\"{}\"}} {} {}".format(
                                                ddoc_stat,
                                                cluster_name,
                                                bucket,
                                                _node,
                                                ddoc_type,
                                                ddoc_uuid,
                                                dpt,
                                                b_json['op']['samples']['timestamp'][idx]))

                                else:
                                    for idx, dpt in enumerate(b_json['op']['samples'][_record]):
                                        bucket_info['metrics'].append(
                                            "{} {{cluster=\"{}\", bucket=\"{}\", "
                                            "node=\"{}\", "
                                            "type=\"bucket\"}} {} {}".format(
                                                record,
                                                cluster_name,
                                                bucket,
                                                _node,
                                                dpt,
                                                b_json['op']['samples']['timestamp'][idx]))
            except Exception as e:
                print(e)
    except Exception as e:
        pass
    return bucket_info
