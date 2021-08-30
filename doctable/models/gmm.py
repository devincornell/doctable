import numpy as np
from collections import Counter
from dataclasses import dataclass, field

class GMM(list):
    ''' Gaussian mixture model.
    '''
    def set_new_sample(self):
        ''' Set a random sample of every centroid in the mixture.
        '''
        for cent in self.centroids:
            cent.set_sample()

    def get_sample(self):
        ''' Create random samples from centroids.
        '''
        self.samp = np.vstack([cent.samp for cent in self])
        return self.samp


@dataclass
class Centroid:
    ''' Represents a gaussian distribution and stores random samples.
    '''
    size: int = 300 # vector size
    norm: int = 1 # norm of the mean vector
    var: float = 0.01 # variance of samples around the mean vector
    nsamp: int = 100 # number of samples to draw
    normed: bool = False # normalize generated vectors or no?
    meanvec: np.ndarray = None # mean vector of centroid
    samp: np.ndarray = None # random samples

    def __post_init__(self):
        ''' Generate mean vector and sample (unless they're provided in constructor).
        ''' 
        # make new sample
        if self.samp is None:
            if self.meanvec is None:
                self.meanvec = self.make_random_mean() # random mean vector
            self.set_new_sample() # sample associated with this centroid
        
        else: # sample has been provided, so compute meanvec if not provided
            if self.meanvec is None:
                self.meanvec = np.mean(self.samp)

    def make_random_mean(self):
        ''' Return random mean vector for this centroid.
        '''
        vec = np.random.random_sample((self.size,))
        return vec / np.linalg.norm(vec) * self.norm

    def draw_sample(self):
        ''' Return random samples from this centroid.
        '''
        # create covariance matrix
        cov = np.zeros((self.size, self.size))
        np.fill_diagonal(cov, self.var)

        # sample from normal distribution
        samp = np.random.multivariate_normal(self.meanvec, cov, (self.nsamp,))

        # NOTE: normalizing each vector to magnitude of 1
        if self.normed:
            samp = samp / np.linalg.norm(samp, axis=1)[:,np.newaxis]
        return samp
    
    def set_new_sample(self):
        ''' Draw sample and assign it to this centroid.
        '''
        self.samp = self.draw_sample()

    def av_sim(self):
        ''' Average similarity between points.
        '''
        return np.mean(np.dot(self.samp, self.samp.T))




