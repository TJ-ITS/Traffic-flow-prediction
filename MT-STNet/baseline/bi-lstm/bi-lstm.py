# -- coding: utf-8 --
import tensorflow as tf

class BilstmClass(object):
    def __init__(self, hp, placeholders=None):
        '''
        :param hp:
        :param placeholders:
        '''
        self.hp = hp
        self.batch_size = self.hp.batch_size
        self.layer_num = self.hp.hidden_layer
        self.hidden_size = self.hp.hidden_size
        self.input_length = self.hp.input_length
        self.output_length = self.hp.output_length
        self.placeholders = placeholders
        self.encoder()
        self.decoder()

    def lstm(self):
        def cell():
            lstm_cell = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_size)
            lstm_cell_ = tf.nn.rnn_cell.DropoutWrapper(cell=lstm_cell,output_keep_prob=1-self.placeholders['dropout'])
            return lstm_cell_
        mlstm = tf.nn.rnn_cell.MultiRNNCell([cell() for _ in range(self.layer_num)])
        return mlstm

    def bilstm(self):
        def cell():
            cell_bw = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_size)  # single lstm unit
            cell_bw = tf.nn.rnn_cell.DropoutWrapper(cell_bw, output_keep_prob=1-self.placeholders['dropout'])
            cell_fw = tf.nn.rnn_cell.BasicLSTMCell(num_units=self.hidden_size)  # single lstm unit
            cell_fw = tf.nn.rnn_cell.DropoutWrapper(cell_fw, output_keep_prob=1-self.placeholders['dropout'])
            return cell_fw, cell_bw
        cell_fw, cell_bw=cell()
        f_mlstm=tf.nn.rnn_cell.MultiRNNCell([cell_fw for _ in range(self.layer_num)])
        b_mlstm = tf.nn.rnn_cell.MultiRNNCell([cell_bw for _ in range(self.layer_num)])
        return f_mlstm, b_mlstm

    def encoder(self):
        '''
        :return:  shape is [batch size, time size, hidden size]
        '''

        self.e_lstm_1 = self.lstm()
        self.e_bilstm_2 = self.bilstm()
        self.e_lstm_3 = self.lstm()

    def decoder(self):
        '''
        :return:
        '''
        self.d_lstm_1 = self.lstm()
        self.d_bilstm_2 = self.bilstm()
        self.d_lstm_3 = self.lstm()

    def encoding(self, inputs):
        '''
        :param inputs:
        :return: shape is [batch size, time size, hidden size]
        '''
        with tf.variable_scope('encoder_lstm'):
            
            outputs, _ = tf.nn.bidirectional_dynamic_rnn(self.ef_mlstm, self.eb_mlstm, inputs, dtype=tf.float32)
            # [2, batch_size, seq_length, output_size]
            outputs = tf.concat(outputs, axis=2)
        return outputs

    def decoding(self,  encoder_hs, site_num):
        '''
        :param encoder_hs:
        :return:  shape is [batch size, prediction size]
        '''
        pres = []
        h_state = encoder_hs[:, -1, :]
        initial_state=self.d_initial_state

        h_state = tf.layers.dense(h_state, units=self.hidden_size)

        for i in range(self.output_length):
            h_state = tf.expand_dims(input=h_state, axis=1)
            with tf.variable_scope('decoder_lstm'):
                h_state, state = tf.nn.dynamic_rnn(cell=self.d_mlstm, inputs=h_state, dtype=tf.float32)
            h_state=tf.reshape(h_state,shape=[-1,self.hidden_size])

            results = tf.layers.dense(inputs=h_state, units=1, name='layer', reuse=tf.AUTO_REUSE)
            pre=tf.reshape(results,shape=[-1,site_num])
            # to store the prediction results for road nodes on each time
            pres.append(tf.expand_dims(pre, axis=-1))

        return tf.concat(pres, axis=-1,name='output_y')

import numpy as np
if __name__ == '__main__':
    train_data=np.random.random(size=[32,3,16])
    x=tf.placeholder(tf.float32, shape=[32, 3, 16])
    r=lstm(32,10,2,128)
    hs=r.encoding(x)

    print(hs.shape)

    pre=r.decoding(hs)
    print(pre.shape)