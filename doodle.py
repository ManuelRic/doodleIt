from flask import Flask, request, render_template, send_from_directory
from werkzeug.utils import secure_filename
import os
import random
import numpy as np
from PIL import Image
from shutil import copyfile

# Initialize app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/Results'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Your existing image processing function ---
def pixelate_to_colored_tiles(original_path, tile_folder, pixel_size, tile_size, overlap_scale=2):
    original = Image.open(original_path).convert("RGB")
    width, height = original.size
    pixelated = original.resize(
        (max(1, width // pixel_size), max(1, height // pixel_size)),
        resample=Image.BILINEAR
    )
    pw, ph = pixelated.size
    bug_img = os.path.join(tile_folder, "bug.png")

    tile_paths = [os.path.join(tile_folder, f) for f in os.listdir(tile_folder)
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not tile_paths:
        raise ValueError("No tile images found in the tile folder!")

    overlapped_tile_size = int(tile_size * overlap_scale)
    tiles = [
        np.array(
            Image.open(p).convert("RGBA").resize((overlapped_tile_size, overlapped_tile_size))
        ).astype(float)
        for p in tile_paths
    ]

    bug_norm = os.path.normpath(bug_img).lower()
    tile_paths_norm = [os.path.normpath(p).lower() for p in tile_paths]

    bug_x = random.randrange(pw)
    bug_y = random.randrange(ph)

    tile_img = Image.new("RGBA", (pw * tile_size, ph * tile_size), (0, 0, 0, 0))
    num_tiles = len(tiles)

    for y in range(ph):
        for x in range(pw):
            r, g, b = pixelated.getpixel((x, y))
            color_array = np.array([r, g, b], dtype=float)

            if x == bug_x and y == bug_y:
                bug_index = tile_paths_norm.index(bug_norm)
                tile_array = tiles[bug_index]
                is_bug = True
                draw_on_top = True
            else:
                tile_index = random.randrange(num_tiles)
                if not all(tp == bug_norm for tp in tile_paths_norm):
                    while tile_paths_norm[tile_index] == bug_norm:
                        tile_index = random.randrange(num_tiles)
                tile_array = tiles[tile_index]
                is_bug = False
                draw_on_top = random.choice([True, False])

            if is_bug:
                tinted_rgb = tile_array[:, :, :3] * np.array([0.6, 0.4, 0.2], dtype=float)
            else:
                tinted_rgb = tile_array[:, :, :3] * (color_array / 255)

            alpha = tile_array[:, :, 3]
            tinted_tile_array = np.dstack([tinted_rgb, alpha])
            tinted_tile_array = np.clip(tinted_tile_array, 0, 255).astype(np.uint8)
            tinted_tile = Image.fromarray(tinted_tile_array, 'RGBA')

            px = x * tile_size - (overlapped_tile_size - tile_size) // 2
            py = y * tile_size - (overlapped_tile_size - tile_size) // 2

            if draw_on_top:
                tile_img.paste(tinted_tile, (px, py), tinted_tile)
            else:
                layer = Image.new("RGBA", tile_img.size, (0, 0, 0, 0))
                layer.paste(tinted_tile, (px, py), tinted_tile)
                tile_img = Image.alpha_composite(layer, tile_img)

    background = pixelated.resize(tile_img.size)
    background.paste(tile_img, (0, 0), tile_img)
    final_img = background

    output_path = os.path.join(app.config['RESULT_FOLDER'], 'doodled_image.png')
    final_img.save(output_path)
    return output_path

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    image_file = request.files.get('image')
    pixel_size = int(request.form.get('pixel_size', 12))
    tile_size = int(request.form.get('tile_size', 20))

    if not image_file or not allowed_file(image_file.filename):
        return "Invalid file", 400

    filename = secure_filename(image_file.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)

    # Call your doodle function
    result_path = pixelate_to_colored_tiles(image_path, "Imgs/Tile", pixel_size, tile_size)
    # Store path relative to static folder for HTML
    result_image = os.path.relpath(result_path, "static")

    return render_template('index.html', result_image=result_image)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['RESULT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
