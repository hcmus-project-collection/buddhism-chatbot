import gdown


def download_embeddings(embedding_url: str, output_path: str):
    gdown.download_folder(embedding_url, output=output_path, quiet=False, use_cookies=False)


if __name__ == "__main__":
    # Example usage
    embedding_url = "https://drive.google.com/drive/folders/10LVJBULAaeVg7EaZsJSmUyMnLnODdxT8"
    output_path = "./jsonl/embeddings"

    download_embeddings(embedding_url, output_path)
    print(f"Embeddings downloaded to: {output_path}")
