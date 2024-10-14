from typing import Optional


def make_labels(
    bins: list[float | int],
    unit: str = "",
    decimals: int = 0,
    overwrite_first_labels: Optional[list[str]] = None,
    overwrite_with_zero: Optional[list[str]] = False,
) -> list[str]:
    """_summary_

    Parameters
    ----------
    bins : list[float | int]
        _description_
    unit : str, optional
        _description_, by default ""
    decimals : int, optional
        _description_, by default 0
    overwrite_first_bin : Optional[str], optional
        _description_, by default None

    Returns
    -------
    list[str]
        _description_
    """
    labels = []
    bins = [f"{unit}{value:,.{decimals}f}" for value in bins]
    for i in range(len(bins) + 1):
        if i == 0:
            label = f"≤ {bins[i]}"
        elif i == len(bins):
            label = f"> {bins[i-1]}"
        else:
            label = f"{bins[i-1]} - {bins[i]}"
        labels.append(label)
    if overwrite_first_labels:
        labels[: len(overwrite_first_labels)] = overwrite_first_labels
    if overwrite_with_zero:
        labels[0] = "0"
        labels[1] = f"≤ {bins[1]}"

    return labels
