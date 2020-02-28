from cb_utilities import *
import cb_cluster, cb_bucket

class view():
    def __init__(self):
        self.methods = ["GET"]
        self.name = "indexes"
        self.filters = [{"variable":"nodes","type":"default","name":"nodes_list","value":[]},
                        {"variable":"buckets","type":"default","name":"bucket_list","value":[]},
                        {"variable":"indexes","type":"default","name":"indexes_list","value":[]}]
        self.comment = '''This is the method used to access FTS metrics'''
        self.service_identifier = "index"

def run(url="", user="", passwrd="", index=[], buckets=[], nodes=[]):
    '''Entry point for getting the metrics for the index nodes'''
    url = check_cluster(url, user, passwrd)
    metrics = []
    cluster_values = cb_cluster._get_cluster(url, user, passwrd, [])
    if len(buckets) == 0:
        buckets = cb_bucket._get_index_buckets(url, user, passwrd)

    if len(nodes) == 0:

        if len(cluster_values['serviceNodes']['index']) > 0 and len(buckets) > 0:
            index_metrics = _get_metrics(
                user,
                passwrd,
                cluster_values['serviceNodes']['index'],
                buckets, cluster_values['clusterName'])

            metrics = index_metrics['metrics']
    else:

        if len(buckets) > 0:
            index_metrics = _get_metrics(
                user,
                passwrd,
                nodes,
                buckets, cluster_values['clusterName'])

            metrics = index_metrics['metrics']

    return metrics

def _get_metrics(user, passwrd, nodes, buckets, cluster_name=""):
    '''Gets the metrics for the indexes nodes, then gets the metrics for each index'''
    index_info = {}
    index_info['metrics'] = []
    auth = basic_authorization(user, passwrd)

    # get cluster index info
    for node in nodes:
        _index_url = "http://{}:8091/pools/default/buckets/@index/nodes/{}:8091/stats".format(
            node.split(":")[0], node.split(":")[0])
        try:
            i_json = rest_request(auth, _index_url)
            _node = node
            for record in i_json['op']['samples']:
                if record != "timestamp":
                    for idx, datapoint in enumerate(i_json['op']['samples'][record]):
                        index_info['metrics'].append(
                            "{} {{cluster=\"{}\", node=\"{}\", "
                            "type=\"index-service\"}} {} {}".format(
                                record,
                                cluster_name,
                                _node,
                                datapoint,
                                i_json['op']['samples']['timestamp'][idx]))

        except Exception as e:
            print("index base: " + str(e))

    for node in nodes:
        for bucket in buckets:
            try:
                index_info_url = "http://{}:8091/pools/default/buckets/@index-{}/" \
                                 "nodes/{}:8091/stats".format(node.split(":")[0],
                                                              bucket,
                                                              node.split(":")[0])
                ii_json = rest_request(auth, index_info_url)
                for record in ii_json['op']['samples']:
                    name = ""
                    index_type = ""
                    _node = node
                    try:
                        split_record = record.split("/")
                        if len(split_record) == 3:
                            name = (split_record[1]).replace("+", "_")
                            index_type = (split_record[2]).replace("+", "_")
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\","
                                        "index=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index\"}} {} {}".format(
                                            index_type,
                                            cluster_name,
                                            _node,
                                            name,
                                            bucket,
                                            datapoint,
                                            ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "index=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index\"}} {}".format(
                                        index_type,
                                        cluster_name,
                                        _node,
                                        name,
                                        bucket,
                                        ii_json['op']['samples'][record]))

                        elif len(split_record) == 2:
                            index_type = split_record[1]
                            if isinstance(ii_json['op']['samples'][record], type([])):
                                for idx, datapoint in enumerate(ii_json['op']['samples'][record]):
                                    index_info['metrics'].append(
                                        "{} {{cluster=\"{}\", node=\"{}\", "
                                        "bucket=\"{}\", "
                                        "type=\"index\"}} {} {}".format(
                                            index_type,
                                            cluster_name,
                                            _node,
                                            bucket,
                                            datapoint,
                                            ii_json['op']['samples']['timestamp'][idx]))
                            else:
                                index_info['metrics'].append(
                                    "{} {{cluster=\"{}\", node=\"{}\", "
                                    "bucket=\"{}\", "
                                    "type=\"index\"}} {}".format(
                                        index_type,
                                        cluster_name,
                                        _node,
                                        bucket,
                                        ii_json['op']['samples'][record]))
                        else:
                            next
                    except Exception as e:
                        print("index specific: " + str(e))

            except Exception as e:
                print("index: " + str(e))

    return index_info
