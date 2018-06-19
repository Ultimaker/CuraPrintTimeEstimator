# Copyright (c) 2018 Ultimaker B.V.
# !/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json
import copy
from typing import List, Dict, Tuple, Optional
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf

##  It creates a NN model with one hidden layer
class CuraNeuralNetworkModel:

    def __init__(self, feature_nr: int, output_nr: int, hidden_layer_neuron_nr: int = 10):
        # Create the input and output variables
        self.input = tf.placeholder(tf.float32, [None, feature_nr], name = "input")
        self.target = tf.placeholder(tf.float32, [None, output_nr], name = "target")

        # Create connections from the input layer to the hidden layer
        W1 = tf.Variable(tf.truncated_normal([feature_nr,hidden_layer_neuron_nr], stddev = 0.03), name = 'W1')
        b1 = tf.Variable(tf.truncated_normal([hidden_layer_neuron_nr]), name = 'b1')
        hidden_out = tf.nn.relu(tf.add(tf.matmul(input, W1), b1))   # activation of the hidden layer

        # Create connections from the hidden layer to the output layer
        W2 = tf.Variable(tf.truncated_normal([hidden_layer_neuron_nr, output_nr], stddev = 0.03), name = 'W2')
        b2 = tf.Variable(tf.truncated_normal([output_nr]), name = 'b2')
        self.output = tf.nn.relu(tf.add(tf.matmul(hidden_out, W2), b2))  # output value

    def cost(self):
        tf.reduce_mean(tf.square(tf.subtract(self.output, self.target)))

    def train(self):
        pass

    def validate(self):
        pass