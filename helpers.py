class MyDataFrame():
    def __init__(self, verbose=0):
        self.x = dict()
        self.max_num_items = 0
        self.verbose = verbose

    def update(self, in_dict, add_missing_values=False, missing_val=np.nan):
        for k, v in in_dict.items():

            if isinstance(v, list):
                warnings.warn(f'Input for {k} is list, consider add_col.')

            if k not in list(self.x.keys()):
                if self.verbose > 0:
                    print(f'added {k}')
                # case 1: df just intialized
                if self.max_num_items == 0:
                    self.x[k] = [v]
                else:
                    # case 2: entire new key is added
                    if add_missing_values:
                        # fill with missing values to current num items
                        self.x[k] = [missing_val] * self.max_num_items
                        self.x[k].append(v)

            else:
                self.x[k].append(v)

        if add_missing_values:
            self._add_missing(missing_val)

    def _add_missing(self, missing_val):
        self._update()
        for k in self.x.keys():
            if self.verbose > 1 and len(self.x[k]) < self.max_num_items:
                print(f'add missing: {k}')

            while len(self.x[k]) < self.max_num_items:
                self.x[k].append(missing_val)

    def _update(self):
        self.max_num_items = max([len(v) for v in self.x.values()])

    def add_col(self, key, col):
        self.x[key] = col

    def get_df(self, cols=None):
        assert self._check_same_lenghts()
        return pd.DataFrame(self.x, columns=cols)

    def _check_same_lenghts(self):
        len_vals = {k: len(v) for k, v in self.x.items()}
        if len(set(len_vals.values())) > 1:
            print(len_vals)
            return False

        return True