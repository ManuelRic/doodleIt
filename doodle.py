import os
import numpy as np
from PIL import Image

def pixelate_to_colored_tiles(original_path, tile_path, pixel_size, tile_size, output_path):
    """
    Pixelates the original image and replaces each pixel with a tile tinted
    to match the pixel's color using NumPy for efficient computation.
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

    # Load and resize tile
    tile = Image.open(tile_path).convert("RGBA").resize((tile_size, tile_size))
    tile_array = np.array(tile).astype(float)  # RGBA as float for blending

    # Create final canvas
    final_img = Image.new("RGBA", (pixelated_width * tile_size, pixelated_height * tile_size))

    # Loop over each pixel in the pixelated image
    for y in range(pixelated_height):
        for x in range(pixelated_width):
            # Get pixel color
            r, g, b = pixelated.getpixel((x, y))

            # Create color array for the pixel
            color_array = np.array([r, g, b], dtype=float)

            # Multiply tile RGB by pixel color / 255
            tinted_tile_rgb = tile_array[:, :, :3] * (color_array / 255)

            # Keep alpha channel unchanged
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

# Example usage
pixel_size = 40   # Coarseness of pixelation
tile_size = 20    # Size of each tile in final image

pixelate_to_colored_tiles(
    "Imgs/pf5.jpg",
    "Imgs/Tile/smiley_guy.png",
    pixel_size,
    tile_size,
    "Results/pixelated_colored_tiles.png"
)
