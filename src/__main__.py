from wave_maker import *

from pathlib import Path

if __name__=="__main__":
    data_path = Path(input("Input the file path to the sources data: "))
    output_path = Path(input("Input the output path to store the image in: "))
    
    sources = load_from_csv(data_path)
    image_generator = WaveImageGenerator()
    image_generator.resize(512,256)
    image_generator(sources, output_path)
