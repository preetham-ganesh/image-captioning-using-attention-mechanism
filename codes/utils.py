# authors_name = 'Preetham Ganesh'
# project_title = 'Captioning of Images using Attention Mechanism'
# email = 'preetham.ganesh2015@gmail.com'


import os
import sys

import tensorflow as tf
import pickle
import json
import numpy as np
import pandas as pd
import time

from bahdanau_attention_model import Encoder
from bahdanau_attention_model import BahdanauDecoder1
from bahdanau_attention_model import BahdanauDecoder2
from bahdanau_attention_model import BahdanauDecoder3
from luong_attention_model import LuongDecoder1
from luong_attention_model import LuongDecoder2
from luong_attention_model import LuongDecoder3


def load_json_file(directory_path: str,
                   file_name: str) -> dict:
    """Loads a JSON file into memory based on the file_name:

    Args:
        file_name: Current name of the dataset split used to load the corresponding JSON file.
        directory_path: Path where the file needs to be saved.

    Returns:
        Loaded JSON file.
    """
    file_path = '{}/{}.json'.format(directory_path, file_name)
    with open(file_path, 'r') as out_file:
        captions = json.load(out_file)
    out_file.close()
    return captions


def save_pickle_file(file: np.ndarray or dict,
                     directory_path: str,
                     file_name: str) -> None:
    """Saves NumPy array or Dictionary into pickle file for future use.

    Args:
        file: NumPy array or dictionary which needs to be saved.
        directory_path: Path where the file needs to be saved.
        file_name: Name by which the given file should be saved.

    Returns:
        None.
    """
    file_path = '{}/{}.pkl'.format(directory_path, file_name)
    with open(file_path, 'wb') as in_file:
        pickle.dump(file, in_file, protocol=2)
    in_file.close()


def save_json_file(file: dict,
                   directory_path: str,
                   file_name: str) -> None:
    """Saves dictionary into a JSON file for future use.

    Args:
        file: Dictionary which needs to be saved.
        directory_path: Path where the file needs to be saved.
        file_name: Name by which the given file should be saved.

    Returns:
        None.
    """
    file_path = '{}/{}.json'.format(directory_path, file_name)
    with open(file_path, 'w') as in_file:
        json.dump(file, in_file, indent=4)
    in_file.close()


def load_pickle_file(directory_path: str,
                     file_name: str) -> dict:
    """Loads a pickle file into memory based on the file_name:

    Args:
        file_name: Current name of the dataset split used to load the corresponding pickle file.
        directory_path: Path where the file needs to be saved.

    Returns:
        Loaded pickle file.
    """
    file_path = '{}/{}.pkl'.format(directory_path, file_name)
    with open(file_path, 'rb') as out_file:
        dictionary = pickle.load(out_file)
    out_file.close()
    return dictionary


def convert_dataset(dataset: dict) -> tuple:
    """Filters captions with length less than or equal to 40. Converts current datasets into 2 tensors for image ids and
    captions. Pads tensors for captions to ensure uniform size.

    Args:
        dataset: Image ids and captions for the current data split.

    Returns:
        A tuple which contains tensors for image ids and captions.
    """
    image_ids, captions = list(), list()
    for i in range(len(dataset['captions'])):
        # Checks if the length tokenized captions is less than or equal to 40.
        if len(dataset['captions'][i]) <= 40:
            image_ids.append(dataset['image_ids'][i])
            captions.append(dataset['captions'][i])
    # Converts modified list of image ids into a tensor.
    image_ids = tf.convert_to_tensor(image_ids)
    # Converts modified list of captions into a tensor, and pads 0 to the end of each item in the tensor if the length
    # is less than 40.
    captions = tf.keras.preprocessing.sequence.pad_sequences(captions, padding='post')
    return image_ids, captions


def check_directory_existence(directory_path: str,
                              sub_directory: str) -> str:
    """Concatenates directory path and sub_directory. Checks if the directory path exists; if not, it will create the
    directory.

    Args:
        directory_path: Current directory path
        sub_directory: Directory that needs to be checked if it exists or not.

    Returns:
        Newly concatenated directory path
    """
    directory_path = '{}/{}'.format(directory_path, sub_directory)
    # If the concatenated directory path does not exist then the sub directory is created.
    if not os.path.isdir(directory_path):
        os.mkdir(directory_path)
    return directory_path


def shuffle_slice_dataset(image_ids: tf.Tensor,
                          captions: tf.Tensor,
                          batch_size: int) -> tf.data.Dataset:
    """Combines the tensors for the image ids and captions, shuffles them and slices them based on batch size.

    Args:
        image_ids: Tensor which contains image ids for the current data split
        captions: Tensor which contains captions for the current data split.
        batch_size: Batch size for training the current model
    """
    dataset = tf.data.Dataset.from_tensor_slices((image_ids, captions)).shuffle(len(image_ids))
    dataset = dataset.batch(batch_size, drop_remainder=True)
    return dataset


def choose_encoder_decoder(parameters) -> tuple:
    """Uses attention and model number keys in the parameters, chooses the encoder and decoder model.

    Args:
        parameters: A dictionary which contains current model configuration details.

    Returns:
         A tuple which contains the objects for the encoder and decoder models
    """
    encoder = Encoder(parameters['embedding_size'], parameters['dropout_rate'])
    if parameters['attention'] == 'bahdanau_attention' and parameters['model_number'] == 1:
        decoder = BahdanauDecoder1(parameters['embedding_size'], parameters['rnn_size'],
                                   parameters['target_vocab_size'], parameters['dropout_rate'])
    elif parameters['attention'] == 'bahdanau_attention' and parameters['model_number'] == 2:
        decoder = BahdanauDecoder2(parameters['embedding_size'], parameters['rnn_size'],
                                   parameters['target_vocab_size'], parameters['dropout_rate'])
    elif parameters['attention'] == 'bahdanau_attention' and parameters['model_number'] == 3:
        decoder = BahdanauDecoder3(parameters['embedding_size'], parameters['rnn_size'],
                                   parameters['target_vocab_size'], parameters['dropout_rate'])
    elif parameters['attention'] == 'luong_attention' and parameters['model_number'] == 1:
        decoder = LuongDecoder1(parameters['embedding_size'], parameters['rnn_size'], parameters['dropout_rate'],
                                parameters['target_vocab_size'])
    elif parameters['attention'] == 'luong_attention' and parameters['model_number'] == 2:
        decoder = LuongDecoder2(parameters['embedding_size'], parameters['rnn_size'], parameters['dropout_rate'],
                                parameters['target_vocab_size'])
    elif parameters['attention'] == 'luong_attention' and parameters['model_number'] == 3:
        decoder = LuongDecoder3(parameters['embedding_size'], parameters['rnn_size'], parameters['dropout_rate'],
                                parameters['target_vocab_size'])
    else:
        print('Arguments for attention name or/and model number are not in the list of possible values.')
        print()
        sys.exit()
    return encoder, decoder


def loss_function(actual_values: tf.Tensor,
                  predicted_values: tf.Tensor) -> tf.Tensor:
    """Computes the loss value for the current batch of the predicted values based on comparison with actual values.

    Args:
        actual_values: Tensor which contains the actual values for the current batch.
        predicted_values: Tensor which contains the predicted values for the current batch.

    Returns:
        Loss for the current batch.
    """
    # Creates the loss object for the Sparse Categorical Crossentropy.
    loss_object = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True, reduction='none')
    # Performs element-wise equality comparison and returns the truth values.
    mask = tf.math.logical_not(tf.math.equal(actual_values, 0))
    # Computes loss for the current batch using actual values and predicted values.
    current_loss = loss_object(actual_values, predicted_values)
    # Converts mask into the type the current loss belongs to.
    mask = tf.cast(mask, dtype=current_loss.dtype)
    current_loss *= mask
    return tf.reduce_mean(current_loss)


@tf.function
def train_step(input_batch: tf.Tensor,
               target_batch: tf.Tensor,
               optimizer: tf.keras.optimizers.Optimizer,
               start_token_index: int,
               rnn_size: int) -> None:
    """Trains the encoder-decoder model using the current input and target training batches.

    Predicts the output for the current input batch, computes loss on comparison with the target batch, and optimizes
    the encoder-decoder based on the computed loss.

    Args:
        input_batch: Current batch for the encoder model which contains the features extracted from the images.
        target_batch: Current batch for the decoder model which contains the captions for the images.
        optimizer: Optimizing algorithm which will be used improve the performance of the encoder-decoder model.
        start_token_index: Index value for the start token in the vocabulary.
        rnn_size: No. of units in each LSTM layer.

    Returns:
        None.
    """
    loss = 0
    # Initializes the hidden states from the decoder for each batch.
    decoder_hidden_states = decoder.initialize_hidden_states(target_batch.shape[0], rnn_size)
    # First decoder input batch contains just the start token index.
    decoder_input_batch = tf.expand_dims([start_token_index] * target_batch.shape[0], 1)
    with tf.GradientTape() as tape:
        encoder_out = encoder(input_batch, True)
        # Passes the encoder features into the decoder for all words in the captions.
        for i in range(1, target_batch.shape[1]):
            predicted_batch, decoder_hidden_states = decoder(decoder_input_batch, decoder_hidden_states, encoder_out,
                                                             True)
            loss += loss_function(target_batch[:, i], predicted_batch)
            # Uses teacher forcing method to pass next target word as input into the decoder.
            decoder_input_batch = tf.expand_dims(target_batch[:, i], 1)
    model_variables = encoder.trainable_variables + decoder.trainable_variables
    gradients = tape.gradient(loss, model_variables)
    optimizer.apply_gradients(zip(gradients, model_variables))
    batch_loss = (loss / target_batch.shape[1])
    train_loss(batch_loss)


def validation_step(input_batch: tf.Tensor,
                    target_batch: tf.Tensor,
                    start_token_index: int,
                    rnn_size: int) -> None:
    """Validates the encoder-decoder model using the current input and target validation batches.

    Args:
        input_batch: Current batch for the encoder model which contains the features extracted from the images.
        target_batch: Current batch for the decoder model which contains the captions for the images.
        start_token_index: Index value for the start token in the vocabulary.
        rnn_size: No. of units in each LSTM layer.

    Returns:
        None.
    """
    loss = 0
    # Initializes the hidden states from the decoder for each batch.
    decoder_hidden_states = decoder.initialize_hidden_states(target_batch.shape[0], rnn_size)
    # First decoder input batch contains just the start token index.
    decoder_input_batch = tf.expand_dims([start_token_index] * target_batch.shape[0], 1)
    encoder_out = encoder(input_batch, False)
    # Passes the encoder features into the decoder for all words in the captions.
    for i in range(1, target_batch.shape[1]):
        predicted_batch, decoder_hidden_states = decoder(decoder_input_batch, decoder_hidden_states, encoder_out, False)
        loss += loss_function(target_batch[:, i], predicted_batch)
        decoder_input_batch = tf.expand_dims(target_batch[:, i], 1)
    batch_loss = loss / target_batch.shape[1]
    validation_loss(batch_loss)


def image_features_retrieve(batch_image_ids: tf.Tensor) -> tf.Tensor:
    """Retrieves saved extracted features for image ids in the batch.

    Args:
        batch_image_ids: A tensor which contains the image ids in the current batch.

    Returns:
        A tensor which contains extracted features for the image ids in the current batch.
    """
    extracted_features = list()
    # Iterates across the image ids in the current batch.
    for i in range(len(batch_image_ids)):
        current_image_features = load_pickle_file('../data/processed_data/images', str(batch_image_ids[i].numpy()))
        extracted_features.append(current_image_features)
    extracted_features = tf.convert_to_tensor(extracted_features)
    # Reshapes the tensor from (batch_size, 1, 64, 2048) to (batch_size, 64, 2048).
    extracted_features = tf.reshape(extracted_features, [extracted_features.shape[0], extracted_features.shape[2],
                                                         extracted_features.shape[3]])
    return extracted_features


def model_training_validation(train_dataset: tf.data.Dataset,
                              validation_dataset: tf.data.Dataset,
                              parameters: dict) -> None:
    """Trains and validates the current configuration of the model using the train and validation dataset.

    Args:
        train_dataset: Image ids and tokenized captions in the train dataset.
        validation_dataset: Image ids and tokenized captions in the validation dataset.
        parameters: A dictionary which contains current model configuration details.

    Returns:
        None.
    """
    global encoder, decoder, train_loss, validation_loss
    # Tensorflow metrics which computes the mean of all the elements.
    train_loss = tf.keras.metrics.Mean(name='train_loss')
    validation_loss = tf.keras.metrics.Mean(name='validation_loss')
    # Chooses the encoder and decoder based on the parameter configuration.
    encoder, decoder = choose_encoder_decoder(parameters)
    # Creates checkpoint and manager for the encoder-decoder model and the optimizer.
    optimizer = tf.keras.optimizers.Adam()
    model_directory_path = '../results/{}/model_{}'.format(parameters['attention'], parameters['model_number'])
    checkpoint_directory = '{}/checkpoints'.format(model_directory_path)
    checkpoint = tf.train.Checkpoint(optimizer=optimizer, encoder=encoder, decoder=decoder)
    manager = tf.train.CheckpointManager(checkpoint, directory=checkpoint_directory, max_to_keep=3)
    # Creates empty dataframe for saving the model training and validation metrics for the current encoder-decoder
    # model.
    split_history_dataframe = pd.DataFrame(columns=['epochs', 'train_loss', 'validation_loss'])
    checkpoint_count = 0
    best_validation_loss = None
    history_directory_path = check_directory_existence(model_directory_path, 'history')
    history_dictionary_path = '{}/split_history.csv'.format(history_directory_path)
    # Iterates across the epochs for training the encoder-decoder model.
    print()
    for epoch in range(parameters['epochs']):
        epoch_start_time = time.time()
        train_loss.reset_states()
        validation_loss.reset_states()
        # Iterates across the batches in the train dataset.
        for (batch, (image_ids, target_batch)) in enumerate(train_dataset.take(parameters['train_steps_per_epoch'])):
            batch_start_time = time.time()
            # Loads features for the image ids in the current batch.
            input_batch = image_features_retrieve(image_ids)
            train_step(input_batch, target_batch, optimizer, parameters['start_token_index'], parameters['rnn_size'])
            batch_end_time = time.time()
            if batch % 10 == 0:
                print('Epoch={}, Batch={}, Training loss={}, Time taken={} sec'.format(
                    epoch + 1, batch, str(round(train_loss.result().numpy(), 3)),
                    round(batch_end_time - batch_start_time, 3)))
        print()
        # Iterates across the batches in the validation dataset.
        for (batch, (image_ids, target_batch)) in enumerate(validation_dataset.take(
                parameters['validation_steps_per_epoch'])):
            batch_start_time = time.time()
            # Loads features for the image ids in the current batch.
            input_batch = image_features_retrieve(image_ids)
            validation_step(input_batch, target_batch, parameters['start_token_index'], parameters['rnn_size'])
            batch_end_time = time.time()
            if batch % 10 == 0:
                print('Epoch={}, Batch={}, Validation loss={}, Time taken={} sec'.format(
                    epoch + 1, batch, str(round(validation_loss.result().numpy(), 3)),
                    round(batch_end_time - batch_start_time, 3)))
        print()
        # Updates the complete metrics dataframe with the metrics for the current training and validation metrics.
        history_dictionary = {'epochs': int(epoch + 1), 'train_loss': str(round(train_loss.result().numpy(), 3)),
                              'validation_loss': str(round(validation_loss.result().numpy(), 3))}
        split_history_dataframe = split_history_dataframe.append(history_dictionary, ignore_index=True)
        split_history_dataframe.to_csv(history_dictionary_path, index=False)
        epoch_end_time = time.time()
        print('Epoch={}, Training loss={}, Validation loss={}, Time taken={} sec'.format(
            epoch + 1, str(round(train_loss.result().numpy(), 3)), str(round(validation_loss.result().numpy(), 3)),
            round(epoch_end_time - epoch_start_time, 3)))
        # If epoch = 1, then best validation loss is replaced with current validation loss, and the checkpoint is saved.
        if best_validation_loss is None:
            checkpoint_count = 0
            best_validation_loss = str(round(validation_loss.result().numpy(), 3))
            manager.save()
            print('Checkpoint saved at {}'.format(checkpoint_directory))
            print()
        # If the best validation loss is higher than current validation loss, the best validation loss is replaced with
        # current validation loss, and the checkpoint is saved.
        elif best_validation_loss > str(round(validation_loss.result().numpy(), 3)):
            checkpoint_count = 0
            print('Best validation loss changed from {} to {}'.format(str(best_validation_loss),
                                                                      str(round(validation_loss.result().numpy(), 3))))
            best_validation_loss = str(round(validation_loss.result().numpy(), 3))
            manager.save()
            print('Checkpoint saved at {}'.format(checkpoint_directory))
            print()
        # If the best validation loss is not higher than the current validation loss, then the number of times the model
        # has not improved is incremented by 1.
        elif checkpoint_count <= 4:
            checkpoint_count += 1
            print('Best validation loss did not improve.')
            print('Checkpoint not saved.')
            print()
        # If the number of times the model did not improve is greater than 4, then model is stopped from training
        # further.
        else:
            print('Model did not improve after 4th time. Model stopped from training further.')
            break


def model_testing(test_dataset: tf.data.Dataset,
                  parameters: dict) -> None:
    """Tests the currently trained encoder-decoder model using the test dataset.

    Args:
        test_dataset: Image ids and tokenized captions in the test dataset.
        parameters: A dictionary which contains current model configuration details.

    Returns:
        None.
    """
    global validation_loss
    # Tensorflow metrics which computes the mean of all the elements.
    validation_loss = tf.keras.metrics.Mean(name='validation_loss')
    validation_loss.reset_states()
    # Chooses the encoder and decoder based on the parameter configuration.
    encoder, decoder = choose_encoder_decoder(parameters)
    # Creates checkpoint for the encoder-decoder model and restores the last saved checkpoint.
    model_directory_path = '../results/{}/model_{}'.format(parameters['attention'], parameters['model_number'])
    checkpoint_directory = '{}/checkpoints'.format(model_directory_path)
    checkpoint = tf.train.Checkpoint(encoder=encoder, decoder=decoder)
    checkpoint.restore(tf.train.latest_checkpoint(checkpoint_directory))
    # Iterates across the batches in the test dataset.
    for (batch, (input_batch, target_batch)) in enumerate(test_dataset.take(parameters['test_steps_per_epoch'])):
        input_batch = image_features_retrieve(input_batch)
        validation_step(input_batch, target_batch, parameters['start_token_index'], parameters['rnn_size'])
    print('Test Loss={}'.format(str(round(validation_loss.result().numpy(), 3))))
