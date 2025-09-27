from PIL import Image
from PIL.ImageDraw2 import Draw, Pen, Brush, Font
import numpy as np
from dataclasses import dataclass

from progress_bar import ProgressBar
from config import *


@dataclass
class WaveSource(object):
    x: float
    y: float
    wavelength: float
    amplitude: float
    time_phase: float
    space_phase: float
    
def load_from_csv(path:str) -> list[WaveSource]:
    text = open(path,'r').read()                                            # Open the file in read mode and save to a text string
    source_strings = [source for source in text.split('\n') if source.startswith('#')==False]  
    parameters = [[float(val) for val in source.split(',')] for source in source_strings]   # Split I-V strings into float value pairs
    sources = [WaveSource(*parameters[i]) for i in range(len(source_strings))]
    return sources

class WaveImageGenerator(object):
    img_height: int = 256
    img_width: int = 512
    nm_pixel_scale: float = 10.0        # image nanometers per pixel ratio
    brush: Brush
    pen: Pen
    progress_bar: ProgressBar
    legend_colour: str 

    def __init__(self) -> None:
        self.br = Brush("#FFFF00")
        self.pen = Pen("#FF220022")
        self.progress_bar = ProgressBar(pr_bar_char="*", start_text="Loading: ")
        self.legend_colour = "#23617E"


    def __call__(self, sources:list[WaveSource], output_path:str, legend=True, *args, **kwds) -> None:            
        img = Image.new("RGBA",(self.img_width,self.img_height),"black")
        pixels = img.load()
        draw_tool = Draw(img)
        wave_amplitudes = self.calculate_intensities(sources)

        min_amplitude = np.min(wave_amplitudes)
        max_amplitude = np.max(wave_amplitudes)

        # Store values to image and convert according to colour_space
        for i in range(self.img_width):
            for j in range(self.img_height):
                amp = wave_amplitudes[j][i]
                # amp = lambda x: int(128 * self.sigmoid(amp*x))   
                pixels[i,j] = self.amplitude_to_rgb(amp, min_amplitude, max_amplitude)          # store colour to image pixels  #! change this

            self.progress_bar.set_percent(100.0*i/self.img_width)
        self.progress_bar.set_percent(100.0)
        # screen_values = wave_amplitudes[:,-1] # Gets values of last column of pixel. Can be used to obtain intensity at far distance

        self.legend(img, draw_tool)
        img.save(output_path)
        print(f"\nWave image successfully stored at: {output_path}")
        

    def resize(self, img_width:int, img_height:int) -> None:
        self.img_width = img_width
        self.img_height = img_height
    
    def sigmoid(self, x:float) -> float: 
        return 1/(1+np.exp(-x)) 
    
    def amplitude_to_rgb(self, amp, min_amplitude, max_amplitude)->tuple: #! Currently set to only produce white images
        brightness = int(256 * (amp-min_amplitude)/(max_amplitude-min_amplitude))
        return (brightness, brightness, brightness)

    def calculate_intensities(self, sources:list[WaveSource]) -> np.ndarray:
        wave_amplitudes = np.ndarray(shape=(self.img_height,self.img_width))

        # Calculate total displacement for each pixel 
        for i in range(self.img_width):
            for j in range(self.img_height):
                wave_amplitude = 0
                for src in sources:
                    distance = np.hypot((src.x-i),(src.y-j)) * self.nm_pixel_scale  # distance in nm
                    k = 2*np.pi/src.wavelength
                    wave_amplitude += src.amplitude * np.sin(k*distance) # Atotal += Asin(kx-wt+theta+phi) #TODO: change to include other components
                wave_amplitudes[j][i] = wave_amplitude

        # TODO: threshold options
        # threshold = 0
        # if(trace_peak): # mean + 2*standard_deviation
        #     threshold = np.average(wave_inte)+2.0*np.std(wave_vals)
        return wave_amplitudes

    def set_legend_colour(self, colour:str) -> None:
        self.legend_colour = colour

    def legend(self, img:Image, draw_tool:Draw, reference_wavelength:float=400) -> None:
        K = reference_wavelength/self.nm_pixel_scale # n. of pixels to cover a full wavelength 
        font = Font(self.legend_colour, "arial.ttf", size=20)
        text = f"Scale: {self.nm_pixel_scale}nm/pixel\nWavelength: {reference_wavelength}nm"
        x_pos, y_pos= self.img_width-200, self.img_height-50
        bbox = draw_tool.textbbox((0, 0), text, font) # Gets size of text before it's placed
        pen = Pen(self.legend_colour)
        w,h = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw_tool.text((x_pos-(w/2), y_pos-(h/2)), text, font) # Draws text in bottom right corner
        draw_tool.line((x_pos-K/2, y_pos-30, x_pos+K/2, y_pos-30), pen) # Draws wavelength scale line
        draw_tool.line((x_pos+K/2, y_pos-35, x_pos+K/2, y_pos-25), pen)
        draw_tool.line((x_pos-K/2, y_pos-35, x_pos-K/2, y_pos-25), pen)


    
if __name__=="__main__":
    sources = [WaveSource(0, 0, 400, 1, 0, 0), WaveSource(0, 100, 400, 1, 0, 0)]

    image_generator = WaveImageGenerator()
    image_generator.resize(512,256)
    image_generator(sources, r"C:\Users\rizzo\Code\VSC-Asus\University Code\Waves\images_output\img.png")

