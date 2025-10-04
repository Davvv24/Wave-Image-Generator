import numpy as np
import pandas as pd

from config import *


sRGB_basis = (  (0.6400,0.3300,0.2126), # red
                (0.3000,0.6000,0.7512), # green
                (0.1500,0.0600,0.0722), # blue
                (0.3127,0.3290,1.0000)) # white


class ColourSpace(object):
    CIE_DATA = pd.read_csv(CIE_DATA_PATH).to_numpy()

    # Set coordinates of colour triangle on CIE diagram
    def __init__(self, r:np.ndarray, g:np.ndarray, b:np.ndarray, w:np.ndarray) -> None:
        """
        Basic class to handle colour calculations.

        Parameters:
        Basis red, green, blue, and white vectors in xyz coordinates."""
        self.r, self.g, self.b, self.w = r, g, b, w
        self.xyz_rgb_mat = np.array((r,g,b))
        self.rgb_xyz_mat = np.linalg.inv(self.xyz_rgb_mat)

    @classmethod
    def sRGB(cls):
        return cls(*sRGB_basis)

    def xyz_rgb_conv(self, xyz:np.ndarray) -> np.ndarray:
        return self.xyz_rgb_mat@(xyz.T)
        
    def rgb_xyz_conv(self, rgb:np.ndarray) -> np.ndarray:
        return self.rgb_xyz_mat@(rgb.T)
    
    def wavelength_xyz_conv(self, wavelength:float) -> np.ndarray:
        min_wavelength, max_wavelength = self.CIE_DATA[0][0], self.CIE_DATA[-1][0]
        if(wavelength<min_wavelength or wavelength>max_wavelength): 
            raise ValueError("Wavelength outside visible spectrum.")
        
        return self.CIE_DATA[int(wavelength-min_wavelength)][1:]
    
    def wavelength_rgb_conv(self, wavelength:float) -> np.ndarray:
        return self.xyz_rgb_conv(self.wavelength_xyz_conv(wavelength))
    
    def floatvec_intvec_conv(self, vec:np.ndarray) -> np.ndarray:
        return np.clip((vec*256).astype(int), 0, 256)


if __name__=="__main__":
    c_space_srgb = ColourSpace(*sRGB_basis)
    print(c_space_srgb.wavelength_xyz_conv(450))
