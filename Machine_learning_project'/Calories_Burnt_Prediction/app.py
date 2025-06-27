from flask import Flask, render_template, request
import numpy as np
import pickle

app = Flask(__name__)
## Load the model
try:
    with open('trained_model.sav', 'rb') as file:
        model = pickle.load(file)
except EOFError:
    print("The file is empty or does not exist. Please make sure the file exists and has data in it.")
except Exception as e:
    print(f"An error occurred: {e}")  
else:
    # code that uses the model only if it was successfully loaded
    print(model) 

@app.route('/',methods=['GET'])
def Home():
    return render_template('index.html')

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        age = float(request.form['age'])
        Gender = request.form['sex']
        if (Gender == 'male'):
            Gender = 0
        else:
            Gender = 1
        Height = float(request.form['height'])
        Weight = float(request.form['weight'])
        Duration = float(request.form['duration'])
        Heart_Rate = float(request.form['Heart_Rate'])
        Body_Temp = float(request.form['Body_Temp'])
  
        values = np.array([[Gender,age,Height,Weight,Duration,Heart_Rate,Body_Temp]])
        prediction = model.predict(values)
        prediction = round(prediction[0],2)
    

        return render_template('index.html', prediction_text='Calories Burnt is {}'.format(prediction))





if __name__ == "__main__":
    app.run(debug=True)