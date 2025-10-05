import numpy as np
import pandas as pd

from config import *


sRGB_basis = (  (0.6400,0.3300,0.2126), # red
                (0.3000,0.6000,0.7512), # green
                (0.1500,0.0600,0.0722), # blue
                (0.3127,0.3290,1.0000)) # white


class ColourSpace(object):
    """
    ColourSpace
    ============
    Basic class to handle colour calculations.

    Args
    ----------------------------
    -  Red, green, blue, and white basis vectors in xyz (colour) coordinates as NumPy arrays."""
    CIE_DATA = pd.read_csv(CIE_DATA_PATH).to_numpy()

    # Set coordinates of colour triangle on CIE diagram
    def __init__(self, r:np.ndarray, g:np.ndarray, b:np.ndarray, w:np.ndarray) -> None:
        self.r, self.g, self.b, self.w = r, g, b, w
        self.xyz_rgb_mat = np.array((r,g,b))
        self.rgb_xyz_mat = np.linalg.inv(self.xyz_rgb_mat)

    @classmethod
    def sRGB(cls):
        """Class method which can be called to instantiate a standard sRGB colourspace based on the sRGB basis values.

        Example
        ----------------------------
        >>> c_space_sRGB = ColourSpace.sRGB()
        
        which is equivalent to:
        >>> c_space_srgb = ColourSpace(*sRGB_basis)
        """
        return cls(*sRGB_basis)

    def xyz_rgb_conv(self, xyz:np.ndarray) -> np.ndarray:
        """Converts an XYZ vector to an RGB (colour) vector."""
        return self.xyz_rgb_mat@(xyz.T)
        
    def rgb_xyz_conv(self, rgb:np.ndarray) -> np.ndarray:
        """Converts an RGB vector to an XYZ (colour) vector."""
        return self.rgb_xyz_mat@(rgb.T)
    
    def wavelength_xyz_conv(self, wavelength:float) -> np.ndarray:
        """Converts a given wavelength to a corresponding XYZ vector based on the CIE data."""
        min_wavelength, max_wavelength = self.CIE_DATA[0][0], self.CIE_DATA[-1][0]
        if(wavelength<min_wavelength or wavelength>max_wavelength): 
            raise ValueError("Wavelength outside visible spectrum.")
        
        return self.CIE_DATA[int(wavelength-min_wavelength)][1:]
    
    def wavelength_rgb_conv(self, wavelength:float) -> np.ndarray:
        """Converts a given wavelength to a corresponding RGB vector based on the CIE data."""
        return self.xyz_rgb_conv(self.wavelength_xyz_conv(wavelength))
    
    def floatvec_intvec_conv(self, vec:np.ndarray) -> np.ndarray:
        """Converts a vector of floats in range [0-1] to a vector of integets in the range [0,255]."""
        return np.clip((vec*256).astype(int), 0, 255)


if __name__=="__main__":
    c_space_srgb = ColourSpace(*sRGB_basis)
    print(c_space_srgb.wavelength_xyz_conv(450))
