import os

def check_dir(path):
    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created.")
    else:
        print(f"Directory '{path}' already exists.")

def level_of_effort(slope, length): #given a slope and length of a link, what is the level of effort according to scale from 'Slope stress criteria as a complement to traffic stress criteria, and impact on high comfort bicycle accessibility'
    loe = 0
    if length<150:
        if slope<0.065:
            return 1
        elif slope<0.08:
            return 2
        elif slope<0.095:
            return 3
        elif slope<0.11:
            return 4
        else:
            return 5
    elif length<500:
        if slope<0.05:
            return 1
        elif slope<0.065:
            return 2
        elif slope<0.08:
            return 3
        elif slope<0.095:
            return 4
        else:
            return 5
    else:
        if slope<0.035:
            return 1
        elif slope<0.05:
            return 2
        elif slope<0.065:
            return 3
        elif slope<0.08:
            return 4
        else:
            return 5
 