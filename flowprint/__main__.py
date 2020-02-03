import argparse
import numpy as np

from flowprint import FlowPrint
from loader import Loader
from preprocessor import Preprocessor

if __name__ == "__main__":
    ########################################################################
    #                           Parse arguments                            #
    ########################################################################

    # Create argument parser
    parser = argparse.ArgumentParser(
                prog="flowprint.py",
                description="Flowprint: Semi-Supervised Mobile-App\nFingerprinting on Encrypted Network Traffic",
                formatter_class=argparse.RawTextHelpFormatter)

    # FlowPrint parameters
    group_flowprint = parser.add_argument_group("FlowPrint Parameters")
    group_flowprint.add_argument('-b', '--batch'      , type=float, default=300, help="batch size in seconds       (default=300)")
    group_flowprint.add_argument('-c', '--correlation', type=float, default=0.1, help="cross-correlation threshold (default=0.1)")
    group_flowprint.add_argument('-s', '--similarity' , type=float, default=0.9, help="similarity threshold        (default=0.9)")
    group_flowprint.add_argument('-w', '--window'     , type=float, default=30 , help="window size in seconds      (default=30)")

    # Data agruments
    group_data = parser.add_argument_group("Data input")
    group_data.add_argument('-f', '--files', nargs='+', help="path to pcap(ng) files to run through FlowPrint")
    group_data.add_argument('-r', '--read' , nargs='+', help="read preprocessed data from given files")
    group_data.add_argument('-t', '--write',            help="write preprocessed data to given file")

    # Set help message
    parser.format_help = lambda: \
"""usage: {} [-h]
                    [-b BATCH] [-c CORRELATION], [-s SIMILARITY], [-w WINDOW]
                    [-f FILES...] [-r READ...] [-t WRITE]

{}

Arguments:
  -h, --help                 show this help message and exit

FlowPrint parameters:
  -b, --batch       FLOAT    batch size in seconds       (default=300)
  -c, --correlation FLOAT    cross-correlation threshold (default=0.1)
  -s, --similarity  FLOAT    similarity threshold        (default=0.9)
  -w, --window      FLOAT    window size in seconds      (default=30)

Data input:
  FlowPrint requires at least one data source: --files or --read.
  -f, --files [PATH...]      path to pcap(ng) files to run through FlowPrint
  -r, --read  [PATH...]      read preprocessed data from given files
  -t, --write [PATH]         write preprocessed data to given file
 """.format(
    # Usage Parameters
    parser.prog,
    # Description
    parser.description)

    # Parse given arguments
    args = parser.parse_args()

    ########################################################################
    #                          Process input data                          #
    ########################################################################

    # Check if any input is given
    if not args.files and not args.read:
        # Give help message
        print(parser.format_help())
        # Throw exception
        raise RuntimeError("No input data provided, please specify --files or --read arguments.")

    # Initialise flows and labels
    X, y = list(), list()

    # Parse files - if necessary
    if args.files:
        # Initialise preprocessor
        preprocessor = Preprocessor(verbose=True)
        # Process data
        X_, y_ = preprocessor.process(args.files, args.files)
        # Add data to datapoints
        X.append(X_)
        y.append(y_)

    # Load preprocessed data - if necessary
    if args.read:
        # Initialise loader
        loader = Loader()
        # Loop over all preprocessed files
        for infile in args.read:
            # Load each file
            X_, y_ = loader.load_file(infile)
            # Add input file to data
            X.append(X_)
            y.append(y_)

    # Concatenate datapoints
    X = np.concatenate(X)
    y = np.concatenate(y)

    # Write preprocessed data - if necessary
    if args.write:
        # Initialise preprocessor
        preprocessor = Preprocessor(verbose=True)
        # Save data
        preprocessor.save(args.write, X, y)

    ########################################################################
    #                            Run FlowPrint                             #
    ########################################################################

    # TODO