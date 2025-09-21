# train_pest_model.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

# --- 1. Setup Data Paths ---
base_dir = 'pest_img_data'

# --- 2. Image Preprocessing ---
image_generator = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_generator = image_generator.flow_from_directory(
    base_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='training'
)

validation_generator = image_generator.flow_from_directory(
    base_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical',
    subset='validation'
)

# --- 3. Build the Model ---
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
num_classes = len(train_generator.class_indices)
predictions = Dense(num_classes, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)

# --- 4. Compile and Train ---
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
print("\n--- Starting Model Training for Pest/Disease Detection ---")
model.fit(train_generator, epochs=5, validation_data=validation_generator)
print("✅ Model training complete.")

# --- 5. Save the Model ---
model.save('models/pest_classifier_model.h5')
print("\n✅ Model saved as 'pest_classifier_model.h5'")