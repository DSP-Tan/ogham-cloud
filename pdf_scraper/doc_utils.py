import fitz
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
import re
from sklearn.cluster import DBSCAN
from pdf_scraper.block_utils import clean_blocks
from pdf_scraper.line_utils  import get_line_df, get_line_text, get_level_line_counts, get_df_bbox
from pdf_scraper.image_utils import sort_images, assign_unique_image_number
from pdf_scraper.image_utils import is_point_image, is_horizontal_strip,filter_point_images, filter_horizontal_strips
from pdf_scraper.image_utils import filter_horizontal_strips,get_stripped_images,stitch_strips, reconstitute_strips, filter_low_res_doubles
from pdf_scraper.image_utils import get_in_image_lines, get_in_image_captions, reconstitute_split_images
from pdf_scraper.general_utils import bbox_horiz_dist, shared_centre, df_bbox_dist
from pdf_scraper.clustering.cluster_utils import hdbscan, get_eps_x, get_eps_y

subject_code = {
    "irish": "001",
    "english":"002",
    "mathematics":"003",
    "history":"004",
    "applied_mathematics":"020"
}

lang_code = {"irish":"IV", "english":"EV"}

def open_exam(year:int, subject="english", level="al", paper=1):
    code = subject_code[subject.lower()]
    fname    = f"LC{code}{level.upper()}P{paper}00EV_{year}.pdf"
    examDir  = Path(__file__).parent.parent / "Exams"  / subject.lower() / level.upper()
    pdf_file = examDir / fname

    return fitz.open(pdf_file)

def get_path_from_doc(doc):
    return str(doc).split("(")[1].split(")")[0].replace('\'',"")

def get_doc_year(doc):
    """Returns year of exam of document using file path."""
    year = int(str(doc).split("_")[1][:4])
    return year

def extract_and_print_page(input_pdf:str, output_pdf:str, n_page:int):
    doc = fitz.open(input_pdf)

    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=n_page-1, to_page=n_page-1)  
    new_doc.save(output_pdf)
    new_doc.close()
    doc.close()

def get_doc_line_df(doc):
    """
    Returns a data frame of all lines in the document with the page numbers added
    and all lines sorted vertically per page.
    """
    dfs = []
    for i, page in enumerate(doc):
        page_blocks  = page.get_text("dict",sort=True)["blocks"]

        text_blocks  = [block for block in page_blocks if not block["type"]]
        text_blocks  = clean_blocks(text_blocks)

        page_lines   = [ line for block in text_blocks for line in block["lines"]]
        page_df = get_line_df(page_lines)
        page_df["page"] = i+1
        page_df.sort_values("y0",inplace=True)
        dfs.append(page_df)
    doc_df = pd.concat(dfs,ignore_index=True)

    return doc_df

def enrich_doc_df_with_images(df, images):
    """
    This function adds lines to the doc df representing images. It contains the coordinates of the 
    bbox of the image, and a "image" as the category column.
    """
    img_dict = { }
    for i, coord in enumerate(["x0","y0","x1","y1"]):
        img_dict[coord]   = [ img["bbox"][i] for img in images ]
    img_dict["page"]  = [ img["page"]   for img in images]
    img_dict["category"] = ["image"]*len(images)
    img_df = pd.DataFrame(img_dict)    
    rich_df = pd.concat([df, img_df],ignore_index=True).sort_values(by=["page","y0"],ignore_index=True)
    
    return rich_df


def get_raw_lines(doc, row: pd.Series):
    n_page = int(row.page)
    page = doc[n_page -1]
    page_blocks  = page.get_text("dict",sort=True)["blocks"]
    text_blocks  = [block for block in page_blocks if not block["type"]]
    text_blocks  = clean_blocks(text_blocks)
    page_lines   = [ line for block in text_blocks for line in block["lines"]]
    line_texts   = [get_line_text(line) for line in page_lines]
    raw_line_index  = [ i for i, text in enumerate(line_texts) if text == row.text]
    raw_lines = [ page_lines[i] for i in raw_line_index]
    return raw_lines


def get_images(doc):
    images = []
    for i, page in enumerate(doc):
        page_blocks  = page.get_text("dict",sort=True)["blocks"]

        image_blocks = [block for block in page_blocks if     block["type"]]
        for image_block in image_blocks:
            image_block["page"]= i+1
            image_block["caption"] = ""
        images.extend(image_blocks)

    return images

# To Do: This function breaks if you do not sort the images before hand.
# You should find out why this is, and put in extra testing.
def filter_images(images):
    images = sort_images(images)
    images = assign_unique_image_number(images)
    if len(images) > 100:
        images=filter_point_images(images)
    if len(images) > 100:
        images = reconstitute_strips(images)
    images = filter_low_res_doubles(images)
    images = reconstitute_split_images(images)
    return images
    

def assign_in_image_captions(doc_df: pd.DataFrame, images: list[dict]) -> list[dict]:
    """
    Add captions to images based on overlapping boxes. 
    For english paper one, we will not caption anything on the first page, or after the 8th
    """
    all_indices = []
    count=0
    for image in images:
        if image["page"] == 1 or image["page"] >8:
            image["caption"]=""
            continue
        indices=get_in_image_lines(image,doc_df)
        doc_df.loc[indices, "category"]="caption1"
        if len(indices)>0:
            all_indices.append(indices)
            captions = get_in_image_captions(image,doc_df, indices)
            image["caption"] = captions
            count+=1
        else:
            image["caption"] = ""
    
    caption_line_indices = pd.Index(np.concatenate(all_indices)) if all_indices else pd.Index([])

    return caption_line_indices, count

def get_captions(doc_df: pd.DataFrame, images: list[dict]) -> list[dict]:
    """
    Add captions to images based on overlapping boxes. For english paper one, we
    will not caption anything on the first page, or after the 8th
    """
    caption_indices, n_img = assign_in_image_captions(doc_df, images)
    # Captions to add manually
    # 2019 p6: 'Warstones\xa0Library\xa0'
    # 2014 p3: 'Canada by Richard Ford – book cover '
    # 2013 p4:
    # 2013 p6:
    # 2013 p7:

    return images

def identify_instructions(doc_df):
    page = (doc_df.page != 1)
    pattern1 = doc_df.text.str.lstrip().str.contains(r"^N\.B\.")
    pattern2 = doc_df.text.str.contains(r"^Candidates may NOT")
    pattern3 = doc_df.text.str.contains(r"^Questions.*A.*and.*B.*carry.*50.*marks.*each")
    mask = page & (pattern1 | pattern2 | pattern3)
    doc_df.loc[mask, "category"] = "instruction"
    return doc_df

def identify_footers(doc_df):
    doc_df['rank'] = doc_df.groupby('page')['y0'].rank(method='first', ascending=False)

    n_page_regex= r'page[ \xa0]*?(?:1[0-2]|[1-9])[ \xa0]of[ \xa0](?:1[0-2]|[1-9])'
    n_page_regex= r'page[\xa0 ]*?(?:1[0-2]|[1-9])[\xa0 ]*?of[\xa0 ]*?(?:1[0-2]|[1-9])'
    lc_regex    = r'leaving[ \xa0]certificate[ \xa0]examination[ \xa0]20[0-9][0-9]'
    eng_regex   = r'english[ \xa0]–[ \xa0]higher[ \xa0]level[ \xa0]–[ \xa0]paper[ \xa0]1'
    num_regex   = r'^(?:1[0-2]|[1-9])$'

    uncategorised = doc_df.category=="uncategorised"
    pattern1 = doc_df.text.str.lower().str.contains(n_page_regex, regex=True)
    pattern2 = doc_df.text.str.lower().str.contains(lc_regex, regex=True)
    pattern3 = doc_df.text.str.lower().str.contains(eng_regex, regex=True)
    pattern4 = doc_df.text.str.strip().str.contains(num_regex, regex=True)
    bottom   = doc_df['rank'] <= 3

    mask = uncategorised & bottom & (pattern1 | pattern2 | pattern3 | pattern4 )

    doc_df.loc[mask, "category"] = "footer"
    doc_df.drop(columns=["rank"],inplace=True)

    return doc_df

def identify_section_headers(doc_df):
    """
    Section Titles will have the following properties:
    - Centred (if one line)
    - Larger than the median text size on page.
    - Near top
    - Specific text saying Section I or Section II or comprehending or composing.
    """
    doc_df['rank'] = doc_df.groupby('page')['y0'].rank(method='first', ascending=True)

    section_regex= r'section[\xa0 ]*(?:I{1,2}|[1-2])'
    compre_regex = r'comprehending'
    compos_regex = r'composing'
    marks_regex  = r'\(\d{1,3}\s*marks\)'

    pattern1 = doc_df.text.str.contains(section_regex,flags=re.IGNORECASE, regex=True)
    pattern2 = doc_df.text.str.lower().str.contains(compre_regex, regex=True)
    pattern3 = doc_df.text.str.lower().str.contains(compos_regex, regex=True)
    pattern4 = doc_df.text.str.lower().str.strip().str.contains(marks_regex, regex=True)
    top = doc_df['rank'] <= 4

    mask = top & (pattern1 | pattern2 | pattern3 | pattern4 )

    doc_df.loc[mask, "category"] = "section"
    doc_df.drop(columns=["rank"],inplace=True)

    return doc_df

def identify_text_headers(doc_df, doc_width):
    if (doc_df.category=="section").sum() == 0:
        raise RuntimeError("Assign section headings first")
    
    middle         = doc_width/2
    median_size    = doc_df.font_size.median()
    standard_font  = doc_df.mode_font.mode()[0]

    uncategorised  = doc_df.category=="uncategorised"
    large_font    = doc_df.font_size >= median_size*1.15
    bold_font     = doc_df.mode_font.str.contains("Bold")
    pages         = (doc_df.page > 1) & (doc_df.page <9)
    centred       = ( (doc_df.x0 + doc_df.x1)/2 > middle -30 ) & ( (doc_df.x0 + doc_df.x1)/2 < middle +30 )

    doc_df['rank'] = doc_df[uncategorised].groupby('page')['y0'].rank(method='first', ascending=True)
    top            = doc_df['rank'] <= 3

    mask = large_font  & pages & uncategorised & centred & top #& bold_font 

    doc_df.loc[mask, "category" ] = "title"  
    doc_df.drop(columns=["rank"],inplace=True)

    return doc_df


def remove_non_contiguous_lines(df: pd.DataFrame, cat: str):
    """
    Here we identify if there are lines which are not vertically contiguous
    to other lines in the category that has been identified, and we remove
    them from the category. 
    
    This function assumes that a dataframe with rows ordered by y0 is input.
    """
    cat_mask = (df.category == cat)

    if len(df[cat_mask]) <2:
        return df

    line_scale = 1.25
    pages = np.unique(df[cat_mask].page)

    dLs=[]
    for page in pages:
        temp_df = df[(df.page==page) & cat_mask ].copy()
        diffs = temp_df.y0.diff().dropna()
        dLs.append(diffs)
    dL = np.median(np.concat(dLs,axis=0) )

    for i in pages:
        page_df = df[(df.page ==i) & cat_mask ].copy()
        if len(page_df) <2:
            continue
        scan = DBSCAN(eps=dL*line_scale, min_samples=3).fit(page_df[["y0"]])
        # If there are only 2 lines in the subtitle the above dbscan will not be able to find any clusters.
        if len(np.unique(scan.labels_)) == 1:
            scan = DBSCAN(eps=dL*line_scale, min_samples=2).fit(page_df[["y0"]])
        if len(np.unique(scan.labels_)) == 1:
            continue
        not_contig_group = (scan.labels_ != scan.labels_[0])
        page_df.loc[not_contig_group, "category"] = "uncategorised"
        df.loc[page_df.index, "category"] = page_df.category

    return df

def identify_page_clusters(df, x_scale, y_scale):
    """
    This function will perform a hierarchical dbscan using end-to-end line distances on 
    all pages of the document. The clusteres to which a given line or image belong will
    be stored in a column "cluster" which will be added to the input dataframe if it does not
    already exist; if it exists it will be overwritten with the newly calculated clusters.
    """
    if len(df[df.category=="image"])==0:
        raise RuntimeError("Enrich df with images before identifying clusters.")

    df["cluster"]=0

    for page in range(1,9):
        page_df = df[df.page==page].copy()
        eps_x = get_eps_x(page_df, page, x_scale)
        eps_y = get_eps_y(page_df, page, y_scale)
        hdbscan(page_df, 100, eps_x, eps_y, metric=df_bbox_dist)
        df.loc[page_df.index, "cluster"] = page_df.cluster

    return df

def identify_vertical_captions(df,image):
    """
    This function will identify any captions to image contained in df. 
    It will look for captions vertically above or below the image.
    """
    if np.unique(df.clusters).shape[0]<1:
        raise RuntimeError("Identify text and image clusters before searching for captions.")
    i_x0, i_y0, i_x1, i_y1 = image["bbox"]
    img_centre = (i_x0 + i_x1)/2
    within_image_frame = (df.x0 >= i_x0) & (df.x1 <= i_x1)
    centred = df.apply( lambda row: shared_centre( (row["x0"],row["y0"],row["x1"],row["y1"] ),image["bbox"]) , axis=1 )
    uncategorised    = df.category=="uncategorised"
    above_top        = abs(i_y0 - df.y1) <= df.h*2.0
    # We will not use above_top as a condition. There are no captions above images in all pdfs I have seen and it causes non-caption 
    # text to be captured.
    below_bottom     = abs(df.y0 -i_y1)  <= df.h*2.0
    page             = df.page == image["page"]
    mask = page & within_image_frame & centred &  uncategorised &  below_bottom

    df.loc[mask, "category"] = "caption2"
    return df

def get_lines_in_image_clusters(df) -> list[int]:
    """
    This finds any text lines which are contained in the same dbscan clustering as 
    an image. The clustering must be done before, and the dataframe must contain images.

    This list of rows can later be viewed using:
    
    indices = get_lines_in_image_clusters(df)
    mask    = df.index.isin( indices )
    """
    if np.unique(df.cluster).shape[0]<1:
        raise RuntimeError("Identify text and image clusters before searching for captions.")
    if len(df[df.category=="image"])==0:
        raise RuntimeError("Enrich dataframe with images before searching for vertical captions.")

    indices = []
    for page in range(2,9):
        page_df = df[df.page==page]

        is_image             = page_df.category=="image"
        clusters_with_images = np.unique(page_df[is_image].cluster)
        in_image_cluster     = page_df.cluster.isin(clusters_with_images)
        uncategorised        = page_df.category=="uncategorised"
        mask                 = uncategorised & in_image_cluster & ~is_image

        indices.extend( page_df[mask].index.to_list() ) 

    return indices

def new_vertical_captions(df,images):
    """
    This function will identify any captions to image contained in df. 
    It will look for captions vertically above or below the image.
    """
    if np.unique(df.cluster).shape[0]<1:
        raise RuntimeError("Identify text and image clusters before searching for captions.")
    if len(df[df.category=="image"])==0:
        raise RuntimeError("Enrich dataframe with images before searching for vertical captions..")
    
    indices = get_lines_in_image_clusters(df)
    mask    = df.index.isin(indices)
    df.loc[mask,"category"] = "temp"

    for page in range(2,9):
        page_df = df[df.page==page].copy()
        line_image_cluster = page_df.index.isin(indices)
        page_df = page_df[line_image_cluster]

        for i_clust in np.unique(page_df.cluster):
            clust_df   = page_df[page_df.cluster==i_clust]
            image_df   = clust_df[clust_df.category=="image"]

            for i, image in image_df.itterrows():
                i_x0 = image.x0
                i_x1 = image.x1



    
    # Captions will all be on only one side of the image, not on many different sides.
    # If there is lots of text in a box, and it is not all on the same side of the image, it is 
    # not a caption.

    return df


def identify_subtitles(doc_df,doc_width):
    if (doc_df.category=="section").sum() == 0:
        raise RuntimeError("assign section headings first")
    if (doc_df.category=="title").sum() == 0:
        raise RuntimeError("assign text headers first")

    doc_df["counts"]  = get_level_line_counts(doc_df, 0.9)
    df = doc_df[doc_df.category !="image"].copy()

    single_line   = (df.counts == 0)
    bold_font     = df.mode_font.str.contains("Bold")
    starts_left   = df.x0 < doc_width/2
    pages         = (df.page > 1) & (df.page <9)
    title_on_page = (df.category=='title').groupby(df.page).transform('sum') >0
    uncategorised = df.category == "uncategorised"
    after_headers = df[uncategorised].groupby('page')['y0'].rank(method='first', ascending=True) <=6

    mask = pages & uncategorised & after_headers & title_on_page 
    mask2 = ( bold_font.astype(int) + starts_left.astype(int) + single_line.astype(int) ) >=2
    df.loc[mask & mask2 , "category"] = "subtitle"
    df = remove_non_contiguous_lines(df, "subtitle")

    change = df.loc[mask & mask2 ]
    doc_df.loc[change.index,"category"] = change.category

    return doc_df


def identify_subsubtitles(doc_df,doc_width):
    if (doc_df.category=="section").sum() == 0:
        raise RuntimeError("assign section headings first")
    if (doc_df.category=="title").sum() == 0:
        raise RuntimeError("assign text titles first")
    if (doc_df.category=="subtitle").sum() == 0:
        raise RuntimeError("assign text subtitles first")

    middle        = doc_width/2

    single_line      = (doc_df.counts == 0)
    title_on_page    = (doc_df.category=='title').groupby(doc_df.page).transform('sum') >0
    subtitle_on_page = (doc_df.category=='subtitle').groupby(doc_df.page).transform('sum') >0
    pages            = (doc_df.page > 1) & (doc_df.page <9)
    uncategorised    = doc_df.category == "uncategorised"
    after_subtitles  = doc_df[uncategorised].groupby('page')['y0'].rank(method='first', ascending=True) <=10
    italic_or_bold   = (doc_df.mode_font.str.contains("Bold") | doc_df.mode_font.str.contains("Italic") )

    mask = single_line & title_on_page & subtitle_on_page & pages & uncategorised & after_subtitles & italic_or_bold
    doc_df.loc[mask, "category"] = "subsubtitle"
    doc_df = remove_non_contiguous_lines(doc_df, "subsubtitle")

    subsub_df =doc_df[doc_df.category=="subsubtitle"].copy()
    for page in np.unique(subsub_df.page):
        page_df = subsub_df[subsub_df.page==page]
        x0, y0, x1, y1 = get_df_bbox(page_df)

        uncentred = not (x0 <= middle and x1 >= middle)
        
        if uncentred: 
            doc_df.loc[page_df.index, "category"] = "uncategorised"


    return doc_df

    
    
def get_line_overlaps(df):
    counts = np.zeros(len(df), dtype=int)
    
    for page, g in df.groupby("page"):
        y = g["y0"].values
        h_vals = g["h"].values*0.1
        row_counts = []
        for i, (yi, hi) in enumerate(zip(y, h_vals)):
            row_counts.append(np.sum(np.abs(y - yi) <= hi))
        counts[g.index] = row_counts
    
    df["counts"] = counts
    return df

    
def get_full_doc_e2e_dL(doc_df):
    dL_e2e =(
        doc_df.groupby("page",group_keys=False)[["page","x0","x1","y0","y1"]].apply(
        lambda g: g.apply(
            lambda row: get_vert_neigh_dist(row, g, dir), axis=1)) 
        )
    return dL_e2e