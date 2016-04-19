import tensorflow as tf

import deepautoencoder.data


class BasicAutoEncoder:
    """A basic autoencoder with a single hidden layer"""

    def __init__(self, data_x, data_x_, hidden_dim, epoch=1000, batch_size=50):
        self.data_x_ = data_x_
        self.data_x = data_x
        self.batch_size = batch_size
        self.epoch = epoch
        self.hidden_dim = hidden_dim
        self.input_dim = len(data_x[0])
        self.hidden_feature = []
        # print(data_x.shape, data_x_.shape, hidden_dim)

    def forward(self, x):
        with tf.name_scope('encode'):
            weights = tf.Variable(tf.random_normal([self.input_dim, self.hidden_dim], dtype=tf.float32),
                                  name='weights')

            biases = tf.Variable(tf.zeros([self.hidden_dim]), name='biases')
            encoded = tf.nn.sigmoid(tf.matmul(x, weights) + biases, name='encoded')

        with tf.name_scope('decode'):
            biases = tf.Variable(tf.zeros([self.input_dim]), name='biases')
            decoded = tf.matmul(encoded, tf.transpose(weights)) + biases
        # loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(decoded, x, name='cross_entropy'))
        return encoded, decoded

    def train(self, x_, decoded):
        loss = tf.sqrt(tf.reduce_mean(tf.square(tf.sub(x_, decoded))))
        train_op = tf.train.AdamOptimizer(0.001).minimize(loss)
        return loss, train_op

    def run(self):
        with tf.Graph().as_default():
            x = tf.placeholder(dtype=tf.float32, shape=[None, self.input_dim], name='x')
            x_ = tf.placeholder(dtype=tf.float32, shape=[None, self.input_dim], name='x_')
            encoded, decoded = self.forward(x)
            loss, train_op = self.train(x_, decoded)
            with tf.Session() as sess:
                sess.run(tf.initialize_all_variables())
                for i in range(self.epoch):
                    for j in range(50):
                        b_x, b_x_ = deepautoencoder.data.get_batch(self.data_x, self.data_x_, self.batch_size)
                        sess.run(train_op, feed_dict={x: b_x, x_: b_x_})
                    if i % 100 == 0:
                        l = sess.run(loss, feed_dict={x: self.data_x, x_: self.data_x_})
                        print('epoch {0}: global loss = {1}'.format(i, l))
                self.hidden_feature = sess.run(encoded, feed_dict={x: self.data_x_})
                # print(sess.run(decoded, feed_dict={x: self.data_x})[0])

    def get_hidden_feature(self):
        return self.hidden_feature