import numpy as np

def shared_centre(bbox1,bbox2, tol):
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2

    c1 = (x0_1+x1_1)/2
    c2 = (x0_2+x1_2)/2

    return abs(c1-c2) < tol

def bbox_distance(bbox1, bbox2):
    """
    Calculates the minimum edge-to-edge distance between two bounding boxes.
    Each box is in [x_min, y_min, x_max, y_max] format.
    Returns 0 if they overlap or touch.
    """
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2

    dx = max(x0_2 - x1_1, x0_1 - x1_2, 0)
    dy = max(y0_2 - y1_1, y0_1 - y1_2, 0)

    return np.hypot(dx, dy)


def bbox_vert_dist(bbox1, bbox2) -> float:
    """
    Returns 0 if the 1D lines (a1, b1) and (a2, b2) overlap or touch.
    Otherwise, returns the minimum distance between their closest endpoints.
    """
    a1,b1 = bbox1[1],bbox1[3]
    a2,b2 = bbox2[1],bbox2[3]

    if max(a1, a2) <= min(b1, b2):
        return 0.0
    return min(abs(b1 - a2), abs(b2 - a1))


def bbox_horiz_dist(bbox1, bbox2) -> float:
    """
    Returns 0 if the 1D lines (a1, b1) and (a2, b2) overlap or touch.
    Otherwise, returns the minimum distance between their closest endpoints.
    """
    a1,b1 = bbox1[0],bbox1[2]
    a2,b2 = bbox2[0],bbox2[2]

    if max(a1, a2) <= min(b1, b2):
        return 0.0
    return min(abs(b1 - a2), abs(b2 - a1))

def df_bbox_next_row_dist(y0, y1, y0_next, y1_next):
    """End-to-end vertical distance between two line segments.

    This function will return 0 if the two bboxes overlap in the chosen dimension.
    Otherwise it will return the distance between their closest endpoints.
    """
    overlap = np.maximum(y0, y0_next) <= np.minimum(y1, y1_next)
    dist = np.where(overlap, 0.0, np.minimum(np.abs(y1 - y0_next), np.abs(y1_next - y0)))
    return dist

def df_bbox_dist(row1, row2):
    """
    This calculates the bbox end to end distance between to dataframe rows.

    It can be used to generate a distance matrix between all rows of a dataframe of lines.
    
    df_bbox_dist(row1[["y0","y1]], row2[["y0","y1"]]) = vertical   end to end bbox distance
    df_bbox_dist(row1[["x0","x1]], row2[["x0","x1"]]) = horizontal end to end bbox distance
    """
    y0, y1 = row1
    y0_next, y1_next = row2

    overlap = max(y0, y0_next) <= min(y1, y1_next)
    if overlap:
        return 0.0
    return min(abs(y1 - y0_next), abs(y1_next - y0))