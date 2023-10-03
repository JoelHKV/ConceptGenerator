import numpy as np

def compute_icc(data):
    """
    Compute the Intraclass Correlation Coefficient (ICC) based on variance components.

    Args:
        data (numpy.ndarray): A 2D NumPy array where rows represent items (concepts) and columns represent measurements.

    Returns:
        float: The computed ICC value.
    """
    nro_items = data.shape[0]
    nro_measurements = data.shape[1]

    # Calculate the means across repeated measurements
    concept_means = np.mean(data, axis=1)

    # Calculate the overall mean across all concepts and measurements
    overall_mean = np.mean(data)

    # Calculate the sums of squares for the total variance
    ss_total = np.sum((data - overall_mean) ** 2)

    # Calculate the sums of squares for the concept variance
    ss_concept = np.sum((concept_means - overall_mean) ** 2) * nro_measurements

    # Calculate the residual sums of squares (within-concept variance)
    ss_residual = ss_total - ss_concept

    # Calculate the degrees of freedom
    df_concept = nro_items - 1  # Number of concepts - 1
    df_residual = nro_items * nro_measurements - 1  # (Number of concepts * Number of measurements per concept) - 1

    # Calculate the mean square values
    ms_concept = ss_concept / df_concept
    ms_residual = ss_residual / df_residual

    # Calculate the ICC based on the variance components
    icc = (ms_concept - ms_residual) / (ms_concept + (nro_measurements - 1) * ms_residual)

    return icc

 