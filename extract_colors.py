import colorgram

# Extract 2 distinct colors from the image
colors = colorgram.extract('logo.jpg', 2)
for color in colors:
    rgb = color.rgb
    hex_code = '#%02x%02x%02x' % (rgb.r, rgb.g, rgb.b)
    print(f"Color: {hex_code} (Proportion: {color.proportion})")
