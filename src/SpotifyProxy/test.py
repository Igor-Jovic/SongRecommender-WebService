# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "igor"
__date__ = "$Jun 29, 2016 9:58:36 PM$"
import pickle
if __name__ == "__main__":
    ml = "Pozdrav"
    with open('ml.pickle', 'wb') as handle:
            pickle.dump(ml, handle)
    print "Hello World"
