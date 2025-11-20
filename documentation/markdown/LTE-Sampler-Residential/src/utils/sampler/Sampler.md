Module LTE-Sampler-Residential.src.utils.sampler.Sampler
========================================================

Classes
-------

`Sampler(bayesian_network_path)`
:   

    ### Methods

    `GUM_Sampling(self, numberOfSamples, evs={})`
    :   Perform sampling to generate a specified number of samples.
        Parameters:
            numberOfSamples (int): The total number of samples to generate.
            evs (dict, optional): A dictionary of environmental variables to influence the sampling process. Defaults to an empty dictionary.
        Returns:
            pd.DataFrame: A DataFrame containing the sampled data, reset to a new index.
        Notes:
            The function first attempts to generate samples using the draw_GUM_Sample method.
            If the initial sample size is insufficient, it continues to sample until the desired number of samples is reached.

    `draw_GUM_Sample(self, number, Multiplicateur=1, evs={})`
    :   Generates samples from a Bayesian network using the PyAgrum library.
        
        Parameters:
            number (int): The base number of samples to generate.
            Multiplicateur (float, optional): A multiplier to adjust the number of samples. Default is 1.
            evs (dict, optional): A dictionary of evidence variables to condition the sampling on. Default is an empty dictionary.
        
        Returns:
            pandas.DataFrame: A DataFrame containing the generated samples.

    `resstock_args_sampling(self, lst_dct_args={})`
    :