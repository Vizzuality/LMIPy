import argparse

from LMIPy import Table
from table_validators import validate_table, validate_tables
from pkg_resources import get_distribution

__version__ = get_distribution('LMIPy').version

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    parser = argparse.ArgumentParser(prog='LMIPy')
    parser.add_argument("function", help="function to run", type=str, choices=['validate_table'])
    parser.add_argument("-p", "--path", help="relative path of ids_json", type=str, nargs=1)
    parser.add_argument("-i", "--id", help="entity id", type=str, nargs=1)
    parser.add_argument("-s", "--slug", help="entity slug for determining type", type=str, nargs=1)
    parser.add_argument("-v", "--verbose", help="activate verbose mode", type=str2bool, nargs='?', const=True, default=False)
    
    args = parser.parse_args()

    if args.function == 'validate_table' and args.slug and args.id:
        validate_table(args.id[0], args.slug[0])
    elif args.function == 'validate_table' and args.path:
        validate_tables(args.path[0])
    else:
        print('invalid arguments')

if __name__ == "__main__":
    main()

