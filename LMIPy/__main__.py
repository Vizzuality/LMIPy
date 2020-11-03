import argparse

from LMIPy import Table
from table_validators import validate_table
from pkg_resources import get_distribution

__version__ = get_distribution('LMIPy').version

def main():
    parser = argparse.ArgumentParser(prog='LMIPy')
    parser.add_argument("function", help="function to run", type=str, choices=['validate'])
    parser.add_argument("-p", "--path", help="relative path of ids_json", type=str, nargs=1)
    parser.add_argument("-t", "--type", help="entity type", type=str, choices=['layer', 'table', 'dataset'], nargs=1)
    parser.add_argument("-i", "--id", help="entity id", type=str, nargs=1)
    parser.add_argument("-s", "--slug", help="entity slug for determining type", type=str, nargs=1)
    
    args = parser.parse_args()
    print(args)

    if args.function == 'validate' and args.slug and args.id:
        validate_table(args.id[0], args.slug[0])

if __name__ == "__main__":
    main()

