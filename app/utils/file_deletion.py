import os

def delete_buffer_files(folder_path):
    # Check if the folder exists
    if not os.path.isdir(folder_path):
        print(f"The folder '{folder_path}' does not exist.")
        return


    for filename in os.listdir(folder_path):
        if filename.startswith("buffer"):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                return

    print("No files starting with 'buffer' were found.")

# Example usage
if __name__ == "__main__":
    ...