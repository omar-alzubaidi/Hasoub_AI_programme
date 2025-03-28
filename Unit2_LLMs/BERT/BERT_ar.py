import os
import numpy as np
import pandas as pd
import ktrain
from ktrain import text
import time


def train_and_save_model(train_data_path, model_save_path):
    # Load  dataset
    df = pd.read_csv(train_data_path, sep='\t')  # Assuming TSV file

    # Splitting data into training and testing
    x_train = df['text'][:80000].to_numpy()
    y_train = df['label'][:80000].to_numpy()
    x_test = df['text'][80000:].to_numpy()
    y_test = df['label'][80000:].to_numpy()

    # Define the model name and categories
    MODEL_NAME = 'bert-base-uncased'
    categories = ['Mixed', 'Negative', 'Positive']

    # Load and preprocess data
    t = text.Transformer(MODEL_NAME, maxlen=200, class_names=categories)
    trn = t.preprocess_train(x_train, y_train)
    val = t.preprocess_test(x_test, y_test)

    # Build and train the model
    model = t.get_classifier()
    learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=16)

    start = time.time()
    learner.fit_onecycle(2e-5, 4)
    stop = time.time()
    print(f"Training time: {stop - start}s")

    # Validate the model
    learner.validate(class_names=categories)

    # Save the model
    predictor = ktrain.get_predictor(learner.model, preproc=t)
    predictor.save(model_save_path)
    print(f"Model saved successfully at: {model_save_path}")


def load_and_predict(model_path, texts):
    # Load the model
    predictor = ktrain.load_predictor(model_path)

    # Make predictions
    predictions = predictor.predict(texts)

    # Print predictions
    print(f"Predictions: {predictions}")
    return predictions


if __name__ == "__main__":
    # Define file paths
    train_data_path = 'ar_reviews_100k.tsv'  # Make sure this file is in the same directory
    model_save_path = 'FineTuned_Arabic_Sentiment_BERT'

    # Train and save the model
    train_and_save_model(train_data_path, model_save_path)

    # Example of using the model for prediction
    sample_texts = ["اقروا الله فينا يكفي رفع اسعار الرواتب بالتطبيق", "كله رائع جدا ربنا يكرمك"]
    load_and_predict(model_save_path, sample_texts)
