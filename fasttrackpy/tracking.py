import parselmouth as pm
import numpy as np
import scipy.fft


def all_tracks(sound, 
               start = 5000, 
               stop = 7000, 
               nstep = 20,
               time_step = 0.001,
               n_formants = 6,
               window_length = 0.025,
               pre_emphasis_from = 50):
    """
    Extract all formant tracks
    """
    max_formants = np.linspace(start = start, stop = stop, num = nstep)
    formant_arrays = [
        findformants(maximum_formant = x,
                     sound=sound,
                     time_step = time_step,
                     n_formants = n_formants, 
                     window_length = window_length,
                     pre_emphasis_from = pre_emphasis_from)
        for x in max_formants
    ]
    formant_candidates = np.stack(formant_arrays, axis = -1)
    return(formant_candidates)

def choose_winner(candidates, 
                  smooth_fun,
                  loss_fun,
                  agg_fun):
    """
    Return index of winner
    """
    smoothed = smooth_formants(candidates, smooth_fun)
    mses = smooth_error(candidates, smoothed, loss_fun, agg_fun)
    winner_idx = np.argmin(mses)
    return(winner_idx)
    
def dct_smooth(x, order = 5, out = "smooth"):
    """
    DCT smoother
    """
    coefs = scipy.fft.dct(x)
    coef_subset = coefs[0:order]
    smooth = scipy.fft.idct(coef_subset, n = x.shape[0])
    if out == "smooth":
        return(smooth)
    elif out == "coef":
        return(coef_subset)
    elif out == "both":
        return(coef_subset, smooth)


def findformants(maximum_formant,
                sound, 
                n_formants=4,  
                window_length = 0.05, 
                time_step = 0.002, 
                pre_emphasis_from = 50):
    """
    Track formants
    """
    formants = sound.to_formant_burg(
        time_step = time_step,
        max_number_of_formants = n_formants, 
        maximum_formant = maximum_formant,
        window_length = window_length,
        pre_emphasis_from = pre_emphasis_from
    )

    time_domain = formants.xs()
    tracks = np.array(
        [
            [formants.get_value_at_time(i+1, x) 
                for x in time_domain] 
            for i in range(int(np.floor(n_formants)))
        ]
    )
    return(tracks)

def lmse(formants, smoothed, axis = 1):
    """
    calculate the log mean squared error
    """
    sqe = np.power(np.log(formants) - np.log(smoothed), 2)
    mse = np.mean(sqe, axis = axis)
    return(mse)

def agg_sum(error, axis = 0):
    """
    Sum the error
    """

    agg_error = np.sum(error, axis = axis)
    return(agg_error)

def smooth_error(formants, smoothed, loss_fun, agg_fun):
    """
    calculate error
    """
    loss = loss_fun(formants, smoothed)
    total_loss = agg_fun(loss)
    return(total_loss)

def smooth_formants(formants, 
                    smooth_fun, 
                    axis = 1, 
                    **kwargs):
    """
    Given a formants array, smooth it according to smooth_fun
    """
    smoothed = np.apply_along_axis(smooth_fun, axis, formants, **kwargs)
    return(smoothed)

if __name__ == "__main__":
    pass