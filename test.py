import argparse
import pickle

import numpy as np
import tensorflow
from numpy.linalg import norm
from sklearn.neighbors import NearestNeighbors  # type: ignore
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input  # type: ignore
from tensorflow.keras.layers import GlobalMaxPooling2D  # type: ignore
from tensorflow.keras.preprocessing import image  # type: ignore


def load_model_and_features(
    embeddings_path: str = "embeddings.pkl",
    filenames_path: str = "filenames.pkl",
):
    feature_list = np.array(pickle.load(open(embeddings_path, "rb")))
    filenames = pickle.load(open(filenames_path, "rb"))

    base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False
    model = tensorflow.keras.Sequential([
        base_model,
        GlobalMaxPooling2D(),
    ])
    return model, feature_list, filenames


def extract_features(img_path: str, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result / norm(result)
    return normalized_result


def get_similar_images(query_image_path: str, n_neighbors: int = 6):
    model, feature_list, filenames = load_model_and_features()

    query_features = extract_features(query_image_path, model)
    neighbors = NearestNeighbors(n_neighbors=n_neighbors, algorithm="brute", metric="euclidean")
    neighbors.fit(feature_list)

    distances, indices = neighbors.kneighbors([query_features])
    return [filenames[idx] for idx in indices[0]]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find similar fashion images using precomputed embeddings.",
    )
    parser.add_argument("image_path", help="Path to the query image")
    parser.add_argument(
        "--top_k",
        type=int,
        default=6,
        help="Number of similar images to return (default: 6)",
    )

    args = parser.parse_args()

    similar_images = get_similar_images(args.image_path, n_neighbors=args.top_k)
    print("Similar images:")
    for path in similar_images:
        print(path)


if __name__ == "__main__":
    main()