import tensorflow as tf
def mean_squared_error(y_true, y_pred): 
    return tf.reduce_mean(tf.square(y_true - y_pred)) 
 
def stego_loss(y_true, y_pred): 
    """ 
    Loss between Cover Image and Stego Image. 
    We want Stego Image to look exactly like Cover Image. 
    """ 
    return mean_squared_error(y_true, y_pred) 
 
def secret_loss(y_true, y_pred): 
    """ 
    Loss between Input Secret and Revealed Secret. 
    We want Revealed Secret to be exactly the Input Secret. 
    """ 
    return mean_squared_error(y_true, y_pred) 
def mean_squared_error(y_true, y_pred): 
    return tf.reduce_mean(tf.square(y_true - y_pred)) 
 
def stego_loss(y_true, y_pred): 
    """ 
    Loss between Cover Image and Stego Image. 
    We want Stego Image to look exactly like Cover Image. 
    """ 
    return mean_squared_error(y_true, y_pred) 
 
def secret_loss(y_true, y_pred): 
    """ 
    Loss between Input Secret and Revealed Secret. 
    We want Revealed Secret to be exactly the Input Secret. 
    """ 
    return mean_squared_error(y_true, y_pred) 