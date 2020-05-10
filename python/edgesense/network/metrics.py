import networkx as nx
import community as co
from edgesense.network.utils import extract_dpsg


# build the deparallelized subnetworks to use for metrics
# compute the metrics by timestep on the deparallelized network
# Cluster, K-Cores, PageRank, 
# betweennessCentralityCount, betweennessCentralityEffort
# graphDensity, modularityCount, modularityEffort
# averageClusteringCoefficient
# Indegree, Outdegree
def extract_network_metrics(mdg, ts, team=True):
    met = {}
    dsg = extract_dpsg(mdg, ts, team)
    if team :
        pre = 'full:'
    else:
        pre = 'user:'

    # avoid trying to compute metrics for  
    # the case of empty networks 
    if dsg.number_of_nodes() == 0:
        return met

    met[pre+'nodes_count'] = dsg.number_of_nodes()
    met[pre+'edges_count'] = dsg.number_of_edges()
    met[pre+'density'] = nx.density(dsg)
    met[pre+'betweenness'] = nx.betweenness_centrality(dsg)
    met[pre+'avg_betweenness'] = sum(met[pre+'betweenness'].values())/len(met[pre+'betweenness'])
    met[pre+'betweenness_count'] = nx.betweenness_centrality(dsg, weight='count')
    met[pre+'avg_betweenness_count'] = sum(met[pre+'betweenness_count'].values())/len(met[pre+'betweenness_count'])
    met[pre+'betweenness_effort'] = nx.betweenness_centrality(dsg, weight='effort')
    met[pre+'avg_betweenness_effort'] = sum(met[pre+'betweenness_effort'].values())/len(met[pre+'betweenness_effort'])
    met[pre+'in_degree'] = dict(dsg.in_degree())
    met[pre+'avg_in_degree'] = sum(met[pre+'in_degree'].values())/len(met[pre+'in_degree'])
    met[pre+'out_degree'] = dict(dsg.out_degree())
    met[pre+'avg_out_degree'] = sum(met[pre+'out_degree'].values())/len(met[pre+'out_degree'])
    met[pre+'degree'] = dict(dsg.degree())
    met[pre+'avg_degree'] = sum(met[pre+'degree'].values())/len(met[pre+'degree'])
    met[pre+'degree_count'] = dict(dsg.degree(weight='count'))
    met[pre+'avg_degree_count'] = sum(met[pre+'degree_count'].values())/len(met[pre+'degree_count'])
    met[pre+'degree_effort'] = dict(dsg.degree(weight='effort'))
    met[pre+'avg_degree_effort'] = sum(met[pre+'degree_effort'].values())/len(met[pre+'degree_effort'])
    usg = dsg.to_undirected()
    louvain = extract_louvain_modularity(usg)
    met[pre+'partitions'] = louvain['partitions']
    met[pre+'louvain_modularity'] = louvain['modularity']
    connected_components = [usg.subgraph(c) for c in nx.connected.connected_components(usg)]
    shortest_paths = [nx.average_shortest_path_length(g) for g in connected_components if g.size()>1]
    if len(shortest_paths) > 0:
        met[pre+'avg_distance'] = max(shortest_paths)
    else:
        met[pre+'avg_distance'] = None
    return met


def extract_louvain_modularity(g):
    met = {}
    usg = g.copy()
    isolated = list(nx.isolates(usg))
    usg.remove_nodes_from(isolated)
    dendo = co.generate_dendrogram(usg)
    if len(dendo) > 0 and isinstance(dendo, list):
        partition = co.partition_at_level(dendo, len(dendo) - 1 )
        met['partitions'] = {}
        for com in set(partition.values()):
            members = [nodes for nodes in partition.keys() if partition[nodes] == com]
            for member in members:
                met['partitions'][member] = com
        met['modularity'] = co.modularity(partition, usg)
        # for node in isolated:
        #     met['partitions'][node] = None
    else:
        met['partitions'] = None
        met['modularity'] = None

    return met
