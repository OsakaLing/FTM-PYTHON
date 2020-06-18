"""
A two-dimensional gas-liquid multiphase flows using a front-tracking type
method. A set of Navier-Stokes equation is solved on a eulerian grid 
using a second order projection method. The fluid properties are advected 
by lagrangian marker points. The time marching is second order by using 
predictor-corrector method. The code can be used to simulate a bubble 
rising in a rectangular box.
Created by: Haryo Mirsandi
"""

# import
from io_manager import create_dir, clean_dir

# clean output folder
create_dir('output')
clean_dir('output','bub*.png')
    
# read input file


# initialization

# initialize variables (grid, velocity, pressure, and force)

# initialize the physical properties

# set the initial front (gas-liquid interface)

# start time-loop

# visualize the initial condition

# time loop
    # store second order variables
        # calculate the surface tension force at the front (lagrangian grid)
        # and distribute it to eulerian grid

        # update the tangential velocity at boundaries

        # calculate the (temporary) velocity

        # solve pressure
        
        # correct the velocity by adding the pressure gradient
        
        # update the front location 

        # update physical properties
  
    # end
    # store second order variables
    
    # restructure the front
    
    # visualize the results

 # end time-loop

