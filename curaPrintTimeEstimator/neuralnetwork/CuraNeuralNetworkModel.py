# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import List
import math
import tensorflow as tf

class CuraNeuralNetworkModel:
    """
    Creates a neural network with one hidden layer
    """

    def __init__(self, feature_nr: int, output_nr: int, hidden_layer_neuron_nr: int = 2):
        """
        :param feature_nr: indicates the number of inputs
        :param output_nr: indicates the number of outputs
        :param hidden_layer_neuron_nr: indicates the number of neurons that are in the hidden layer
        """

        # Create the input and output variables
        logging.info("Creating a NeuralNetwork with {feature_nr} inputs, {output_nr} outputs and 1 hidden layer with "
                     "{hidden_nr} neurons".format(feature_nr = feature_nr, output_nr = output_nr, hidden_nr = hidden_layer_neuron_nr))

        self.input  = tf.placeholder(tf.float32, [None, feature_nr], name = "input")
        self.target = tf.placeholder(tf.float32, [None, output_nr], name = "target")

        # Create connections from the input layer to the hidden layer
        self.W1 = tf.Variable(tf.truncated_normal([feature_nr, hidden_layer_neuron_nr], mean = 0.0, stddev = 0.0), name = 'W1')
        self.b1 = tf.Variable(tf.truncated_normal([hidden_layer_neuron_nr], mean = 0.0, stddev = 0.0), name = 'b1')
        hidden_out = tf.add(tf.matmul(self.input, self.W1), self.b1)   # activation of the hidden layer using linear function TODO test with tanh or other activation functions

        # Create connections from the hidden layer to the output layer
        self.W2 = tf.Variable(tf.truncated_normal([hidden_layer_neuron_nr, output_nr], mean = 0.0, stddev = 0.0), name = 'W2')
        self.b2 = tf.Variable(tf.truncated_normal([output_nr], mean = 0.0, stddev = 0.0), name = 'b2')
        self.output = tf.add(tf.matmul(hidden_out, self.W2), self.b2)  # output value

        # Function used to calculate the cost between the right output and the predicted output
        self.cost_function = tf.reduce_mean(tf.square(tf.subtract(self.target, self.output)))

    def train(self, data_train: List[List[float]], target_train: List[List[float]], learning_rate: float = 0.0001,
              epochs: int = 10000, batch_size: int = 10):
        logging.info("################# TRAINING #################")
        optimizer = tf.train.GradientDescentOptimizer(learning_rate = learning_rate).minimize(self.cost_function)

        with tf.Session() as sess:
            # Initialize the variables
            sess.run(tf.global_variables_initializer())
            w1_value = sess.run(self.W1)
            b1_value = sess.run(self.b1)
            w2_value = sess.run(self.W2)
            b2_value = sess.run(self.b2)
            logging.debug("Initial values for hidden layer: {weights} + {bias}".format(weights = w1_value, bias = b1_value))
            logging.debug("Initial values for output layer: {weights} + {bias}".format(weights = w2_value, bias = b2_value))

            # Number of batches that will be used for training
            batch_nr = int(len(target_train) / batch_size)

            # Train the NN for the number of epochs
            for epoch in range(epochs):
                avg_cost = 0
                cost = 0
                for index in range(batch_nr):
                    # Split the training dataset in batches
                    data_batch = data_train[index * batch_size : min((index + 1) * batch_size, len(data_train))]
                    target_batch = target_train[index * batch_size : min((index + 1) * batch_size, len(target_train))]

                    logging.debug("Input {}".format(data_batch[0]))
                    logging.debug("Estimated output before train {est} ?= {target}".format(
                        est = sess.run(self.output, feed_dict={self.input: data_batch})[0], target = target_batch[0]))
                    # Actually train the NN with the provided data
                    optimizer_result, cost = sess.run([optimizer, self.cost_function], feed_dict = {
                        self.input: data_batch, self.target: target_batch
                    })
                    avg_cost += cost / batch_nr
                    if math.isnan(cost):
                        return
                    if (epoch + 1) % 10 == 0 and index == 0:
                        w_value = sess.run(self.W2)
                        b_value = sess.run(self.b2)
                        logging.warning("############### Epoch: {epoch} - cost = {cost:.5f}".format(epoch = epoch + 1, cost = cost))
                        # logging.debug("Estimation: {weights} + {bias} = {est} <> {target}".format(
                        #     weights = w_value, bias = b_value, est = sess.run(self.output, feed_dict={self.input: data_batch}),
                        #     target = target_batch))

    def validate(self, data_test: List[List[float]], target_test: List[List[float]]):
        logging.info("################### TEST ###################")
        with tf.Session() as sess:
            # Initialize the variables
            sess.run(tf.global_variables_initializer())
            # Validate the NN with the provided test data
            logging.debug("{data_test} and {target_test}")
            logging.debug("{output}".format(output = sess.run(self.cost_function, feed_dict = {self.input: data_test, self.target: target_test})))

    def predict(self, data_predict: List[List[float]]) -> List[List[float]]:
        logging.info("################ PREDICTION ################")
        with tf.Session() as sess:
            # Initialize the variables
            sess.run(tf.global_variables_initializer())
            # Validate the NN with the provided test data
            predicted_value = sess.run(self.output, feed_dict = {self.input: data_predict})
            logging.debug("{output}".format(output = predicted_value))

        return predicted_value
