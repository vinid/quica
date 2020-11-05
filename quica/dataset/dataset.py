
class IRRDataset:
    def __init__(self, dataset):
        self.data = dataset
        self.coders = len(dataset)
        self.subjects = len(dataset[0])

    def get_coder(self, index):
        return self.data[index]

