import os
import random
import numpy as np
from PIL import Image, ImageFilter

def pixelate_to_colored_tiles(original_path, tile_folder, pixel_size, tile_size, output_path,
                              overlap_scale):
    """
    Creates pixel mosaic using tiles that are LARGER than pixel grid cells so they overlap,
    and randomly decides whether each tile is drawn above or below existing tiles.
    """

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load original image
    original = Image.open(original_path).convert("RGB")
    width, height = original.size

    # Pixelate down
    pixelated = original.resize(
        (max(1, width // pixel_size), max(1, height // pixel_size)),
        resample=Image.BILINEAR
    )
    pw, ph = pixelated.size

    # Load tile images
    tile_paths = [os.path.join(tile_folder, f) for f in os.listdir(tile_folder)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not tile_paths:
        raise ValueError("No tile images found in the tile folder!")

    # The NEW overlap size (bigger than tile_size)
    overlapped_tile_size = int(tile_size * overlap_scale)

    tiles = [
        np.array(
            Image.open(p).convert("RGBA").resize((overlapped_tile_size, overlapped_tile_size))
        ).astype(float)
        for p in tile_paths
    ]

    # Final canvas
    final_img = Image.new("RGBA", (pw * tile_size, ph * tile_size), (0,0,0,0))

    tile_index = 0
    num_tiles = len(tiles)

    for y in range(ph):
        for x in range(pw):

            r, g, b = pixelated.getpixel((x, y))
            color_array = np.array([r, g, b], dtype=float)

            tile_array = tiles[tile_index]
            tile_index = (tile_index + 1) % num_tiles

            tinted_rgb = tile_array[:, :, :3] * (color_array / 255)
            alpha = tile_array[:, :, 3]

            tinted_tile_array = np.dstack([tinted_rgb, alpha])
            tinted_tile_array = np.clip(tinted_tile_array, 0, 255).astype(np.uint8)
            tinted_tile = Image.fromarray(tinted_tile_array, 'RGBA')

            # base placement (center the enlarged tile)
            px = x * tile_size - (overlapped_tile_size - tile_size) // 2
            py = y * tile_size - (overlapped_tile_size - tile_size) // 2

            # Random overlapped stacking
            draw_on_top = random.choice([True, False])

            if draw_on_top:
                # draw normally on top
                final_img.paste(tinted_tile, (px, py), tinted_tile)
            else:
                # draw below: composite reversed
                layer = Image.new("RGBA", final_img.size, (0,0,0,0))
                layer.paste(tinted_tile, (px, py), tinted_tile)
                final_img = Image.alpha_composite(layer, final_img)

    final_img.show(output_path)
    print(f"Saved mosaic with overlap to {output_path}")

    return final_img

doodled_img = pixelate_to_colored_tiles(
    "Imgs/screaming_skull.jpg",
    "Imgs/Tile",
    pixel_size=15,
    tile_size=40,
    output_path="Results/doodle_overlap.png",
    overlap_scale=2   # tiles are 2× bigger than pixel grid
)
