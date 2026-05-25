from tensorflow import keras
from tensorflow.keras import layers, regularizers


# Build LSTM model for music generation
# Creates a 3-layer LSTM architecture with dropout and batch normalization
# Parameters: seq_length (sequence length), n_vocab (vocabulary size)
# Returns: Compiled Keras model ready for training
def build_lstm_model(seq_length: int, n_vocab: int) -> keras.Model:
    """
    Build a professional LSTM model for sequential note prediction.
    
    Architecture:
    - 3 LSTM layers (512, 512, 256 units) to capture musical patterns at different levels
    - Dropout layers to prevent overfitting
    - Batch normalization for stable training
    - Dense layers for final prediction
    
    Args:
        seq_length: Length of input note sequences
        n_vocab: Size of vocabulary (number of unique notes)
    
    Returns:
        Compiled Keras model ready for training
    """
    l2_reg = regularizers.l2(0.001)
    
    model = keras.Sequential([
        # First LSTM layer: Extract low-level patterns
        layers.LSTM(512, input_shape=(seq_length, 1), return_sequences=True, 
                   kernel_regularizer=l2_reg),
        layers.Dropout(0.25),
        layers.BatchNormalization(),
        
        # Second LSTM layer: Extract mid-level patterns and themes
        layers.LSTM(512, return_sequences=True, 
                   kernel_regularizer=l2_reg),
        layers.Dropout(0.25),
        layers.BatchNormalization(),
        
        # Third LSTM layer: Extract high-level structure
        layers.LSTM(256, return_sequences=False, 
                   kernel_regularizer=l2_reg),
        layers.Dropout(0.25),
        layers.BatchNormalization(),
        
        # Dense layers for prediction
        layers.Dense(256, activation="relu", kernel_regularizer=l2_reg),
        layers.Dropout(0.2),
        layers.Dense(128, activation="relu", kernel_regularizer=l2_reg),
        layers.Dropout(0.15),
        layers.Dense(n_vocab, activation="softmax")
    ], name="professional_music_lstm")

    optimizer = keras.optimizers.Adam(learning_rate=0.001, clipnorm=1.0)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model
