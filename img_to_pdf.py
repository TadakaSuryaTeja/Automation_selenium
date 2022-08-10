from PIL import Image


def Images_Pdf(filename, output):
    images = []

    for file in filename:
        im = Image.open(file)
        im = im.convert('RGB')
        images.append(im)

        images[0].save(output, save_all=True, append_images=images[1:])


Images_Pdf(["test1.jpg", "test2.jpg", "test3.jpg"], "output.pdf")  ## Images Path , output pdf
