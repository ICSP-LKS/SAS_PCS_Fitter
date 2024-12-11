import datetime

import numpy as np
from os.path import isfile
from scipy.optimize import curve_fit
from numbers import Number
from SAS_PCS_FITTER_KGOETZ91.helpers.functions import linear_function, spline_data

class BaseOneDDataSet:

    def _find_concat(self, x_max_orig, x_min_orig, x_max_new, x_min_new):
        if (x_max_orig < x_min_new) or (x_min_orig > x_max_new):
            return self._concat_no_overlap
        elif (x_min_orig > x_min_new) and (x_max_orig < x_max_new):
            return self._concat_old_in_new
        elif (x_min_new > x_min_orig) and (x_max_new < x_max_orig):
            return self._concat_new_in_old
        elif (x_max_orig > x_min_new):
            return self._concat_overlap_new_higher_x_range
        else:
            return self._concat_overlap_new_lower_x_range

    def _concat_no_overlap(self, dataset):
        x_max_orig = np.max(self.x)
        x_max_new = np.max(dataset.x)

        if x_max_orig > x_max_new:
            new_x = np.concatenate((dataset.x, self.x))
            new_y = np.concatenate((dataset.y, self.y))
            new_e = np.concatenate((dataset.error, self.error))
        else:
            new_x = np.concatenate((self.x, dataset.x))
            new_y = np.concatenate((self.y, dataset.y))
            new_e = np.concatenate((self.error, dataset.error))

        return BaseOneDDataSet(new_x, new_y, name=self.name, header=self._header, error=new_e)

    def _concat_overlap(self, left_overlap, right_overlap):

        if len(left_overlap) < 3 or len(right_overlap) < 3:
            mean_int_left = np.sum(left_overlap.y) / len(left_overlap.y)
            mean_int_right = np.sum(right_overlap.y) / len(right_overlap.y)
            factor = (mean_int_left / mean_int_right)
        else:
            m0 = ((left_overlap.y[-1] - left_overlap.y[0]) /
                  (left_overlap.x[-1] - left_overlap.x[0]))
            b0 = left_overlap.y[0] - m0 * left_overlap.x[0]
            p0 = [m0, b0]
            popt, pcov = curve_fit(linear_function, left_overlap.x, left_overlap.y,
                                   p0=p0)
            mleft = popt[0]
            bleft = popt[1]

            m0 = ((right_overlap.y[-1] - right_overlap.y[0]) /
                  (right_overlap.x[-1] - right_overlap.x[0]))
            b0 = right_overlap.y[0] - m0 * right_overlap.x[0]
            p0 = [m0, b0]
            popt, pcov = curve_fit(linear_function, right_overlap.x, right_overlap.y,
                                   p0=p0)
            mright = popt[0]
            bright = popt[1]
            lin_left = np.concatenate((linear_function(left_overlap.x, mleft, bleft),
                                       linear_function(right_overlap.x, mleft, bleft)))
            lin_right = np.concatenate((linear_function(left_overlap.x, mright, bright),
                                        linear_function(right_overlap.x, mright, bright)))
            factor = np.mean(np.divide(lin_left, lin_right))

        right_overlap = right_overlap * factor
        dtype = [("x", float), ("y", float), ("e", float)]
        new_left = np.array(list(zip(left_overlap.x, left_overlap.y, left_overlap.error)), dtype=dtype)
        new_right = np.array(list(zip(right_overlap.x, right_overlap.y, right_overlap.error)), dtype=dtype)
        new_values = np.sort(np.concatenate((new_left, new_right)), order="x")
        return BaseOneDDataSet(new_values['x'], new_values['y'], error=new_values['e'],
                               name=self.name, header=self._header), factor

    def _concat_old_in_new(self, dataset):
        x_max_orig = np.max(self.x)
        x_min_orig = np.min(self.x)

        left, overlap, right = dataset._create_overlap(x_max_orig, x_min_orig)
        overlap, factor = self._concat_overlap(self, overlap)
        left *= factor
        right *= factor

        result = left._concat_no_overlap(overlap)
        result = result._concat_no_overlap(right)
        return result

    def _concat_new_in_old(self, dataset):
        return dataset._concat_old_in_new(self)

    def _concat_overlap_new_higher_x_range(self, dataset):
        x_max_orig = np.max(self.x)
        x_min_new = np.min(dataset.x)

        old_x_no_overlap = self.x[self.x < x_min_new]
        new_x_no_overlap = dataset.x[dataset.x > x_max_orig]

        left = self[:len(old_x_no_overlap)]
        old_overlap = self[len(old_x_no_overlap):]

        new_overlap = dataset[:len(dataset) - len(new_x_no_overlap)]
        right = dataset[len(dataset) - len(new_x_no_overlap):]

        result_overlap, factor = self._concat_overlap(old_overlap, new_overlap)
        right *= factor

        result = left._concat_no_overlap(result_overlap)
        result = result._concat_no_overlap(right)
        return result

    def _concat_overlap_new_lower_x_range(self, dataset):
        return dataset._concat_overlap_new_higher_x_range(self)

    def _create_overlap(self, x_max, x_min):

        lower_x = self.x[self.x < x_min]
        higher_x = self.x[self.x > x_max]

        left = self[:len(lower_x)]
        right = self[len(self) - len(higher_x):]

        overlap = self[len(lower_x):len(self) - len(higher_x)]

        return left, overlap, right

    def concatenate(self, dataset, factor=None):

        if isinstance(dataset, BaseOneDDataSet):
            x_max_orig = np.max(self.x)
            x_min_orig = np.min(self.x)

            x_max_new = np.max(dataset.x)
            x_min_new = np.min(dataset.x)

            if type(factor) == type(None):
                concat_func = self._find_concat(x_max_orig, x_min_orig, x_max_new, x_min_new)

                self._header += "#\n# Concatenated {} to {}\n".format(dataset.name, self.name)
                result = concat_func(dataset)
                return result
            elif isinstance(factor, Number):
                concat_func = self._find_concat(x_max_orig, x_min_orig, x_max_new, x_min_new)

                self._header += "#\n# Concatenated {} to {}\n".format(dataset.name, self.name)
                result = concat_func(dataset)
                return result
            else:
                raise TypeError("Factor needs to be a number.")

        else:
            raise TypeError("Concatenate only works among two BaseOneDDatasets.")

    def __getitem__(self, sliced):
        result = BaseOneDDataSet(self.x[sliced], self.y[sliced],
                                 name="{}".format(self.name),
                                 header="#Element {} of {}".format(sliced, self.name),
                                 error=self.error[sliced])
        return result

    def __len__(self):
        return len(self.x)

    def __mul__(self, value):
        if isinstance(value, Number):
            new_header = self._header + "#Arithmetic operation multiplication: {}*{}\n".format(self.name, value)
            new_y = np.multiply(self.y, value)
            new_error = np.multiply(self.error, value)
            return BaseOneDDataSet(np.array(self.x), new_y, error=new_error, name=self.name, header=new_header)
        else:
            raise ValueError('Only numbers are possible.')

    def __truediv__(self, value):
        if isinstance(value, Number):
            new_header = self._header + "#Arithmetic operation division: {}\\{}\n".format(self.name, value)
            new_y = np.divide(self.y, value)
            new_error = np.divide(self.error, value)
            return BaseOneDDataSet(np.array(self.x), new_y, error=new_error, name=self.name, header=new_header)
        elif isinstance(value, type(np.array([]))) and len(value) == len(self.y):
            new_header = self._header + "#Arithmetic operation division: {}\\{}\n".format(self.name, value)
            new_y = np.divide(self.y, value)
            new_error = np.divide(self.error, value)
            return BaseOneDDataSet(np.array(self.x), new_y, error=new_error, name=self.name, header=new_header)
        else:
            raise ValueError('Only numbers and np.arrays of same length are possible.')

    def spline(self, x1, y1, e1, x2, y2, e2):

        x_min = max(min(x1), min(x2))
        x_max = min(max(x1), max(x2))

        y1_new = np.where(x1 >= x_min, y1, None)
        y1_new = np.where(x1 <= x_max, y1_new, None)
        y1_new = y1_new[y1_new != None]
        e1_new = e1[x1 >= x_min]
        x1_new = x1[x1 >= x_min]
        e1_new = e1_new[x1_new <= x_max]
        x1_new = x1_new[x1_new <= x_max]

        y_spline = []

        x_spline, y_spline, e_spline = spline_data(x1_new, [x2, y2, e2])

        return x_spline, y1_new, y_spline, e1_new, e_spline

    def make_linear(self, x_min=(-1) * np.inf, x_max=np.inf):
        min_limit = x_min if x_min > min(self.x) else min(self.x)
        max_limit = x_max if x_max < max(self.x) else max(self.x)

        y0 = self.y[self.x < min_limit]
        y1 = self.y[self.x > min_limit]
        x1 = self.x[self.x > min_limit]
        y1 = y1[x1 < max_limit]
        x1 = x1[x1 < max_limit]
        y2 = self.y[self.x > max_limit]
        x0 = self.x[self.x < min_limit]
        x2 = self.x[self.x > max_limit]

        m_0 = y1[-1] - y1[0]
        b_0 = y1[0] - m_0 * x1[0]
        p_0 = [m_0, b_0]
        p_best, cov = curve_fit(linear_function, x1, y1, p0=p_0)
        y1 = linear_function(x1, *p_best)

        self.x = np.array(list(x0) + list(x1) + list(x2))
        self.y = np.array(list(y0) + list(y1) + list(y2))

    def make_horizontal(self, value, x_min=(-1) * np.inf, x_max=np.inf):
        min_limit = x_min if x_min > min(self.x) else min(self.x)
        max_limit = x_max if x_max < max(self.x) else max(self.x)

        y0 = self.y[self.x < min_limit]
        y1 = self.y[self.x > min_limit]
        x1 = self.x[self.x > min_limit]
        y1 = y1[x1 < max_limit]
        x1 = x1[x1 < max_limit]
        y2 = self.y[self.x > max_limit]
        x0 = self.x[self.x < min_limit]
        x2 = self.x[self.x > max_limit]

        y1 = [value for i in y1]

        self.x = np.array(list(x0) + list(x1) + list(x2))
        self.y = np.array(list(y0) + list(y1) + list(y2))

    def interpolate(self, x_min=(-1) * np.inf, x_max=np.inf):
        min_limit = x_min if x_min > min(self.x) else min(self.x)
        max_limit = x_max if x_max < max(self.x) else max(self.x)

        y0 = self.y[self.x < min_limit]
        y1 = self.y[self.x > min_limit]
        x1 = self.x[self.x > min_limit]
        y1 = y1[x1 < max_limit]
        x1 = x1[x1 < max_limit]
        y2 = self.y[self.x > max_limit]
        x0 = self.x[self.x < min_limit]
        x2 = self.x[self.x > max_limit]

        m0 = (y1[-1] - y1[0]) / (x1[-1] - x1[0])
        b0 = 0.5 * (y1[-1] + y1[0] - m0 * (x1[-1] + x1[0]))
        p0 = [m0, b0]

        p_opt, pcov = curve_fit(linear_function, x1, y1, p0)
        y_opt = linear_function(x1, *p_opt)
        self.x = np.array(list(x0) + list(x1) + list(x2))
        self.y = np.array(list(y0) + list(y_opt) + list(y2))

    def __sub__(self, secondDataset):
        if issubclass(type(secondDataset), BaseOneDDataSet):
            new_header = self._header + "#Arithmetic operation subtraction: {}-{}\n".format(self.name,
                                                                                            secondDataset.name)
            x1 = np.array(self.x)
            y1 = np.array(self.y)
            e1 = np.array(self.error)

            x2 = np.array(secondDataset.x)
            y2 = np.array(secondDataset.y)
            e2 = np.array(secondDataset.error)

            xspline, y3, y4, e3, e4 = self.spline(x1, y1, e1, x2, y2, e2)
            new_y = np.subtract(y3, y4)
            new_e = np.sqrt(np.power(e3, 2) + np.power(e4, 2))
            new_x = xspline

        elif isinstance(secondDataset, Number):
            new_header = self._header + "#Arithmetic operation subtraction: {}-{}\n".format(self.name, secondDataset)
            new_y = np.subtract(self.y, secondDataset)
            new_x = np.array(self.x)
            new_e = np.array(self.e)
        else:
            raise ValueError('Subtraction only defined for numbers and other 1D-Datasets')
        return BaseOneDDataSet(new_x, new_y, error=new_e, name=self.name, header=new_header)

    def __add__(self, secondDataset):
        if issubclass(type(secondDataset), BaseOneDDataSet):
            new_header = self._header + "#Arithmetic operation subtraction: {}-{}\n".format(self.name,
                                                                                            secondDataset.name)
            x1 = np.array(self.x)
            y1 = np.array(self.y)
            e1 = np.array(self.error)

            x2 = np.array(secondDataset.x)
            y2 = np.array(secondDataset.y)
            e2 = np.array(secondDataset.error)

            xspline, y3, y4, e3, e4 = self.spline(x1, y1, e1, x2, y2, e2)

            new_y = np.add(y3, y4)
            new_e = np.sqrt(np.power(e3, 2) + np.power(e4, 2))
            new_x = xspline

        elif isinstance(secondDataset, Number):
            new_header = self._header + "#Arithmetic operation subtraction: {}-{}\n".format(self.name, secondDataset)
            new_y = np.add(self.y, secondDataset)
            new_x = np.array(self.x)
            new_e = np.array(self.e)
        else:
            raise ValueError('Subtraction only defined for numbers and other 1D-Datasets')
        return BaseOneDDataSet(new_x, new_y, error=new_e, name=self.name, header=new_header)

    def __init__(self, x=[0], y=[0], name='', header='', error=None):
        self.x = x
        self.y = y
        if type(error) == type(None):
            self.error = np.sqrt(y)
        else:
            if len(error) == len(x):
                self.error = error
            else:
                self.error = np.sqrt(y)
        self._header = header
        self.name = name

    def from_file(self,filename):
        if not isfile(filename):
            raise FileExistsError(f"File {filename} does not exist.")
        name = list(list(filename.split("/"))[-1].split("."))[0]
        xs = []
        ys = []
        es = []
        with open(filename, "r") as infile:
            for line in infile:
                if not line.startswith("#"):
                    data = list(line.strip().split())
                    try:
                        x = float(data[0])
                        y = float(data[1])
                        e = np.sqrt(y)
                        if len(data>2):
                            e = float(data[2])
                        xs.append(x)
                        ys.append(y)
                        es.append(e)
                    except:
                        pass
        header = f"#{datetime.datetime.now()}\n"
        header += f"#Data loaded from {filename}\n"
        return type(self)(xs,ys,name=name,header=header,error=es)


class SAXSData(BaseOneDDataSet):
    pass

class SANSData(BaseOneDDataSet):
    pass

class PCSData(BaseOneDDataSet):
    pass