import pandas as pd
import argparse
import sys

def parse_arguments():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Load a .pkl file and display its contents.')
    
    # Required positional argument for the file path
    parser.add_argument('file_path', type=str, help='Path to the .pkl file')
    
    # Optional argument for specifying columns
    parser.add_argument(
        '--columns',
        type=str,
        nargs='+',
        help=(
            'Name(s) of the column(s) to display. '
            'Provide multiple columns separated by space or comma.'
        )
    )
    
    return parser.parse_args()

def main():
    # Parse the arguments
    args = parse_arguments()
    
    # Load the .pkl file
    try:
        data = pd.read_pickle(args.file_path)
    except FileNotFoundError:
        print(f"Error: The file '{args.file_path}' does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading the file: {e}")
        sys.exit(1)
    
    # Display general information about the DataFrame
    print("\n--- DataFrame Information ---")
    print(data.info())
    
    print("\n--- First 5 Rows ---")
    print(data.head())
    
    print("\n--- Column Names ---")
    print(data.columns.tolist())
    
    # If columns are specified, display them
    if args.columns:
        # Flatten the list in case of comma-separated inputs
        columns = []
        for col in args.columns:
            columns.extend(col.split(','))  # Split by comma if needed
        
        # Remove any extra whitespace
        columns = [col.strip() for col in columns]
        
        # Check if specified columns exist in the DataFrame
        missing_cols = [col for col in columns if col not in data.columns]
        if missing_cols:
            print(f"\nError: The following columns are not in the DataFrame: {missing_cols}")
            sys.exit(1)
        
        # Select and display the specified columns
        column_data = data[columns]
        print(f"\n--- Specified Column Data ({', '.join(columns)}) ---")
        print(column_data)
    else:
        # If no columns specified, default to the two columns mentioned
        default_columns = ['weight_Pileup_up_yield', 'weight_Pileup_down_yield']
        missing_defaults = [col for col in default_columns if col not in data.columns]
        if missing_defaults:
            print(f"\nError: The default columns are missing from the DataFrame: {missing_defaults}")
            sys.exit(1)
        
        column_data = data[default_columns]
        print(f"\n--- Default Column Data ({', '.join(default_columns)}) ---")
        print(column_data)

if __name__ == '__main__':
    main()
