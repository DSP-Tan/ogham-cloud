1. Check clustering against standard Kmeans using the normal distance calculation.                        - Done

2. Check customCluster for the case where word mask is the whole array against KMeans. 
   - refactor normal distance calculations as special case of custom case. 
   - Give more meaningful names to all masks. It is confusing at the moment. 

3. Write function to detect possible mixed blocks so you can split them then.
   - see notebook                                                                                          - Done


Organisation:

A directory just for clustering. All the primary clustering functions in cluster.py, the side utilities
like printing etc, will go into cluster_utils.py.                                                           - Done


# Other clustering ideas

## Kmeans ideas
Aside from what you have already implemented:

- square y-dimension to increase importance. 
- experiment more with post standardisation importance scaling of variables.

## Line discontinuity clustering
- Just use the discontinuity in dL for an empty-line-removed, vertically sorted, bunch of lines to find
  the split point. 

## Custom DBScan

DBscan is a great clustering algorithm for line clustering. However, there are features and patterns in 
how lines are spaced that it does not take advantage of in how it calculates the distances.

A good modification would be to have a vector epsilon. If we take the case of just having x, and y coordinates,
we could have an 

epsilon[0] = eps_x: space in x to consider a line a part of a different chunk. This space would be for dual column lines 
             consistent with the centrale strip down the middle of the two columns, and hopefully this distance could
             also be chosen such as to not break off the case where there are several spans on one  line which got 
             separated out.

epsilon[1] = eps_y: Tis can be something like dL, which can just capture when there is the space of one whole empty line between
             two lines. The size of the empty line can be the median line height on the page.

Two lines can be considered within the neighbourhood of each other if:

epsilon[0] <= dX and epsilon[1] < dY

The distance in y between two lines can be 0, if their boxes overlap, or calculated like this:

y0_below = min(y0_1,y0_2)

dy = y1_above - y0_below


