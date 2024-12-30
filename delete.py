import os

def delete_file(filename):
    try:
        os.remove(filename)
        print(f"{filename} has been deleted successfully.")
    except FileNotFoundError:
        print(f"The file {filename} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_to_delete = "signals.json"
    delete_file(file_to_delete)
