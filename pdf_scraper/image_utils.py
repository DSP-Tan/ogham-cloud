import numpy  as np
import pandas as pd
from PIL import Image
from io import BytesIO
import io
import fitz

import matplotlib.pyplot as plt


def sort_images(images: list[dict]) -> list[dict]:
    """
    Sort images by page and y0.
    """
    return sorted(images, key=lambda img: (img["page"], img["bbox"][1]))

def assign_unique_image_number(images: list[dict]) -> list[dict]:
    """
    The "number" key of the image dictionary provided by pymupdf does not have unique numbers.
    Here we assign a document-unique number according to the order of the list.
    """
    for i, img in enumerate(images, start=1):
        img["number"] = i
    return images

def sort_and_rename_images(images: list[dict]) -> list[dict]:
    sorted_ims = sorted(images, key=lambda img: (img["page"], img["bbox"][1]))
    for i, img in enumerate(sorted_ims, start=1):
        img["number"] = i
    return images

def is_point_image(img, threshold=5):
    x0, y0, x1, y1 = img["bbox"]
    return (x1 - x0) < threshold and (y1 - y0) < threshold

def is_horizontal_strip(img):
    return img["height"] <2 and img["width"] > 40

def filter_point_images(images):
    return [img for img in images if not is_point_image(img) ]

def filter_horizontal_strips(images):
    return [img for img in images if not is_horizontal_strip(img)]


def find_contiguous_image_pairs(images, tol) -> list[list[dict]]:
    """
    This function will find any images that share the same x0 and x1 position,
    and are vertically contiguous. I.e. the y1 of the image above ~ the y0 of 
    that below.
    
    It will return a list of lists of pairs of images, all of which are vertically
    touching, and horizontally aligned.
    
    This function deals with the fact that in many pdfs there are images which have been
    for some reason divided in two on being extracted by pymupdf, likely an artifact of 
    microsoft word translation to pdf.
    """
    contiguous_image_pairs = []
    for i in range(len(images)):
        for j in range(i+1,len(images)):
            im_a, im_b  = images[i], images[j]
            x0_a, y0_a, x1_a, y1_a = im_a["bbox"]
            x0_b, y0_b, x1_b, y1_b = im_b["bbox"]
    
            same_page = im_a["page"] == im_b["page"]
            same_x    = (x0_a<=x0_b+tol and x0_a>=x0_b-tol) and (x1_a<=x1_b+tol and x1_a>=x1_b-tol)
    
            a_bellow = (y1_a <= y0_b+tol and y1_a >= y0_b-tol)
            a_on_top = (y1_b <= y0_a+tol and y1_b >= y0_a-tol)
            top_bottom_touch = a_bellow or a_on_top
    
            if same_page and same_x and top_bottom_touch:
                contiguous_image_pairs.append([im_a,im_b] )
    return contiguous_image_pairs

def merge_contiguous_pair_lists(contiguous_image_pairs: list[list[dict]]):
    """
    Merge contiguous image pairs (like [1,2], [2,3], [8,9], [9,10], [10,11]) into full groups [[1,2,3], [8,9,10,11]].
    Keeps groups separate by page.
    """
    merged = []

    # Get all involved images in a list
    images       = [img for im_pair in contiguous_image_pairs for img in im_pair] 
    # Get apired image numbers.
    pair_numbers = [[a["number"],b["number"]] for a, b in contiguous_image_pairs]
    
    for pair in pair_numbers:
        added = False
        for group in merged:
            page_pair  = next(im["page"] for im in images if im["number"]==pair[0])
            page_group = next(im["page"] for im in images if im["number"] in group)
            if page_group != page_pair:
                continue

            if any(x in group for x in pair):
                group.update(pair)
                added = True
                break
        if not added:
            merged.append(set(pair))  
    
    merged_ids = [sorted(list(g)) for g in merged]
    image_lookup = {im["number"]: im for im in images}
    contiguous_image_groups = [ [image_lookup[id] for id in id_list] for id_list in merged_ids]
    contiguous_image_groups = [ sort_images(img_list) for img_list in contiguous_image_groups]
    

    return contiguous_image_groups

def identify_contiguous_images(images) -> list[list[dict]]:
    contiguous_image_pairs  = find_contiguous_image_pairs(images,0.01)
    contiguous_image_groups = merge_contiguous_pair_lists(contiguous_image_pairs)
    return contiguous_image_groups

def stitch_strips(image_blocks: list[dict]) -> dict:
    """
    Stitch a list of horizontal image strips (already sorted top-to-bottom), belonging to the same image 
    into a single image. Return a dictionary mimicking a fitz text block.
    """
    # check if strips or contiguous:
    strip_blocks = identify_contiguous_images(image_blocks)[0]
    if not strip_blocks:
        return image_blocks
    images = [Image.open(io.BytesIO(block["image"])) for block in strip_blocks]

    total_height = sum(img.height for img in images)
    max_width    = max(img.width for img in images)

    stitched = Image.new("RGB", (max_width, total_height), (255, 255, 255))
    offset = 0
    for img in images:
        stitched.paste(img, (0, offset))
        offset += img.height

    img_byte_arr = io.BytesIO()
    stitched.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()
    stitched.close(); img_byte_arr.close()

    min_number = min(block["number"]  for block in image_blocks)
    min_x0     = min(block["bbox"][0] for block in image_blocks)
    min_y0     = min(block["bbox"][1] for block in image_blocks)
    max_x1     = max(block["bbox"][2] for block in image_blocks)
    max_y1     = max(block["bbox"][3] for block in image_blocks)
    bbox = (min_x0, min_y0, max_x1, max_y1)

    img_block = image_blocks[0].copy()
    img_block["number"]=min_number
    img_block["bbox"]=bbox
    img_block['width']= stitched.width
    img_block['height']= stitched.height
    img_block['size']= len(img_bytes)
    img_block['image']= img_bytes

    return img_block

def reconstitute_split_images(image_blocks: dict):
    split_images = identify_contiguous_images(image_blocks)
    split_ids    = [img["number"] for im_group in split_images for img in im_group]

    stitched = [stitch_strips(group) for group in split_images]
    filtered_blocks = [img for img in image_blocks if img["number"] not in split_ids]
    filtered_blocks.extend(stitched)
    sort_and_rename_images(filtered_blocks)
    return filtered_blocks


def filter_low_res_doubles(images) -> list[dict]:
    """
    There are sometimes on a given pdf page, two versions of a given image, one superposed exactly
    on the other. The one over the other is normally of higher resolution.

    Given that in any case, two images which occupy exactly the same space will not both be visible,
    we can safely filter out one.

    This function will search through a list of images, find such high-low-resolution doubling, and drop
    the lower resolution copy.
    """
    num_pages = [(im["number"],im["page"]) for im in images]
    if len(num_pages) != len(set(num_pages)):
        raise ValueError(
            "Duplicate image numbers detected."
            "Ensure images are sorted and renumbered before filtering."
        )
    
    images_to_drop = []
    for i in range(len(images)):
        for j in range(i+1,len(images)):
            im1, im2  = images[i], images[j]
            num_page1 = im1["number"], im1["page"]
            num_page2 = im2["number"], im2["page"]
            if im2["bbox"]==im1["bbox"] and im2["page"]==im1["page"]:
                images_to_drop.append( num_page1 if im1["size"] < im2["size"] else num_page2  )
    filtered_images = [im for im in images if (im["number"],im["page"]) not in images_to_drop]
    return filtered_images


def get_in_image_lines(image: dict,doc_df: pd.DataFrame) -> pd.Index:
    rect = fitz.Rect(*image["bbox"])

    overlap_mask = (
        (doc_df["x1"] > rect.x0 + 0.2) &
        (doc_df["x0"] < rect.x1) &
        (doc_df["y1"] > rect.y0 + 0.2) &
        (doc_df["y0"] < rect.y1) &
        (doc_df["page"] == image["page"] )
    )
    return doc_df[overlap_mask].index

def get_in_image_captions(image: dict, doc_df: pd.DataFrame, indices: pd.Index) -> str:
    """
    Find all text contained within an image's bounding box. To be used together
    with get_in_image_lines which will provide the indices fo the lines in the bounding
    box of the image.
    """
    overlapping_rows = doc_df.loc[indices].copy()

    overlapping_rows = overlapping_rows.sort_values(by="y0")
    lines = overlapping_rows.groupby("y0")["text"].apply(lambda x: " ".join(x.astype(str)))

    caption = "\n".join(lines).strip()

    return caption

#########################################################################################################
############################### Image Visualisation Functions ###########################################
#########################################################################################################

def show_image(image):
    """
    This function is for executing in a notebook to view an image based on the image block dictionary.
    """
    img_bytes = image["image"]
    img_stream = BytesIO(img_bytes)
    img = Image.open(img_stream)
    return img

def show_all_imgs(nrows,ncols, imgs):
    fig, axes = plt.subplots(nrows, ncols, figsize=(18, 5))
    for i, ax in enumerate(axes.flat):
        if i < len(imgs):  # Only show the available imgs
            img_bytes = imgs[i]["image"]
            img = Image.open(BytesIO(img_bytes))
            ax.imshow(img)
            ax.set_title("Page: "+str(imgs[i]['page'])+"; "+imgs[i]["caption"] + str(imgs[i]["number"]) )
            ax.axis('off')
        else:
            ax.axis('off')  # Hide empty subplot

    plt.tight_layout()
    plt.show()

def get_bboxed_page_image(doc,  page_number: int, rects: list[fitz.Rect],  color: tuple[float]=(0,0,0.0), labels: list[int] = None ) -> Image:
    """
    This function returns an image of a document page with the passed in list of rectangles drawn on it and optionally numbered.
    It can be used to check clustering on a pdf page, or to check the visual appearance of the bbox of any object or class
    of objects.

    doc: a fitz.Document object
    page_number: the page of this document you are looking at
    rects: a list of fitz.Rect objects which will be drawn on the page.
    color: the color of te drawn rectangles.
    labels: the labels of the rectangles which will be drawn on the page with them.
    """
    i_p  = int(page_number-1)

    out_doc = fitz.open()
    out_doc.insert_pdf(doc, from_page=i_p, to_page=i_p)
    page = out_doc[0]

    for i, rect in enumerate(rects):
        page.draw_rect(rect, color=color, width=3)
        if np.any(labels):
            label_text = str(labels[i])
            pos = fitz.Point((rect.x0+rect.x1)/2.0, rect.y0 - 2)  # adjust -2 for spacing
            page.insert_text(pos, label_text, fontsize=8, color=(1,0,0))

    pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))  # scale=2 for higher resolution
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    out_doc.close()

    return img

