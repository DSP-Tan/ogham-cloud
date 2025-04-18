1. Check clustering against standard Kmeans using the normal distance calculation.                        - Done

2. Check customCluster for the case where word mask is the whole array against KMeans. 
   - refactor normal distance calculations as special case of custom case. 
   - Give more meaningful names to all masks. It is confusing at the moment. 

3. Write function to detect possible mixed blocks so you can split them then.
   - see notebook                                                                                          - Done


Organisation:

A directory just for clustering. All the primary clustering functions in cluster.py, the side utilities
like printing etc, will go into cluster_utils.py.                                                           - Done
