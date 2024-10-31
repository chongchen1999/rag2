import os
import hashlib

PERSISTENT_UPLOAD_DIR = "../uploaded_files"  # Persistent directory to store uploaded files

def handle_file_upload(uploaded_files):
    """Store uploaded files in a persistent directory if they don't already exist."""
    if uploaded_files:
        # Ensure the persistent directory exists
        if not os.path.exists(PERSISTENT_UPLOAD_DIR):
            os.makedirs(PERSISTENT_UPLOAD_DIR)

        # Generate a unique directory name based on file hash
        files_hash = get_files_hash(uploaded_files)
        upload_dir = os.path.join(PERSISTENT_UPLOAD_DIR, files_hash)

        # Create the directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)

        # Save each file only if it does not already exist in the directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(upload_dir, uploaded_file.name)
            
            # Calculate file hash to check for duplicates
            file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()
            
            # If the file already exists, skip writing it to disk
            if os.path.exists(file_path):
                existing_file_hash = calculate_file_hash(file_path)
                if existing_file_hash == file_hash:
                    print(f"File '{uploaded_file.name}' already exists. Skipping upload.")
                    continue
            
            # Save the file if it's not a duplicate
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
        
        return upload_dir
    return None

def get_files_hash(files):
    """Calculate MD5 hash for uploaded files to create a unique identifier."""
    hash_md5 = hashlib.md5()
    for file in files:
        file_bytes = file.read()
        hash_md5.update(file_bytes)
        file.seek(0)  # Reset file pointer for reuse
    return hash_md5.hexdigest()

def calculate_file_hash(file_path):
    """Calculate MD5 hash of a file on disk."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
