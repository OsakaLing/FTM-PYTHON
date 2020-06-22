"""
Computational domain related classes
Created on Sat Jun 20 19:45:03 2020

@author: mirsandiharyo
"""

import numpy as np
import math

class Domain:
    def __init__(self, lx, ly, nx, ny, gravx, gravy):
        self.lx = lx
        self.ly = ly
        self.nx = nx
        self.ny = ny
        self.gravx = gravx
        self.gravy = gravy
        self.dx = self.lx/self.nx;
        self.dy = self.ly/self.ny;

    def get_cell_index(self, x, y, axis):
        # fetch the indices of the eulerian cell located on the left of a given point
        if (axis == 1):      # x-dir
            index_x = math.floor(x/self.dx)+1;
            index_y = math.floor((y+0.5*self.dy)/self.dy)+1      
        else:                # y-dir
            index_x = math.floor((x+0.5*self.dx)/self.dx)+1
            index_y = math.floor(y/self.dy)+1
        return index_x, index_y
        
    def get_weight_coeff(self, x, y, index_x, index_y, axis):
        # calculate the weight coefficients of a point with respect to its location
        # inside the eulerian cell
        if (axis == 1):      # x-dir
            coeff_x = x/self.dx-index_x+1
            coeff_y = (y+0.5*self.dy)/self.dy-index_y+1
        else:                # y-dir
            coeff_x = (x+0.5*self.dx)/self.dx-index_x+1
            coeff_y = y/self.dy-index_y+1
        return coeff_x, coeff_y

class Face:
    def __init__(self, domain):
        # initialize variables (liquid is at rest at the beginning)
        # velocity in x-direction
        self.u = np.zeros((domain.nx+1, domain.ny+2))
        self.u_old = np.zeros((domain.nx+1, domain.ny+2))
        self.u_temp = np.zeros((domain.nx+1, domain.ny+2))
        # velocity in y-direction
        self.v = np.zeros((domain.nx+2, domain.ny+1))
        self.v_old = np.zeros((domain.nx+2, domain.ny+1))
        self.v_temp = np.zeros((domain.nx+2, domain.ny+1))
        # forces
        self.force_x = np.zeros((domain.nx+2, domain.ny+2))
        self.force_y = np.zeros((domain.nx+2, domain.ny+2))
    
    def initialize_force(self, domain):
        self.force_x = np.zeros((domain.nx+2, domain.ny+2))
        self.force_y = np.zeros((domain.nx+2, domain.ny+2))
        
    def store_old_variables(self):
        # store old variables for second order scheme
        self.u_old = self.u
        self.v_old = self.v

class Center:
    def __init__(self, domain):
        # set the grid
        self.x = np.linspace(-0.5, domain.nx+2-1.5, domain.nx+2)*domain.dx
        self.y = np.linspace(-0.5, domain.ny+2-1.5, domain.ny+2)*domain.dy;
        # pressure
        self.pres = np.zeros((domain.nx+2, domain.ny+2))  
    
  