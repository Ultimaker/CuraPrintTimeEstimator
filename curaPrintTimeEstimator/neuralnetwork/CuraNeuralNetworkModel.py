# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from typing import List
import math
import tensorflow as tf

from Settings import Settings

class CuraNeuralNetworkModel:
    """
    Creates a neural network
    """
    LOG_FILE = "{}/logs/train.log".format(Settings.PROJECT_DIR)
    CURA_NN_FILE = "{}/output/cura_datamodel.ckpt".format(Settings.PROJECT_DIR)

    def __init__(self, feature_nr: int, output_nr: int, hidden_layer_neuron_nr: List[int] = None):
        """
        :param feature_nr: indicates the number of inputs
        :param output_nr: indicates the number of outputs
        :param hidden_layer_neuron_nr: indicates the number of neurons that are in the hidden layer
        """

        # Create the input and output variables
        logging.debug("Creating a NeuralNetwork with {feature_nr} inputs, {output_nr} outputs and {layers} hidden layers with "
                     "{hidden_nr} neurons".format(feature_nr = feature_nr, output_nr = output_nr, layers = len(hidden_layer_neuron_nr), hidden_nr = hidden_layer_neuron_nr))

        self.input  = tf.placeholder(tf.float32, [None, feature_nr], name = "input")
        self.target = tf.placeholder(tf.float32, [None, output_nr], name = "target")

        # Construct the NN with several hidden layers as indicated in the input variable
        hidden_input = self.input
        hidden_out = self.input
        hidden_layer_nr = feature_nr
        input_nr = hidden_input._shape_as_list()[1]
        count = 0
        mean = 1.0
        std_dev = 0.1
        if hidden_layer_neuron_nr is not None:
            for hidden_layer_nr in hidden_layer_neuron_nr:
                count += 0
                # Create connections from the input layer to the hidden layer
                W = tf.Variable(tf.truncated_normal([input_nr, hidden_layer_nr], mean = mean, stddev = std_dev), name = "W{}".format(count))
                b = tf.Variable(tf.truncated_normal([hidden_layer_nr], mean = mean, stddev = std_dev), name = "b{}".format(count))
                hidden_out = tf.nn.relu(tf.add(tf.matmul(hidden_input, W), b))   # activation of the hidden layer using linear function TODO test with tanh or other activation functions
                tf.summary.histogram("activation_{}".format(count), hidden_out)
                hidden_input = hidden_out
                input_nr = hidden_layer_nr

        # Create connections from the hidden layer to the output layer
        self.WOut = tf.Variable(tf.truncated_normal([hidden_layer_nr, output_nr], mean = mean, stddev = std_dev), name = "WOut")
        self.bOut = tf.Variable(tf.truncated_normal([output_nr], mean = mean, stddev = std_dev), name = "bOut")
        self.output = tf.nn.relu(tf.add(tf.matmul(hidden_out, self.WOut), self.bOut))  # output value
        tf.summary.histogram("activationOut".format(count), self.output)

        # Function used to calculate the cost between the right output and the predicted output
        self.cost_function = tf.reduce_mean(tf.square(tf.subtract(self.target, self.output)))
        tf.summary.histogram("cost", self.cost_function)

    def train(self, data_train: List[List[float]], target_train: List[List[float]], learning_rate: float = 0.0001,
              epochs: int = 10000, batch_size: int = 10):
        logging.info("################# TRAINING #################")
        optimizer = tf.train.GradientDescentOptimizer(learning_rate = learning_rate).minimize(self.cost_function)
        saver = tf.train.Saver()

        with tf.Session() as sess:
            # Initialize the variables
            try:
                saver.restore(sess, self.CURA_NN_FILE)
            except:
                sess.run(tf.global_variables_initializer())
            train_writer = tf.summary.FileWriter(self.LOG_FILE, sess.graph)

            # Number of batches that will be used for training
            batch_nr = int(len(target_train) / batch_size)

            # Train the NN for the number of epochs
            counter = 0
            for epoch in range(epochs):
                avg_cost = 0
                for index in range(batch_nr):
                    counter += 1
                    # Split the training dataset in batches
                    data_batch = data_train[index * batch_size : min((index + 1) * batch_size, len(data_train))]
                    target_batch = target_train[index * batch_size : min((index + 1) * batch_size, len(target_train))]

                    merge = tf.summary.merge_all()
                    logging.debug("Input {}".format(data_batch[0]))
                    logging.debug("Estimated output before train {est} ?= {target}".format(
                        est = sess.run(self.output, feed_dict={self.input: data_batch})[0], target = target_batch[0]))

                    # Actually train the NN with the provided data
                    summary, optimizer_result, cost = sess.run([merge, optimizer, self.cost_function], feed_dict = {
                        self.input: data_batch, self.target: target_batch
                    })
                    train_writer.add_summary(summary, counter)
                    avg_cost += cost / batch_nr
                    if math.isnan(cost):
                        return
                    if (epoch + 1) % 10 == 0 and index == 0:
                        w_value = sess.run(self.WOut)
                        b_value = sess.run(self.bOut)
                        logging.warning("############### Epoch: {epoch} - cost = {cost:.5f}".format(epoch = epoch + 1, cost = cost))
                        logging.debug("Estimation: {weights} + {bias} = {est} <> {target}".format(
                            weights = w_value, bias = b_value, est = sess.run(self.output, feed_dict={self.input: data_batch})[0],
                            target = target_batch[0]))

            # Store the training data
            save_path = saver.save(sess, self.CURA_NN_FILE)
            logging.warning("Model file saved in {path}".format(path = save_path))

    def validate(self, data_test: List[List[float]], target_test: List[List[float]]):
        logging.info("################### TEST ###################")
        saver = tf.train.Saver()

        with tf.Session() as sess:
            # Initialize the variables
            try:
                saver.restore(sess, self.CURA_NN_FILE)
            except:
                logging.error("No model file found in {path}. Can't continue the validation.".format(path = self.CURA_NN_FILE))
                return
            # Validate the NN with the provided test data
            logging.debug("{data_test} and {target_test}")
            logging.debug("{output}".format(output = sess.run(self.cost_function, feed_dict = {self.input: data_test, self.target: target_test})))

    def predict(self, data_predict: List[List[float]]) -> List[List[float]]:
        logging.info("################ PREDICTION ################")
        saver = tf.train.Saver()

        with tf.Session() as sess:
            # Initialize the variables
            try:
                saver.restore(sess, self.CURA_NN_FILE)
            except:
                logging.error("No model file found in {path}. Can't continue the prediction.".format(path = self.CURA_NN_FILE))
                return [[]]
            # Validate the NN with the provided test data
            predicted_value = sess.run(self.output, feed_dict = {self.input: data_predict})
            logging.debug("{output}".format(output = predicted_value))

        return predicted_value
