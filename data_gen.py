from PIL import Image
import numpy as np
from pathlib import Path
from tqdm.notebook import tqdm
import imageio.v3 as imageio

PATCH_SIZE = 1080

def open_sample(scale=1, PATH='', TXT_Path='', patch_size=(PATCH_SIZE, PATCH_SIZE)):
    img = Image.open(PATH)
    h, w = img.size
    new_size = (h//scale, w//scale)
    image = np.array(img) # .resize(new_size)
    with open(TXT_Path) as f:
        boxes = []
        for line in f:
            txt = line.rstrip("\n")
            txt = [float(t) if i > 0 else int(t) for i, t in enumerate(txt.split())]
            center_x = txt[2] * new_size[1]
            center_y = txt[1] * new_size[0]
            w = txt[4] * new_size[1]
            h = txt[3] * new_size[0]
            x = center_x - w / 2
            y = center_y - h / 2
            boxes.append([txt[0], x, y, w, h])
    
    patches = []
    img_height, img_width, _ = image.shape

    y_steps_ = img_height // patch_size[0]
    x_steps_ = img_width // patch_size[1]
    y_steps = y_steps_ if img_height % patch_size[0] == 0 else y_steps_ + 1
    x_steps = x_steps_ if img_width % patch_size[1] == 0 else y_steps_ + 1

    for y in range(y_steps):
        for x in range(x_steps):
            y_start = y * patch_size[0]
            x_start = x * patch_size[1]
            y_end = min((y + 1) * patch_size[0], img_height)
            x_end = min((x + 1) * patch_size[1], img_width)

            patch = image[y_start:y_end, x_start:x_end]
            patch_bboxes = []
            for bbox in boxes:
                cl, by, bx, bh, bw = bbox
                xmin, ymin, xmax, ymax = bx, by, bx + bw, by + bh
                if (xmin < x_end and xmax > x_start) and (ymin < y_end and ymax > y_start):
                    crop_xmin = max(xmin - x_start, 0)
                    crop_xmax = min(xmax - x_start, x_end - x_start)
                    crop_ymin = max(ymin - y_start, 0)
                    crop_ymax = min(ymax - y_start, y_end - y_start)
                    new_w = crop_xmax - crop_xmin
                    new_h = crop_ymax - crop_ymin
                    patch_bboxes.append({
                        'label': cl,
                        'bbox': [crop_xmin+new_w/2, crop_ymin+new_h/2, new_w, new_h]
                    })
            patches.append((patch, patch_bboxes, [y_start, x_start], [x_start, y_start, x_end, y_end]))
    return patches

def main(orig_path_labels, orig_path_images, save_path_labels, save_path_images, save_path_orig_coord):
    for im_p, l_p in tqdm(list(zip(
            sorted(list(orig_path_images.glob('*.jpg'))),
            sorted(list(orig_path_labels.glob('*.txt')))
        ))):
        sample = open_sample(PATH=im_p, TXT_Path=l_p)
        for sample_ind, sampl in enumerate(sample):
            img, boxes, coords, orig = sampl
            if np.array([i==0 for i in img.shape]).any():
                continue
            
            orig_coord = ' '.join([str(i) for i in orig])
            pp = np.zeros((PATCH_SIZE, PATCH_SIZE, 3), dtype=np.uint8)
            pp[:orig[3]-orig[1], :orig[2]-orig[0], :] = img
            imageio.imwrite(uri=save_path_images/f'{sample_ind}_{im_p.name}', image=pp)
            
            ans = []
            for box in boxes:
                cl = box["label"]
                x, y, w, h = box["bbox"]
                yolo_line = [x, y, w, h] # xcenter ycenter w h
                ans.append([cl, *(i/PATCH_SIZE for i in yolo_line)])
    
            tmp = [' '.join(list(map(str, s))) for s in ans]
            with open(save_path_labels/f'{sample_ind}_{l_p.name}', 'w') as f:
                f.write('\n'.join(tmp)+'\n')
            with open(save_path_orig_coord/f'{sample_ind}_{l_p.name}', 'w') as f:
                f.write(orig_coord+'\n')

if __name__ == "__main__":
    orig_path_labels = Path('/mnt/data/personal_folders/gvozdev/datasets/Welds/all/labels')
    orig_path_images = Path('/mnt/data/personal_folders/gvozdev/datasets/Welds/all/images')
    save_path_labels = Path('/mnt/data/personal_folders/gvozdev/datasets/split_welds/labels')
    save_path_images = Path('/mnt/data/personal_folders/gvozdev/datasets/split_welds/images')
    save_path_orig_coord = Path('/mnt/data/personal_folders/gvozdev/datasets/split_welds/orig_coord')
    
    main(orig_path_labels, orig_path_images, save_path_labels, save_path_images, save_path_orig_coord)
