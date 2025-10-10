import pandas as pd
import os
import glob

def find_matching_csv(directory):
    """
    Iterates through CSV files in a directory to find a row where 'choice_id' is not 0 and 'not_included_links' is not 0.

    Args:
        directory (str): The path to the directory containing the CSV files.

    Returns:
        str: The name of the first CSV file where the condition is met, or None if no such file is found.
    """
    # Use glob to get a list of all CSV files in the directory
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    not_included_count=0
    if not csv_files:
        print(f"No CSV files found in the directory: {directory}")
        return None

    for csv_file_path in csv_files:
        # Extract the filename from the full path
        csv_file_name = os.path.basename(csv_file_path)
        try:
            # Read the CSV file into a pandas DataFrame
            df = pd.read_csv(csv_file_path)

            # Check if the required columns exist
            if 'choice_id' not in df.columns or 'not_included_links' not in df.columns:
                print(f"Error: CSV file '{csv_file_name}' is missing one or both of the required columns ('choice_id', 'not_included_links'). Skipping this file.")
                continue  # Skip to the next CSV file

            # Check for the condition: 'choice_id' != 0 and 'not_included_links' != 0
            if df['not_included_links'].sum()>1:
                not_included_count +=1


        except pd.errors.EmptyDataError:
            print(f"Error: CSV file '{csv_file_name}' is empty. Skipping this file.")
            continue  # Skip to the next CSV file
        except Exception as e:
            print(f"Error reading CSV file '{csv_file_name}': {e}")
            continue # Skip to the next file

    print(f"{not_included_count} trajectories with missing links")
    return None  # Return None if no matching row is found in any file

if __name__ == "__main__":
    # Specify the directory containing the CSV files
    directory_path = "choice_properties/backup"  # Replace with the actual path if needed

    # Call the function to find the matching CSV file
    find_matching_csv(directory_path)

