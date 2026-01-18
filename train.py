import os
import pickle

import numpy as np
import tensorflow
from numpy.linalg import norm
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input  # type: ignore
from tensorflow.keras.layers import GlobalMaxPooling2D  # type: ignore
from tensorflow.keras.preprocessing import image  # type: ignore
from tqdm import tqdm


def build_model():
    base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False
    model = tensorflow.keras.Sequential([
        base_model,
        GlobalMaxPooling2D(),
    ])
    return model


def extract_features(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    result = model.predict(preprocessed_img).flatten()
    normalized_result = result / norm(result)
    return normalized_result


def main(images_dir: str = "images") -> None:
    if not os.path.isdir(images_dir):
        raise FileNotFoundError(f"Images directory not found: {images_dir}")

    model = build_model()

    filenames = []
    for file in os.listdir(images_dir):
        file_path = os.path.join(images_dir, file)
        if os.path.isfile(file_path):
            filenames.append(file_path)

    feature_list = []
    for file in tqdm(filenames, desc="Extracting features"):
        feature_list.append(extract_features(file, model))

    pickle.dump(feature_list, open("embeddings.pkl", "wb"))
    pickle.dump(filenames, open("filenames.pkl", "wb"))


if __name__ == "__main__":
    main()