# Kmeans
2. Check customCluster for the case where word mask is the whole array against KMeans. 
   - refactor normal distance calculations as special case of custom case. 
   - Give more meaningful names to all masks. It is confusing at the moment. 


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


## premade solution
Actually, this can be achieved by just doing two consecutive dbscans with just the one variable. Here you will get clusters
of lines contiguous in y0, and clusters of lines contiguous in x0.

Of course this will not implement the "line distance" concept,  but just using x0 and y0 should be sufficient to get vertical
and horizontally grouped lines, and to separate columns too.

## dBscan document categorisation strategy

- Two consecutive clusterings of bboxes. First y0 then x0, each with characteristic eps for the dimension
- Image bboxes must be added to the dataframe
- Distances must be correctly calculated between the ends of boxes. You cannot just use x0 or y0.

# eps_y and eps_x determination 

At the moment eps_y and eps_x are determined using the functions get_eps_x and get_eps_y in cluster_utils.
These do a good job, but have some short comings in cases where there are not many lines on the page.
See for example 2001 page 8.

Ideally, eps_x and eps_y could be determined from the size of a carriage return for a given font. This would require
a custom dbscan.

Alternative modes could be a document wide determination of each.