import matplotlib.pyplot as plt

# Support for Chinese characters.
plt.rcParams["font.sans-serif"] = ['Microsoft YaHei', 'Heiti']


def plot(title: str, names: list[str], counts: list[int]):
    plt.bar(names, counts)
    plt.title(title)
    plt.show()
