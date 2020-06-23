"""
Bubble class
Created on Sat Jun 20 19:06:17 2020

@author: mirsandiharyo
"""

import numpy as np
import math

class Bubble:
    total = 0
    
    def __init__(self, center_x, center_y, radius, point):
        """
        Initialize the bubble.
        """        
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.point = point
        self.x = np.zeros(self.point*2)
        self.y = np.zeros(self.point*2)
        self.x_old = np.zeros(self.point*2)
        self.y_old = np.zeros(self.point*2)        
        Bubble.total += 1
        
    def initialize_front(self):
        """
        Determine the location of the initial spherical bubble.
        """ 
        for i in range(self.point+2):
            self.x[i] = self.center_x-self.radius*math.sin(2.0*math.pi*i/self.point)
            self.y[i] = self.center_y+self.radius*math.cos(2.0*math.pi*i/self.point)
            
    def store_old_variables(self):
        """ 
        Store old variables for second order scheme.
        """ 
        self.x_old = self.x
        self.y_old = self.y

    def store_2nd_order_variables(self):
        """ 
        Store second order variables.
        """ 
        self.x = 0.5*(self.x_old+self.x)
        self.y = 0.5*(self.y_old+self.y)
        
    def calculate_surface_tension(self, domain, fluid_prop, face):
        """ 
        Calculate the surface tension force on the lagrangian grid and
        distribute it to the surrounding eulerian grid cells.
        """
        # initialize the variables to store the tangent vector
        tan_x = np.zeros(self.point+2)
        tan_y = np.zeros(self.point+2)
        # calculate the tangent vector
        for i in range(self.point+1):
            dist = math.sqrt((self.x[i+1]-self.x[i])**2+
                             (self.y[i+1]-self.y[i])**2)
            tan_x[i] = (self.x[i+1]-self.x[i])/dist
            tan_y[i] = (self.y[i+1]-self.y[i])/dist     
        tan_x[self.point+1] = tan_x[1]
        tan_y[self.point+1] = tan_y[1]

        # distribute the surface tension force to the eulerian grid
        for i in range(1, self.point+1):
            # force in x-direction
            force_x = fluid_prop.sigma*(tan_x[i]-tan_x[i-1])
            self.distribute_lagrangian_to_eulerian(
                domain, face.force_x, self.x[i], self.y[i], force_x, 1)
            # force in y-direction
            force_y = fluid_prop.sigma*(tan_y[i]-tan_y[i-1]);
            self.distribute_lagrangian_to_eulerian(
                domain, face.force_y, self.x[i], self.y[i], force_y, 2)

    @staticmethod
    def distribute_lagrangian_to_eulerian(domain, cell, x, y, value, axis):
        """ 
        Distribute a value from a lagrangian point to neighboring eulerian cells.
        """
        # assign the grid size
        if (axis == 1):      # x-dir
            d1 = domain.dx;
            d2 = domain.dy;           
        else:                # y-dir
            d1 = domain.dy;
            d2 = domain.dx;   

    	# get the eulerian cell indices
        [index_x, index_y] = domain.get_cell_index(x, y, axis)
    	# calculate the weighing coefficients
        [coeff_x, coeff_y] = domain.get_weight_coeff(x, y, index_x, index_y, axis) 
        # distribute the force to the surrounding eulerian cells
        cell[index_x  ,index_y  ] = cell[index_x  ,index_y  ] + \
            (1.0-coeff_x)*(1.0-coeff_y)*value/d1/d2;
        cell[index_x+1,index_y  ] = cell[index_x+1,index_y  ] + \
            coeff_x*(1.0-coeff_y)*value/d1/d2;
        cell[index_x  ,index_y+1] = cell[index_x  ,index_y+1] + \
            (1.0-coeff_x)*coeff_y*value/d1/d2;      
        cell[index_x+1,index_y+1] = cell[index_x+1,index_y+1] + \
            coeff_x*coeff_y*value/d1/d2
            
    def update_front_location(self, face, param, domain):
        """
        Advect the location of marker points using the interpolated velocity field.
        """
        # interpolate the velocity from the eulerian grid to the location of marker point
        u_x = np.zeros(self.point+2)
        u_y = np.zeros(self.point+2)
        for i in range(1, self.point+1):
            # interpolate velocity in x-direction
            u_x[i] = self.interpolate_velocity(domain, face.u, self.x[i], self.y[i], 1)
            # interpolate velocity in y-direction
            u_y[i] = self.interpolate_velocity(domain, face.v, self.x[i], self.y[i], 2)
    
    	# advect the marker point 
        for i in range(1, self.point+1):
            self.x[i] = self.x[i]+param.dt*u_x[i]
            self.y[i] = self.y[i]+param.dt*u_y[i]
        self.x[0] = self.x[self.point];
        self.y[0] = self.y[self.point];
        self.x[self.point+1] = self.x[1];
        self.y[self.point+1] = self.y[1]; 
    
    @staticmethod
    def interpolate_velocity(domain, face_vel, x, y, axis):
        """
        Interpolate velocities located on eulerian cells to a lagrangian marker
        point.
        """
        # get the eulerian cell index
        [index_x, index_y] = domain.get_cell_index(x, y, axis)
        # calculate the weighing coefficient
        [coeff_x, coeff_y] = domain.get_weight_coeff(x, y, index_x, index_y, axis)
        # interpolate the surrounding velocities to the marker location
        vel = (1.0-coeff_x)*(1.0-coeff_y)*face_vel[index_x  ,index_y  ]+ \
                   coeff_x *(1.0-coeff_y)*face_vel[index_x+1,index_y  ]+ \
              (1.0-coeff_x)*     coeff_y *face_vel[index_x  ,index_y+1]+ \
                   coeff_x *     coeff_y *face_vel[index_x+1,index_y+1]      
        
        return vel
    
    def restructure_front(self, domain):
        """
        Restructure the front to maintain the quality of the interface.
        """
        self.x_old = self.x
        self.y_old = self.y
        j = 0
        print(self.point)
        for i in range(1, self.point+1):
            # check the distance
            dst = math.sqrt(((self.x_old[i]-self.x[j])/domain.dx)**2 +
                            ((self.y_old[i]-self.y[j])/domain.dy)**2)
            if (dst > 0.5):         # too big
             	# add marker points
                j = j+1
                self.x[j] = 0.5*(self.x_old[i]+self.x[j-1])
                self.y[j] = 0.5*(self.y_old[i]+self.y[j-1])
                j = j+1
                self.x[j] = self.x_old[i]
                self.y[j] = self.y_old[i]
            elif (dst >= 0.25) and (dst <= 0.5):
                j = j+1
                self.x[j] = self.x_old[i]
                self.y[j] = self.y_old[i]
        self.point = j;
        self.x[0] = self.x[self.point];
        self.y[0] = self.y[self.point];
        self.x[self.point+1] = self.x[1];
        self.y[self.point+1] = self.y[1];