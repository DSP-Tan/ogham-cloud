import numpy as np

def shared_centre(bbox1,bbox2):
    x0_1, y0_1, x1_1, y1_1 = bbox1
    x0_2, y0_2, x1_2, y1_2 = bbox2

    c1 = (x0_1+x1_1)/2
    c2 = (x0_2+x1_2)/2

    return abs(c1-c2) < 10

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
