import sys
from locality import utils, generate_masks

FCLASSES_WATER = [
    "water",
    "reservoir",
    "river",
    "dock",
    "riverbank",
    None
]

def transform(df):
    return utils.filter_by_fclass(df, FCLASSES_WATER)

def main():

    n_args = len(sys.argv)
    if n_args < 3:
        print("Wrong numbers of args")
        return

    dir_in = sys.argv[1]
    dir_out = sys.argv[2]

    generate_masks.generate_masks(
        dir_in, 
        dir_out, 
        transform,
        offset_half=True,
        all_touched=True
    )

if __name__ == "__main__":
    main()