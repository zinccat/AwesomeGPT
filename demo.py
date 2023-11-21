import streamlit as st
# import pandas as pd
import re
from pipeline import process
from urllib.parse import urlparse
import json

def extract_github_repo(url):
    """
    Extracts user and repository name from a given GitHub URL.

    Args:
    url (str): A URL to check and extract information from.

    Returns:
    tuple: A tuple containing the username and repository name if the URL is a valid GitHub repository URL, None otherwise.
    """
    # Check if the URL is valid
    try:
        parsed_url = urlparse(url)
    except Exception as e:
        print(f"Invalid URL: {e}")
        return None

    # Check if the domain is github.com
    if parsed_url.netloc != 'github.com':
        return None

    # Extract the path and split into parts
    path_parts = parsed_url.path.strip("/").split("/")
    
    # Check if path has at least 2 parts (username and repo)
    if len(path_parts) >= 2:
        username, repo_name = path_parts[0], path_parts[1]
        return (username, repo_name)
    else:
        return None

# Streamlit interface
def main():
    st.title("Awesome Repo Processor")

    # User input for GitHub repository
    github_repo_url = st.text_input("Enter the GitHub repository URL:")

    if github_repo_url:
        ret = extract_github_repo(github_repo_url)
        if ret is None:
            st.error("Invalid GitHub repository URL")
        else:
            username, repo = ret
            st.success(f"Valid GitHub repository URL: {username}/{repo}")
            # Process the GitHub repository
            try:
                with st.spinner("Processing..."):
                    processed_data = process(username, repo)
                st.success("Processing complete!")
                # change dict to binary
                processed_data = json.dumps(processed_data)
                st.download_button(
                    "Download!",
                    data=processed_data,
                    file_name=f"{username}-{repo}.json",
                    mime="application/json"
                )
            except Exception as e:
                processed_data = {}
                st.error(e)
            

if __name__ == "__main__":
    main()
