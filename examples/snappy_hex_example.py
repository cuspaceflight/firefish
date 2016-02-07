import os

from firefish.case import Case

def main(case_dir='snappy'):
    #Create a new case file, raise an error if the directory already exists
    case = create_new_case(case_dir)
    
def create_new_case(case_dir):
    # Check that the specified case directory does not already exist
    if os.path.exists(case_dir):
        raise RuntimeError(
            'Refusing to write to existing path: {}'.format(case_dir)
        )

    # Create the case
    return Case(case_dir)