import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import re
from pathlib import Path

INPUT_DIR = Path("/usr/src/app/InputData")
OUTPUT_DIR = Path("/usr/src/app/output")
DATA_DIR = Path(".")

labels = {}


# Step 1: Load Data with Extended Text Extraction
def load_data(json_file_path):
    texts, labels, filenames = [], [], []  # Add filenames list
    with open(json_file_path, "r") as file:
        data_list = json.load(file)
        for data in data_list:
            text = ""
            if "event" in data:
                event = data["event"]
                text += " ".join(
                    [str(event.get(k, "")) for k in event if isinstance(event[k], str)]
                )
            if "file" in data:
                file_info = data["file"]
                text += " " + " ".join(
                    [
                        str(file_info.get(k, ""))
                        for k in file_info
                        if isinstance(file_info[k], str)
                    ]
                )
            if "message" in data:
                text += " " + data["message"]
            if "powershell" in data and "command" in data["powershell"]:
                ps_command = data["powershell"]["command"]
                text += (
                    " "
                    + str(ps_command.get("name", ""))
                    + " "
                    + " ".join(
                        [
                            str(inv.get("value", ""))
                            for inv in ps_command.get("invocation_details", [])
                        ]
                    )
                )

            label = data.get("label")
            filename = data.get("filename")  # Extract filename
            if label in [0, 1]:
                texts.append(clean_text(text))
                labels.append(label)
                filenames.append(filename)  # Add filename to the list
    return texts, labels, filenames


# Step 2: Text Cleaning
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r"\b\d+\b", "", text)  # Remove standalone numbers
    text = re.sub(r"\s+", " ", text)  # Remove extra whitespace
    return text.strip()


# Step 3: Preprocess and Train Model
def preprocess(texts, labels):
    # Use a pipeline to include TfidfVectorizer and classifier in one flow
    pipeline = Pipeline(
        [
            ("vectorizer", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("classifier", RandomForestClassifier(n_estimators=100, random_state=42)),
        ]
    )

    # Train the model on the data
    pipeline.fit(texts, labels)
    return pipeline


# Step 4: Evaluate the Model
def evaluate_model(model, X_test, y_test, texts_test, filenames_test):
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    # print("Classification Report:\n", classification_report(y_test, y_pred))

    # Print each test instance's actual vs. predicted label and the filename
    for i in range(len(y_test)):
        # print(
        #     f"Test Instance {i + 1}: Filename = {filenames_test[i]}, "
        #     f"Actual Label = {y_test[i]}, Predicted Label = {y_pred[i]}"
        # )
        labels[filenames_test[i]] = int(y_pred[i])

    # # Save files classified as label 1
    # classified_as_1 = [
    #     {"filename": filenames_test[i], "text": texts_test[i]}
    #     for i in range(len(y_pred)) if y_pred[i] == 1
    # ]
    # with open("classified_as_1.json", "w") as outfile:
    #     json.dump(classified_as_1, outfile, indent=4)


# Main Execution
train_file = "train.json"
test_file = "test.json"

# Load the data
train_texts, train_labels, train_filenames = load_data(train_file)
test_texts, test_labels, test_filenames = load_data(test_file)

# Print the number of training and test files
print(f"Number of training files: {len(train_filenames)}")
print(f"Number of test files: {len(test_filenames)}")

# Preprocess and train the model
model = preprocess(train_texts, train_labels)

# Evaluate the model with filenames
evaluate_model(model, test_texts, test_labels, test_texts, test_filenames)

(Path(OUTPUT_DIR) / "labels").write_text(json.dumps(labels))
