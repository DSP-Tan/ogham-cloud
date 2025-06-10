import numpy  as np
import pandas as pd
from PIL import Image
import io
import fitz

def is_point_image(img, threshold=5):
    x0, y0, x1, y1 = img["bbox"]
    return (x1 - x0) < threshold and (y1 - y0) < threshold

def is_horizontal_strip(img):
    return img["height"] <2 and img["width"] > 40

def filter_point_images(images):
    return [img for img in images if not is_point_image(img) ]

def filter_horizontal_strips(images):
    return [img for img in images if not is_horizontal_strip(img)]


def get_stripped_images(images):
    strips = [img for img in images if is_horizontal_strip(img)]
    x0s = np.unique([strip["bbox"][0] for strip in strips])
    if len(x0s) > 1:
        raise ValueError(
                f"Multiple stripped images detected on the page (x0s={x0s}). "
                "Refactor required to handle multiple horizontal strips."
            )
    return strips

def stitch_strips(image_blocks: list[dict]) -> dict:
    """
    Stitch a list of horizontal image strips (already sorted top-to-bottom) into a single image.
    Return a dictionary mimicking a fitz text block.
    """
    strip_blocks = [strip for strip in image_blocks if is_horizontal_strip(strip)]
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
    #'transform': ref_block.get('transform', (1.0, 0.0, 0.0, 1.0, min_x0, min_y0)),

    return img_block

def reconstitute_strips(image_blocks):
    strips = get_stripped_images(image_blocks)
    stitched = stitch_strips(strips)
    filtered_blocks = [img for img in image_blocks if not is_horizontal_strip(img)]
    filtered_blocks.append(stitched)
    filtered_blocks.sort(key=lambda x: (x["page"], x["bbox"][1]))
    return filtered_blocks

def get_in_image_lines(doc_df: pd.DataFrame, image: dict) -> pd.Index:
    img_rect = fitz.Rect(*image["bbox"])

    overlap_mask = (
        (doc_df["x1"] > img_rect.x0 + 0.2) &
        (doc_df["x0"] < img_rect.x1) &
        (doc_df["y1"] > img_rect.y0 + 0.2) &
        (doc_df["y0"] < img_rect.y1) &
        (doc_df["page"] == image["page"] )
    )
    return doc_df[overlap_mask].index

def get_in_image_captions(doc_df: pd.DataFrame, image: dict) -> str:
    """
    Find all text contained within an image's bounding box.
    """
    indices = get_in_image_lines(doc_df, image)
    overlapping_rows = doc_df.loc[indices].copy()

    overlapping_rows = overlapping_rows.sort_values(by="y0")
    lines = overlapping_rows.groupby("y0")["text"].apply(lambda x: " ".join(x.astype(str)))

    caption = "\n".join(lines).strip()

    return caption
