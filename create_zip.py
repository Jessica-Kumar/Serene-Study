import zipfile
import os

def zip_project(output_filename="Mental_Health_Analyzer.zip"):
    # Files/Dirs to exclude
    EXCLUDE_DIRS = {'.git', '__pycache__', '.streamlit', 'venv', 'env', '.idea', '.vscode'}
    EXCLUDE_FILES = {'firebase_key.json', output_filename, '.DS_Store'}
    
    # Specific file inside .streamlit to exclude, but we might want to include config.toml
    # actually, we should include .streamlit/config.toml but NOT .streamlit/secrets.toml
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES:
                    continue
                
                file_path = os.path.join(root, file)
                
                # Double check for secrets
                if "secrets.toml" in file_path:
                    continue
                if "firebase_key.json" in file_path:
                    continue
                    
                print(f"Adding {file_path}")
                zipf.write(file_path, arcname=os.path.relpath(file_path, "."))
                
        # Manually add .streamlit/config.toml if it exists
        if os.path.exists(".streamlit/config.toml"):
             print(f"Adding .streamlit/config.toml")
             zipf.write(".streamlit/config.toml", arcname=".streamlit/config.toml")

if __name__ == "__main__":
    zip_project()
    print("Zip creation complete!")
