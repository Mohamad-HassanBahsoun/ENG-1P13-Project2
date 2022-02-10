
import time
import random
import sys
sys.path.append('../')

from Common_Libraries.p2_lib import *

import os
from Common_Libraries.repeating_timer_lib import repeating_timer

def update_sim ():
    try:
        arm.ping()
    except Exception as error_update_sim:
        print (error_update_sim)

arm = qarm()

update_thread = repeating_timer(2, update_sim)


## STUDENT CODE BEGINS
## ----------------------------------------------------------------------------------------------------------
home_position = [0.4064,0.0,0.4826]
container_location = [0.4918, 0.0, 0.0062]
# Used to check if a container has already been spawned/used
container_list = [1,2,3,4,5,6]
threshold = 0.50


# execute is what allows the while loop in the main to run
execute = True


# gripper_close is a failsafe, This ensures that the user correctly functions the EMG
# This will not allow the user to move to drop off location unless True
gripper_close = False


# drawer_open checks if the drawer is open or not. This ensures that the user correctly functions the EMG
# This will not allow the user to close the drawer until it is True
drawer_open = False


# autoclave_Bins_access checks if we are allowed access the autoclave_Bins function, This also allows the user to make
# a mistake, without ruining functionality 
autoclave_Bins_access = False


# move_end_effector_access checks if we are allowed access the move_end_effector function, This also allows the user to make
# a mistake, without ruining functionality
move_end_effector_access = True


# control_gripper_access checks if we are allowed access the control_gripperfunction, This allows the user to make
# a mistake, without ruining functionality
control_gripper_access = False

#---------------------------------------------------------------------------------------------------------------------------------------------

# autoclaveLocations(iD) is what contains the locations of the autoclave positions (Top, and Drawer)
# Container ID is input that is passed to the function (parameter iD) it will return the location as a list
def autoclaveLocations(iD):
    if iD == 1:
        """
        Small, Red Container Location
        """
        location = [-0.6012, 0.2429, 0.3658]
    elif iD == 2:
        """
        Small, Green Container Location
        """
        location = [0.0,-0.6484,0.3658]
    elif iD == 3:
        """
        Small, Blue Container Location
        """
        location = [0.0, 0.6484, 0.3658]
    elif iD == 4:
        """
        Large, Red Container Location
        """
        location = [-0.359, 0.1599, 0.2967]
    elif iD == 5:
        """
        Large, Green Container Location
        """
        location = [0.0, -0.3895, 0.2882]
    elif iD == 6:
        """
        Large, Blue Container Location
        """
        location = [0.0, 0.4001, 0.2929]
    return location

#---------------------------------------------------------------------------------------------------------------------------------------------

# autoclave_Bins(iD) will take the container ID as input and will open the coresponding autoclave drawer if the variable drawer_open is false
# When drawer_open is true, the function will be able to close the autoclave drawers

def autoclave_Bins(iD):
    global drawer_open
    global execute
    global autoclave_Bins_access
    global control_gripper_access
    global move_end_effector_access

    while autoclave_Bins_access:
        if drawer_open == False:
            if ((arm.emg_left() == 0) and (0 != arm.emg_right() < threshold)):
                if iD == 4:
                    arm.open_red_autoclave(True)
                    drawer_open = True
                    gripper_close= False
                    control_gripper_access = True
                    autoclave_Bins_access = False
                    """
                    -drawer_open is true, thus we are not allowed to access this part of the function
                    -gripper_close is now false which will prevent the user from moving to a different autoclave loaction (prevents user error)
                    -control_gripper_access is now true which allows us to drop the container in the autoclave bin
                    -autoclave_Bins_access is now false which takes us out of the function
                    """
                elif iD == 5:
                    arm.open_green_autoclave(True)
                    drawer_open = True
                    gripper_close= False
                    control_gripper_access = True
                    autoclave_Bins_access = False
                elif iD == 6:
                    arm.open_blue_autoclave(True)
                    drawer_open = True
                    gripper_close= False
                    control_gripper_access = True
                    autoclave_Bins_access = False

        if drawer_open:
            if ((arm.emg_left() == 0) and (arm.emg_right() > threshold)):
                if iD == 4:
                    arm.open_red_autoclave(False)
                    time.sleep(1)
                    arm.home()
                    drawer_open = False
                    move_end_effector_access = True
                    autoclave_Bins_access = False
                    execute = False
                    """
                    -After closing the drawer we return home, and and resume the cycle
                    -drawer_open is now false becasue the drawer is now closed, and when the cycle returns, we have to open the drawer first
                    -move_end_effector_access is now true. In the next cycle we can now access move_end_effector
                    -Autoclave_Bins_access is now false which takes us out of the function
                     we now exit the while loop in the main function
                    """
                elif iD == 5:
                    arm.open_green_autoclave(False)
                    time.sleep(1)
                    arm.home()
                    drawer_open = False
                    move_end_effector_access = True
                    autoclave_Bins_access = False
                    execute = False
                elif iD == 6:
                    arm.open_blue_autoclave(False)
                    time.sleep(1)
                    arm.home()
                    drawer_open = False
                    move_end_effector_access = True
                    autoclave_Bins_access = False
                    execute = False
                
#---------------------------------------------------------------------------------------------------------------------------------------------

# spawn_container() is used to spawn a container, it will check if the integer is in the pre-created list
# if it is it will spawn a container and remove that value from the list. The functions returns the container_ID that was generated
# and the length of the list which will be used to check if the main should terminate or not

def spawn_container():
    global container_list
    container_ID = random.randint(1,6)
    list_length = len(container_list)
    if container_ID in container_list:
        if container_list:
            arm.spawn_cage(container_ID)
            container_list.remove(container_ID)
    else:
        container_ID = 0
        """
        if an integer is generated more than once, container_ID will now be assigned 0, which
        affects how the main operates
        """
    return [container_ID, list_length]


#---------------------------------------------------------------------------------------------------------------------------------------------

# control_gripper(i) is used to control the gripper, it will either open or close the gripper
def control_gripper(iD):
    global gripper_close
    global autoclave_Bins_access
    global execute
    global control_gripper_access
    global move_end_effector_access
    
    while control_gripper_access:
        if ((arm.emg_left() > threshold) and (arm.emg_right() == 0)):
            time.sleep(1)
            arm.control_gripper(45)
            gripper_close = True
            time.sleep(1)
            arm.move_arm(home_position[0],home_position[1],home_position[2])
            time.sleep(1)
            move_end_effector_access = True
            control_gripper_access = False
            """
            -After picking up the container gripper_close is True
             allowing us to move to the drop off location
            -move_end_effector_access is now true allowing us to enter the move_end _effector function
            - once control_gripper_access is assigned false, the control_gripper function no longer runs
            """
            

        elif((0 != arm.emg_left() < threshold) and (arm.emg_right() == 0)):
            time.sleep(1)
            arm.control_gripper(-45)
            time.sleep(1)
            if iD == 1 or iD == 2 or iD == 3:
                arm.home()
                execute = False
                gripper_close= False
                move_end_effector_access = True
                control_gripper_access = False
                """
                -execute is now false, which exits the while loop in the main function
                -gripper close is now false. resets it back to what was originally declared
                -move_end_effector_access is now true. When the next cycle begins we can go to the container location
                -control_gripper_access is now false, the control_gripper function no longer runs
                """
            if iD == 4 or iD == 5 or iD == 6:
                autoclave_Bins_access = True
                control_gripper_access = False
                """
                -once we drop the container in the drawer we now have
                access to the autoclave_Bin function to close the drawer
                -control_gripper_access is now false, the control_gripper function no longer runs
                """
            time.sleep(1)
        else:
            break

        
#---------------------------------------------------------------------------------------------------------------------------------------------

# move_end_effector(iD,location) is used for moving the arm to specified drop off locations.
# loactions is passed so we may move to the appropriate atoclave locations, and iD aids
# in preventing user error
def move_end_effector(iD,location):
    global gripper_close
    global autoclave_Bins_access
    global move_end_effector_access
    global control_gripper_access

    while move_end_effector_access:
        if ((arm.emg_left() > threshold) and (arm.emg_right() > threshold)):
            time.sleep(1)
            arm.move_arm(container_location[0],container_location[1],container_location[2])
            time.sleep(1)
            control_gripper_access = True
            move_end_effector_access = False
            """
            -control_gripper_access is now true, allowing us to access the control_gripper function
            -move_end_effector_accessis now false, we exit the move_end effector function
            """

        if gripper_close== True:
            if ((0 != arm.emg_left() < threshold) and (0 != arm.emg_right() < threshold)):
                if(iD == 1 or iD == 2 or iD == 3):
                    time.sleep(1)
                    arm.move_arm(location[0],location[1],location[2])
                    time.sleep(1)
                    control_gripper_access = True
                    move_end_effector_access = False
                if(iD == 4 or iD == 5 or iD == 6):
                    time.sleep(1)
                    arm.move_arm(location[0],location[1],location[2])
                    time.sleep(1)
                    autoclave_Bins_access = True
                    """
                    Once we have moved to the drop off location, we now have
                    access to the autoclave_Bin function to open the drawer
                    """
                    move_end_effector_access = False
                    gripper_close= False

                
#--------------------------------------------------------------------------------------------------------------------------------------------

# main() is where the magic happens (brings everything together)
# The main is a form of recursion with, terminate == 0, as our base case (when terminate is 0 main exits),
# when the id is 0 that means that the continer has already been used, so we call the main and a new id is used.
# when the new id is not 0 we move on to continue the cycle by calling our predefined functions

def main():
    global execute
    container_iD, terminate = spawn_container()
    if terminate == 0:
        """
        -terminate is assigned to the length of the list, when the list is
        zero (when every container is spawned) the main will no longer run 
        """
        return
    else:
        if container_iD == 0:
            """
            -when the container_iD is zero we call the main again (recursion) and do nothing because that
            container has already been spawned
            """
            return main()
        else:
            location = autoclaveLocations(container_iD)
            execute = True
            while execute:
                move_end_effector(container_iD,location)
                control_gripper(container_iD)
                autoclave_Bins(container_iD)
    return main()



if __name__ == "__main__":
    main()

                


