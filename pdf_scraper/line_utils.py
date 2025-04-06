import numpy as np 

def get_mode_font(fonts):
    font_counts = np.unique(fonts,return_counts=True)
    maxfontarg  = np.argmax(font_counts[1])
    return fonts[maxfontarg]

def common_font_elems(s1,s2):
    L1, L2 = len(s1), len(s2)
    L = L1 if L1 < L2 else L2
    s3 = ""
    for i in range(L):
        if s1[i]!=s2[i]:
            return s3
        s3 += s1[i]
    return s3

def get_common_font(fonts):
    common_font=fonts[0]
    for font in fonts[1:]:
        common_font =common_font_elems(common_font,font)
    return "".join(common_font)