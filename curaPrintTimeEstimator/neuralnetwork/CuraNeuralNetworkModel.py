# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import List
import numpy as np
import tensorflow as tf

##  It creates a NN model with one hidden layer
class CuraNeuralNetworkModel:

    def __init__(self, feature_nr: int, output_nr: int, hidden_layer_neuron_nr: int = 10):
        # Create the input and output variables
        logging.info("Creating a NeuralNetwork with {feature_nr} inputs, {output_nr} outputs and 1 hidden layer with "
                     "{hidden_nr} neurons".format(feature_nr = feature_nr, output_nr = output_nr, hidden_nr = hidden_layer_neuron_nr))

        self.input = tf.placeholder(tf.float32, [None, feature_nr], name = "input")
        self.target = tf.placeholder(tf.float32, [None, output_nr], name = "target")

        # Create connections from the input layer to the hidden layer
        W1 = tf.Variable(tf.truncated_normal([feature_nr, hidden_layer_neuron_nr], stddev = 0.03), name = 'W1')
        b1 = tf.Variable(tf.truncated_normal([hidden_layer_neuron_nr]), name = 'b1')
        hidden_out = tf.nn.relu(tf.add(tf.matmul(self.input, W1), b1))   # activation of the hidden layer using rectified linear TODO test with tanh or other activation functions

        # Create connections from the hidden layer to the output layer
        W2 = tf.Variable(tf.truncated_normal([hidden_layer_neuron_nr, output_nr], stddev = 0.03), name = 'W2')
        b2 = tf.Variable(tf.truncated_normal([output_nr]), name = 'b2')
        self.output = tf.nn.relu(tf.add(tf.matmul(hidden_out, W2), b2))  # output value

        # Function used to calculate the cost between the right output and the predicted output
        self.cost_function = tf.reduce_mean(tf.square(tf.subtract(self.output, self.target)))

    def train(self, data_train: List[List[float]], target_train: List[List[float]], learning_rate: float = 0.02, epochs: int = 2000, batch_size: int = 10):
        logging.info("################# TRAINING #################")
        optimizer = tf.train.GradientDescentOptimizer(learning_rate = learning_rate).minimize(self.cost_function)

        with tf.Session() as sess:
            # Initialize the variables
            sess.run(tf.global_variables_initializer())

            # Number of batches that will be used for training
            batch_nr = int(len(target_train) / batch_size)

            # Train the NN for the number of epochs
            for epoch in range(epochs):
                avg_cost = 0
                for index in range(batch_nr):
                    # Split the training dataset in batches
                    data_batch = data_train[index * batch_size : min((index + 1) * batch_size, len(data_train))]
                    target_batch = target_train[index * batch_size : min((index + 1) * batch_size, len(target_train))]

                    # Actually train the NN with the provided data
                    _, cost = sess.run([optimizer, self.cost_function], feed_dict = {self.input: data_batch, self.target: target_batch})
                    avg_cost += cost / batch_nr
                if (epoch + 1) % 10 == 0:
                    logging.debug("Epoch: {epoch} - cost = {cost:.3f}".format(epoch = epoch + 1, cost = avg_cost))

    def validate(self, data_test: List[List[float]], target_test: List[List[float]]):
        logging.info("################### TEST ###################")
        with tf.Session() as sess:
            # Initialize the variables
            sess.run(tf.global_variables_initializer())
            # Validate the NN with the provided test data
            logging.debug("{output}".format(output = sess.run(self.cost_function, feed_dict = {self.input: data_test, self.target: target_test})))
