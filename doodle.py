import os
import numpy as np
from PIL import Image, ImageFilter

def pixelate_to_colored_tiles(original_path, tile_folder, pixel_size, tile_size, output_path):
    """
    Pixelates the original image and replaces each pixel with a tile tinted
    to match the pixel's color using all images in the tile folder in sequence.
    """
    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load original image
    original = Image.open(original_path).convert("RGB")
    width, height = original.size

    # Resize down to create pixelated image
    pixelated = original.resize(
        (max(1, width // pixel_size), max(1, height // pixel_size)),
        resample=Image.BILINEAR
    )

    pixelated_width, pixelated_height = pixelated.size

    # Load all tile images from folder
    tile_paths = [os.path.join(tile_folder, f) for f in os.listdir(tile_folder)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not tile_paths:
        raise ValueError("No tile images found in the specified folder!")

    tiles = [np.array(Image.open(p).convert("RGBA").resize((tile_size, tile_size))).astype(float)
             for p in tile_paths]

    # Create final canvas
    final_img = Image.new("RGBA", (pixelated_width * tile_size, pixelated_height * tile_size))

    tile_index = 0  # To loop through tiles
    num_tiles = len(tiles)

    # Loop over each pixel in the pixelated image
    for y in range(pixelated_height):
        for x in range(pixelated_width):
            # Get pixel color
            r, g, b = pixelated.getpixel((x, y))
            color_array = np.array([r, g, b], dtype=float)

            # Select tile and increment index
            tile_array = tiles[tile_index]
            tile_index = (tile_index + 1) % num_tiles  # Loop back to start

            # Multiply tile RGB by pixel color / 255
            tinted_tile_rgb = tile_array[:, :, :3] * (color_array / 255)
            alpha_channel = tile_array[:, :, 3]

            # Combine RGB + alpha
            tinted_tile_array = np.dstack([tinted_tile_rgb, alpha_channel])
            tinted_tile_array = np.clip(tinted_tile_array, 0, 255).astype(np.uint8)

            tinted_tile = Image.fromarray(tinted_tile_array, 'RGBA')

            # Paste onto final canvas
            px = x * tile_size
            py = y * tile_size
            final_img.paste(tinted_tile, (px, py), mask=tinted_tile)

    # Save result
    final_img.show(output_path)
    print(f"Saved pixelated mosaic to {output_path}")

    return final_img

# Future input parameters
pixel_size = 20   # Coarseness of pixelation
tile_size = 20    # Size of each tile in final image

# Run the function and store the result in a variable 
# As of now the image can only be saved as png due to alpha channel handling
doodled_img = pixelate_to_colored_tiles(
    "Imgs/vexx_paint.jpeg",
    "Imgs/Tile",
    pixel_size,
    tile_size,
    "Results/pixelated_colored_tiles.png"
)