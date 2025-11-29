import os
import random
import numpy as np
from PIL import Image

def pixelate_to_colored_tiles(original_path, tile_folder, pixel_size, tile_size, overlap_scale):
    # Load original image
    original = Image.open(original_path).convert("RGB")
    width, height = original.size

    # Pixelate down
    pixelated = original.resize(
        (max(1, width // pixel_size), max(1, height // pixel_size)),
        resample=Image.BILINEAR
    )
    pw, ph = pixelated.size

    bug_img = "Imgs/Tile/bug.png"

    # Load tile images
    tile_paths = [os.path.join(tile_folder, f) for f in os.listdir(tile_folder)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not tile_paths:
        raise ValueError("No tile images found in the tile folder!")

    # Overlap size
    overlapped_tile_size = int(tile_size * overlap_scale)

    tiles = [
        np.array(
            Image.open(p).convert("RGBA").resize((overlapped_tile_size, overlapped_tile_size))
        ).astype(float)
        for p in tile_paths
    ]

    # Normalize paths for bug detection
    bug_norm = os.path.normpath(bug_img).lower()
    tile_paths_norm = [os.path.normpath(p).lower() for p in tile_paths]

    # Pick random location for bug tile
    bug_x = random.randrange(pw)
    bug_y = random.randrange(ph)

    # Final canvas
    final_img = Image.new("RGBA", (pw * tile_size, ph * tile_size), (0, 0, 0, 0))
    num_tiles = len(tiles)

    for y in range(ph):
        for x in range(pw):
            r, g, b = pixelated.getpixel((x, y))
            color_array = np.array([r, g, b], dtype=float)

            # Decide which tile to use
            if x == bug_x and y == bug_y:
                # Force bug tile
                bug_index = tile_paths_norm.index(bug_norm)
                tile_array = tiles[bug_index]
                is_bug = True
                draw_on_top = True
            else:
                tile_index = random.randrange(num_tiles)
                # Avoid picking bug tile again
                if not all(tp == bug_norm for tp in tile_paths_norm):
                    while tile_paths_norm[tile_index] == bug_norm:
                        tile_index = random.randrange(num_tiles)
                tile_array = tiles[tile_index]
                is_bug = False
                draw_on_top = random.choice([True, False])

            # Tinting
            if is_bug:
                tinted_rgb = tile_array[:, :, :3] * np.array([1, 0, 0], dtype=float)  # red bug
            else:
                tinted_rgb = tile_array[:, :, :3] * (color_array / 255)

            alpha = tile_array[:, :, 3]
            tinted_tile_array = np.dstack([tinted_rgb, alpha])
            tinted_tile_array = np.clip(tinted_tile_array, 0, 255).astype(np.uint8)
            tinted_tile = Image.fromarray(tinted_tile_array, 'RGBA')

            # Base placement
            px = x * tile_size - (overlapped_tile_size - tile_size) // 2
            py = y * tile_size - (overlapped_tile_size - tile_size) // 2

            # Draw tile
            if draw_on_top:
                final_img.paste(tinted_tile, (px, py), tinted_tile)
            else:
                layer = Image.new("RGBA", final_img.size, (0, 0, 0, 0))
                layer.paste(tinted_tile, (px, py), tinted_tile)
                final_img = Image.alpha_composite(layer, final_img)

    final_img.save("Results/doodled_image.png")
    final_img.show()
    return final_img

# Run
pixelate_to_colored_tiles(
    "Imgs/popeye.jpg",
    "Imgs/Tile",
    pixel_size=10,
    tile_size=20,
    overlap_scale=2
)
