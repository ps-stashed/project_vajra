from PIL import Image, ImageDraw
import os

def create_shapes():
    # Shape 1: Smiley Face
    img1 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(img1)
    # Yellow Face Circle
    draw1.ellipse((2, 2, 29, 29), fill=(255, 215, 0, 255))
    # Eyes
    draw1.ellipse((8, 10, 11, 13), fill=(0, 0, 0, 255))
    draw1.ellipse((20, 10, 23, 13), fill=(0, 0, 0, 255))
    # Smile
    draw1.arc((8, 15, 23, 23), start=0, end=180, fill=(0, 0, 0, 255), width=2)
    
    img1.save("shape1.png")
    print("Created shape1.png (Smiley)")

    # Shape 2: Blue Square with Red Cross
    img2 = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)
    # Blue Box
    draw2.rectangle((4, 4, 27, 27), fill=(0, 100, 255, 255))
    # Red Cross
    draw2.rectangle((14, 4, 17, 27), fill=(255, 50, 50, 255))
    draw2.rectangle((4, 14, 27, 17), fill=(255, 50, 50, 255))

    img2.save("shape2.png")
    print("Created shape2.png (Square Cross)")

if __name__ == "__main__":
    create_shapes()
