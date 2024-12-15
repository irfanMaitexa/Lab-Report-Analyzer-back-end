

# # !sudo apt-get install -y tesseract-ocr
# # !pip install pytesseract pillow
# import pytesseract
# from PIL import Image
# import re
# import joblib

# import warnings
# warnings.filterwarnings("ignore")

# # OCR function to extract text from the image
# def extract_text_from_image(image_path):
#     # Open the image
#     img = Image.open(image_path)

#     # Use Tesseract to do OCR on the image
#     text = pytesseract.image_to_string(img)

#     return text
# def extract_values(text):
#     # Define patterns for the required fields
#     patterns = {
#         'Hemoglobin': r'Hemoglobin \(Hb\)\s+([\d.]+)',  # Extract Hemoglobin value
#         'MCV': r'Mean Corpuscular Volume \(MCV\)\s+([\d.]+)',  # Extract MCV value
#         'MCH': r'MCH\s+([\d.]+)',  # Extract MCH value
#         'MCHC': r'MCHC\.\s+([\d.]+)',  # Extract MCHC value
#         'Gender': r'Sex\s+:\s+(\w+)'  # Extract Gender
#     }

#     # Create a dictionary to store the extracted values
#     extracted_values = {}

#     # Loop through the patterns and search in the text
#     for key, pattern in patterns.items():
#         match = re.search(pattern, text)
#         if match:
#             extracted_values[key] = match.group(1)

#     return extracted_values
# def preprocess_features(report_features):
#     # Map 'Gender' to 0 for Male and 1 for Female (no default)
#     gender_mapping = {'Male': 0, 'Female': 1}
#     report_features['Gender'] = gender_mapping[report_features['Gender']]  # Assumes 'Male' or 'Female' is always present

#     # Convert string values to float, if possible
#     for key, value in report_features.items():
#         if isinstance(value, str):
#             try:
#                 report_features[key] = float(value)
#             except ValueError:
#                 pass  # If it can't be converted, leave it as is

#     # Reorder the dictionary to match the desired order
#     ordered_keys = ['Gender', 'Hemoglobin', 'MCH', 'MCHC', 'MCV']
#     ordered_report_features = {key: report_features[key] for key in ordered_keys if key in report_features}

#     return list(ordered_report_features.values())
# # Function to predict anemia using the trained model
# def predict_anemia(preprocessed_values, model_path='anemia_model.joblib'):
#     # Load the trained model from joblib file
#     model = joblib.load(model_path)

#     # Make the prediction (assuming binary classification)
#     prediction = model.predict([preprocessed_values])[0]

#     # Convert the prediction to a readable format
#     if prediction == 1:
#         return "Anemia detected \t താങ്കള്‍ക്ക് അനീമിയ ബാധിചിരുക്കുന്നു."
#     else:
#         return "No anemia detected \t താങ്കള്‍ക്ക് അനീമിയ ഇല്ല."
# # Main function to handle the entire process
# def anemia_prediction_pipeline(image_path, model_path='lra_rfmodel.joblib'):
#     # Step 1: Extract text from the image
#     extracted_text = extract_text_from_image(image_path)

#     # Step 2: Extract required values from the text
#     extracted_values = extract_values(extracted_text)

#     # Step 3: Preprocess the extracted values
#     preprocessed_values = preprocess_features(extracted_values)

#     # Step 4: Use the trained model to predict anemia
#     prediction_result = predict_anemia(preprocessed_values, model_path)

#     return prediction_result

import pytesseract
import re
import joblib
from PIL import Image, UnidentifiedImageError
import warnings

warnings.filterwarnings("ignore")

# Load model only once at the start
model = joblib.load('lra_rfmodel.joblib')

# OCR function to extract text from the image

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        # Process the image for text extraction
        text = pytesseract.image_to_string(img)
        return text
    except UnidentifiedImageError:
        print("UnidentifiedImageError: Cannot identify image file. Please use a supported format (e.g., JPG, PNG).")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def extract_values(text):
    # Define patterns for the required fields
    patterns = {
        'Hemoglobin': r'Hemoglobin \(Hb\)\s+([\d.]+)',  # Extract Hemoglobin value
        'MCV': r'Mean Corpuscular Volume \(MCV\)\s+([\d.]+)',  # Extract MCV value
        'MCH': r'MCH\s+([\d.]+)',  # Extract MCH value
        'MCHC': r'MCHC\.\s+([\d.]+)',  # Extract MCHC value
        'Gender': r'Sex\s+:\s+(\w+)'  # Extract Gender
    }
    
    # Create a dictionary to store the extracted values
    extracted_values = {}
    missing_values = []

    # Loop through the patterns and search in the text
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            extracted_values[key] = match.group(1)
        else:
            missing_values.append(key)

    return extracted_values, missing_values

def preprocess_features(report_features):
    # Map 'Gender' to 0 for Male and 1 for Female
    gender_mapping = {'Male': 0, 'Female': 1}
    report_features['Gender'] = gender_mapping.get(report_features['Gender'], 0)  # Default to 0 if gender is unknown

    # Convert string values to float
    for key, value in report_features.items():
        if isinstance(value, str):
            try:
                report_features[key] = float(value)
            except ValueError:
                pass

    # Reorder the dictionary to match the desired order
    ordered_keys = ['Gender', 'Hemoglobin', 'MCH', 'MCHC', 'MCV']
    ordered_report_features = {key: report_features[key] for key in ordered_keys if key in report_features}

    return list(ordered_report_features.values())

# Function to predict anemia using the pre-loaded model
def predict_anemia(preprocessed_values):
    # Make the prediction (assuming binary classification)
    prediction = model.predict([preprocessed_values])[0]

    # Convert the prediction to a readable format
    if prediction == 1:
        return "Anemia detected \t താങ്കള്‍ക്ക് അനീമിയ ബാധിചിരുക്കുന്നു.", True
    else:
        return "No anemia detected \t താങ്കള്‍ക്ക് അനീമിയ ഇല്ല.", False


# Main function to handle the entire process
def anemia_prediction_pipeline(image_path):
    # Step 1: Extract text from the image
    extracted_text = extract_text_from_image(image_path)

    # Step 2: Extract required values from the text
    extracted_values, missing_values = extract_values(extracted_text)

    # Check if any values are missing
    if missing_values:
        return None, missing_values  # Return None if any values are missing

    # Step 3: Preprocess the extracted values
    preprocessed_values = preprocess_features(extracted_values)

    # Step 4: Use the model to predict anemia
    prediction_result = predict_anemia(preprocessed_values)

    return prediction_result, None
