# doodleIt

doodleIt converts images into doodle reconstructions.

When converting images into doodle-style reconstructions, transparency (alpha) inconsistencies can cause visual artifacts. Depending on the viewer or browser, “holes” may appear in the final image. To address this, the current implementation uses the pixelated version of the original image as a background and overlays the doodle-generated tiles on top. This ensures consistent results across different viewers and prevents alpha-related rendering issues.
