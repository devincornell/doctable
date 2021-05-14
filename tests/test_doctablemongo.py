import sys
sys.path.append('..')
import doctable

def test_doctablemongo():
    # make a bunch of centroids from which to sample
    gmm = doctable.GMM([
        doctable.Centroid(nsamp=1000), # specify any of the members of Centroid to change from defaults
        doctable.Centroid(nsamp=100),
        doctable.Centroid(nsamp=100),
        doctable.Centroid(nsamp=100),
        doctable.Centroid(nsamp=100),
    ])

    print([c.av_sim() for c in gmm])

    # show the size of the output. Will be sum of nsamp from each centroid
    X = gmm.get_sample()
    print(X.shape)


if __name__ == '__main__':

    test_doctablemongo()