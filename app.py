from flask import Flask, render_template, request, jsonify
import os
from model import anemia_prediction_pipeline, extract_text_from_image

app = Flask(__name__)

# Set the upload folder for images
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded image
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Use the model to extract text from image (if needed)
    extracted_text = extract_text_from_image(file_path)
    if extracted_text is None:
        return jsonify({'error': 'Unsupported image format. Please upload a JPG or PNG file.'}), 400

    # Use the model to predict anemia
    result = anemia_prediction_pipeline(file_path)

    # Determine if anemia is detected
    anemia_detected = bool(result[1])  # Convert the result to a boolean value (True or False)

    # Additional information based on anemia prediction
    if anemia_detected:  # If anemia is detected
        additional_info = {
            "symptoms": [
                "Fatigue",
                "Weakness",
                "Shortness of breath",
                "Pale or yellowish skin",
                "Irregular heartbeats"
            ],
            "treatment": [
                "Iron supplements",
                "Vitamin B12 injections",
                "Folic acid supplements",
                "Eating iron-rich foods (e.g., spinach, red meat, beans)",
                "Treating underlying causes (e.g., infections, chronic diseases)"
            ],
            "diet": [
                "Iron-rich foods like leafy greens, lentils, and tofu",
                "Foods rich in vitamin C (e.g., oranges, strawberries) to help iron absorption",
                "Avoid tea or coffee during meals as they can hinder iron absorption"
            ],
            "exercise": [
                "Light physical activity to improve overall energy",
                "Yoga and stretching exercises to reduce fatigue",
                "Walking and aerobic exercises as tolerated"
            ],
            "advice": "Consult a healthcare professional for a detailed diagnosis and personalized treatment plan."
        }
    else:  # If anemia is not detected
        additional_info = {
            "message": "No signs of anemia detected. Maintain a healthy diet and regular check-ups."
        }

    # Return result and additional information as JSON
    return jsonify({
        'result': result[0],  # The prediction result
        'anemia_detected': anemia_detected,  # Whether anemia was detected (True/False)
        'additional_info': additional_info,  # Extra information like treatment, diet, etc.
        'message': 'Prediction successful'
    })



@app.route('/manual_entry', methods=['POST'])
def manual_entry():
    # Get the manually entered values from the form
    manual_data = {
        'Gender': request.form.get('Gender'),
        'Hemoglobin': request.form.get('Hemoglobin'),
        'MCV': request.form.get('MCV'),
        'MCH': request.form.get('MCH'),
        'MCHC': request.form.get('MCHC')
    }

    # Convert form data to the proper format
    preprocessed_values = preprocess_features(manual_data)

    # Use the model to predict anemia
    result = predict_anemia(preprocessed_values)

    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
